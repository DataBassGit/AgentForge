from typing import Dict, Optional, Any, List
from agentforge.utils.logger import Logger
from agentforge.config import Config
from agentforge.config_structs import CogConfig
from agentforge.storage.memory import Memory
from agentforge.utils.parsing_processor import ParsingProcessor


class MemoryManager:
    """
    Manages memory nodes for a Cog, handling memory resolution, querying, and updating.
    Mirrors the AgentRegistry pattern for memory-specific concerns.
    """

    def __init__(self, cog_config: CogConfig, cog_name: str):
        """
        Initialize the MemoryManager with cog configuration and name.
        
        Args:
            cog_config: The structured cog configuration
            cog_name: The name of the cog
        """
        self.logger = Logger(cog_name, "mem_mgr")
        self.cog_config = cog_config
        self.cog_name = cog_name
        self.config = Config()  # singleton for resolve_class / persona helpers

        # Resolve persona using existing precedence (Cog > Agent > default)
        persona_data = self.config.resolve_persona(
            cog_config={"cog": {"persona": self.cog_config.cog.persona}}
        )
        self.persona = persona_data.get("name") if persona_data else None

        # Build memory nodes
        self.memories = self._build_memory_nodes()

    # -----------------------------------------------------------------
    # Public hooks
    # -----------------------------------------------------------------
    
    def query_before(self, agent_id: str, context: dict, state: dict) -> None:
        """
        Query memory nodes configured to run before the specified agent.
        
        Args:
            agent_id: The agent ID about to be executed
            context: External context data
            state: Internal state data
        """
        self.logger.log(f"Querying memory nodes before agent: {agent_id}", "debug", "Memory")
        
        for mem_id, mem_data in self.memories.items():
            cfg = mem_data["config"]
            mem_obj = mem_data["instance"]

            # Check if this memory should be queried before this agent
            query_agents = cfg.query_before
            if isinstance(query_agents, str):
                query_agents = [query_agents]
                
            if agent_id not in query_agents:
                continue
                
            self.logger.log(f"Querying memory {mem_id} before agent {agent_id}", "debug", "Memory")
            
            # Handle query keys - if empty or missing, use both context and state
            query_keys = cfg.query_keys
            if not query_keys:
                # Use merged context and state as query text
                query_text = {**context, **state}
                if query_text:
                    self.logger.log(f"Using merged context/state for memory {mem_id} query", "debug", "Memory")
                    result = mem_obj.query_memory(query_text=query_text)
                    if result:
                        self.logger.log(f"Found memories in {mem_id}", "debug", "Memory")
                        mem_obj.store.update(result)
                else:
                    self.logger.log(f"No context or state available for memory {mem_id} query", "debug", "Memory")
                continue
                
            try:
                input_for_query = self._extract_keys(query_keys, context, state)
                if not input_for_query:
                    self.logger.log(f"No query data extracted for memory {mem_id}", "debug", "Memory")
                    continue
                
                # Prepare query text from extracted values
                if len(input_for_query) == 1:
                    query_text = next(iter(input_for_query.values()))
                else:
                    query_text = list(input_for_query.values())

                self.logger.log(f"Querying memory {mem_id} with: {query_text}", "debug", "Memory")
                
                # Execute query - empty result is normal
                result = mem_obj.query_memory(query_text=query_text)
                if result:
                    self.logger.log(f"Found memories in {mem_id}", "debug", "Memory")
                    mem_obj.store.update(result)
                    
            except Exception as e:
                # Storage-level errors should be fatal
                self.logger.log(f"Memory query failed for {mem_id}: {e}", "error", "Memory")
                raise

    def update_after(self, agent_id: str, context: dict, state: dict) -> None:
        """
        Update memory nodes configured to run after the specified agent.
        
        Args:
            agent_id: The agent ID that just completed execution
            context: External context data
            state: Internal state data
        """
        self.logger.log(f"Updating memory nodes after agent: {agent_id}", "debug", "Memory")
        
        for mem_id, mem_data in self.memories.items():
            cfg = mem_data["config"]
            mem_obj = mem_data["instance"]
            
            # Check if this memory should be updated after this agent
            update_agents = cfg.update_after
            if isinstance(update_agents, str):
                update_agents = [update_agents]
                
            if agent_id not in update_agents:
                continue
                
            self.logger.log(f"Updating memory {mem_id} after agent {agent_id}", "debug", "Memory")
            
            # Handle update keys - if empty or missing, use both context and state
            update_keys = cfg.update_keys
            if not update_keys:
                # Use merged context and state for update
                update_data = {**context, **state}
                if update_data:
                    self.logger.log(f"Using merged context/state for memory {mem_id} update", "debug", "Memory")
                    mem_obj.update_memory(data=update_data, context={**context, **state})
                    self.logger.log(f"Successfully updated memory {mem_id}", "debug", "Memory")
                else:
                    self.logger.log(f"No context or state available for memory {mem_id} update", "debug", "Memory")
                continue
                
            try:
                update_data = self._extract_keys(update_keys, context, state)
                if not update_data:
                    self.logger.log(f"No update data extracted for memory {mem_id}", "debug", "Memory")
                    continue
                
                self.logger.log(f"Updating memory {mem_id} with: {list(update_data.keys())}", "debug", "Memory")
                
                # Update memory with extracted data and merged context/state for metadata
                mem_obj.update_memory(data=update_data, context={**context, **state})
                self.logger.log(f"Successfully updated memory {mem_id}", "debug", "Memory")
                
            except Exception as e:
                # Storage-level errors should be fatal
                self.logger.log(f"Memory update failed for {mem_id}: {e}", "error", "Memory")
                raise

    def build_mem(self) -> Dict[str, Any]:
        """
        Return {mem_id: mem_instance.store} for agent.run(_mem=...).
        
        Returns:
            Dict mapping memory IDs to their storage instances
        """
        return {mid: m["instance"].store for mid, m in self.memories.items()}

    # -----------------------------------------------------------------
    # Internal helpers (moved from Cog)
    # -----------------------------------------------------------------
    
    def _build_memory_nodes(self) -> Dict[str, Any]:
        """
        Build memory nodes from the cog configuration.
        
        Returns:
            Dict mapping memory IDs to memory node data
        """
        memories = {}
        memory_list = self.cog_config.cog.memory
        
        for mem_def in memory_list:
            mem_id = mem_def.id
            mem_class = self._resolve_memory_class(mem_def)
            
            # Create a unique collection ID that's independent of the cog/persona namespacing
            collection_id = mem_def.collection_id or mem_id

            # Pass cog_name and resolved persona to the Memory constructor
            mem_obj = mem_class(cog_name=self.cog_name, persona=self.persona, collection_id=collection_id)
            memories[mem_id] = {
                "instance": mem_obj,
                "config": mem_def,  # store the structured config for query/update triggers
            }
        
        return memories

    @staticmethod
    def _resolve_memory_class(mem_def) -> type:
        """
        Resolve and return the memory class for a given memory definition.
        
        Args:
            mem_def: Memory definition from configuration
            
        Returns:
            The resolved memory class
        """
        return Config.resolve_class(
            mem_def.type,
            default_class=Memory,
            context=f"memory '{mem_def.id}'"
        )

    @staticmethod
    def _extract_keys(key_list: Optional[List[str]], context: dict, state: dict) -> dict:
        """
        Extract values for the given keys from context (external) first, then state (internal).
        Supports dot-notated keys for nested dict access.
        If key_list is empty or None, returns a merged dict of context and state.
        
        Args:
            key_list: List of keys to extract
            context: External context data
            state: Internal state data
            
        Returns:
            Dict of extracted key-value pairs
            
        Raises:
            ValueError: If a key is not found in either context or state
        """
        if not key_list:
            merged = {**state, **context}
            return merged
        result = {}
        for key in key_list:
            value = ParsingProcessor.get_dot_notated(context, key)
            if value is not None:
                result[key] = value
                continue
            value = ParsingProcessor.get_dot_notated(state, key)
            if value is not None:
                result[key] = value
                continue
            raise ValueError(f"Key '{key}' not found in context or state.")
        return result 