from typing import Dict, Optional, Any, List, Type
from agentforge.utils.logger import Logger
from agentforge.config import Config
from agentforge.config_structs import CogConfig
from agentforge.storage.memory import Memory


class MemoryManager:
    """
    Manages memory nodes for a Cog, handling memory resolution, querying, and updating.
    Mirrors the AgentRegistry pattern for memory-specific concerns.
    """

    def __init__(self, cog_config: CogConfig, cog_name: str) -> None:
        """
        Initialize the MemoryManager with cog configuration and name.

        Args:
            cog_config (CogConfig): The structured cog configuration.
            cog_name (str): The name of the cog.
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

        # Build memory nodes and agent-to-memory maps
        self.memory_nodes = self._build_memory_nodes()
        self.query_before_map = self._map_agents_to_memory_nodes(trigger="query_before")
        self.update_after_map = self._map_agents_to_memory_nodes(trigger="update_after")
        self.logger.debug(f"Initialized MemoryManager for cog='{self.cog_name}', persona='{self.persona}' with {len(self.memory_nodes)} memory nodes.")

    # -----------------------------------------------------------------
    # Public Interface Methods
    # -----------------------------------------------------------------

    def query_before(self, agent_id: str, _ctx: dict, _state: dict) -> None:
        """
        Query memory nodes configured to run before the specified agent.

        Args:
            agent_id (str): The agent ID about to be executed.
            _ctx (dict): External context data.
            _state (dict): Internal state data.
        Raises:
            Exception: If a memory query fails fatally.
        """
        self.logger.info(f"Querying memory nodes before agent: {agent_id}")
        queried = 0
        results_found = 0
        for mem_id in self.query_before_map.get(agent_id, []):
            mem_data = self.memory_nodes[mem_id]
            cfg = mem_data["config"]
            mem_obj = mem_data["instance"]

            self.logger.debug(f"Querying memory '{mem_id}' before agent '{agent_id}'")
            mem_obj.query_memory(cfg.query_keys, _ctx, _state)
            if mem_obj.store:
                results_found += 1
            queried += 1
            
        self.logger.info(f"Queried {queried} memory node(s) before agent '{agent_id}'; {results_found} returned results.")

    def update_after(self, agent_id: str, _ctx: dict, _state: dict) -> None:
        """
        Update memory nodes configured to run after the specified agent.

        Args:
            agent_id (str): The agent ID that just completed execution.
            _ctx (dict): External context data.
            _state (dict): Internal state data.
        Raises:
            Exception: If a memory update fails fatally.
        """
        self.logger.info(f"Updating memory nodes after agent: {agent_id}")
        updated = 0
        for mem_id in self.update_after_map.get(agent_id, []):
            mem_data = self.memory_nodes[mem_id]
            cfg = mem_data["config"]
            mem_obj = mem_data["instance"]
            self.logger.debug(f"Updating memory '{mem_id}' after agent '{agent_id}'")
            
            mem_obj.update_memory(cfg.update_keys, _ctx, _state)
            updated += 1
            
        self.logger.info(f"Updated {updated} memory node(s) after agent '{agent_id}'.")

    def build_mem(self) -> Dict[str, Any]:
        """
        Return a mapping of memory node IDs to their current store for agent execution context.

        Returns:
            Dict[str, Any]: Mapping of memory node IDs to their store dicts.
        """
        self.logger.debug("Building memory context for agent execution.")
        return {mid: m["instance"].store for mid, m in self.memory_nodes.items()}

    # -----------------------------------------------------------------
    # Internal Helper Methods
    # -----------------------------------------------------------------

    def _build_memory_nodes(self) -> Dict[str, Any]:
        """
        Build memory nodes from the cog configuration.

        Returns:
            Dict[str, Any]: Mapping of memory node IDs to their instance/config dicts.
        """
        memories = {}
        memory_list = self.cog_config.cog.memory
        for mem_def in memory_list:
            mem_id = mem_def.id
            mem_class = self._resolve_memory_node_class(mem_def)
            collection_id = mem_def.collection_id or mem_id
            mem_obj = mem_class(cog_name=self.cog_name, persona=self.persona, collection_id=collection_id)
            memories[mem_id] = {
                "instance": mem_obj,
                "config": mem_def,
            }
        self.logger.debug(f"Built {len(memories)} memory node(s) from configuration.")
        return memories

    def _map_agents_to_memory_nodes(self, trigger: str) -> Dict[str, List[str]]:
        """
        Build a mapping from agent_id to memory node IDs for a given trigger ("query_before" or "update_after").

        Args:
            trigger (str): The trigger attribute to use ("query_before" or "update_after").
        Returns:
            Dict[str, List[str]]: Mapping of agent IDs to lists of memory node IDs.
        """
        agent_map: Dict[str, List[str]] = {}
        for mem_id, mem_data in self.memory_nodes.items():
            agents = getattr(mem_data["config"], trigger, None)
            if not agents:
                continue
            if isinstance(agents, str):
                agents = [agents]
            for agent_id in agents:
                if agent_id not in agent_map:
                    agent_map[agent_id] = []
                agent_map[agent_id].append(mem_id)
        self.logger.debug(f"Built agent-to-memory map for trigger '{trigger}' with {len(agent_map)} entries.")
        return agent_map

    @staticmethod
    def _resolve_memory_node_class(mem_def: Any) -> Type[Memory]:
        """
        Resolve and return the memory class for a given memory definition.

        Args:
            mem_def (Any): Memory definition from configuration.
        Returns:
            Type[Memory]: The resolved memory class.
        Raises:
            Exception: If class resolution fails.
        """
        return Config.resolve_class(
            mem_def.type,
            default_class=Memory,
            context=f"memory '{mem_def.id}'"
        ) 