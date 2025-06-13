from typing import Dict, Any, List, Type
from agentforge.utils.logger import Logger
from agentforge.config import Config
from agentforge.config_structs import CogConfig
from agentforge.storage.memory import Memory
from agentforge.storage.chat_history_memory import ChatHistoryMemory


class MemoryManager:
    """
    Manages memory nodes for a Cog, handling memory resolution, querying, and updating.
    Mirrors the AgentRegistry pattern for memory-specific concerns.
    """

    def __init__(self, cog_config: CogConfig, cog_name: str) -> None:
        """
        Initialize the MemoryManager with cog configuration and name.
        Orchestrates logger, config, persona, memory node, and agent-memory map setup.
        """
        self.cog_config = cog_config
        self.cog_name = cog_name
        self.logger = Logger(self.cog_name, "mem_mgr")
        self.config = Config() 
        self._resolve_persona()
        self._initialize_memory_nodes()
        self._initialize_agent_memory_maps()
        
        self.logger.debug(f"Initialized MemoryManager for cog='{self.cog_name}', persona='{self.persona}' with {len(self.memory_nodes)} memory nodes.")

    def _resolve_persona(self) -> None:
        """
        Resolve persona using precedence: Cog > Agent > default.
        """
        persona_data = self.config.resolve_persona(
            cog_config={"cog": {"persona": self.cog_config.cog.persona}}
        )
        self.persona = persona_data.get("name") if persona_data else None

    def _initialize_memory_nodes(self) -> None:
        """
        Build memory nodes from the cog configuration and add chat history node if enabled.
        """
        self.memory_nodes = self._build_memory_nodes()
        self._initialize_chat_memory()
        
    def _initialize_chat_memory(self) -> None:
        """
        Initialize the chat history memory node if enabled.
        """
        # Use the dataclass field for chat_memory_enabled (default True if None)
        chat_enabled = self.cog_config.cog.chat_memory_enabled
        self._chat_memory_enabled = chat_enabled if chat_enabled is not None else True

        if not self._chat_memory_enabled:
            return
        
        max_results = self.cog_config.cog.chat_history_max_results
        self._chat_history_max_results = max_results if max_results is not None and max_results >= 0 else 20

        # Pull chat_history_max_retrieval from cog config, defaulting to 20 if missing or negative
        max_retrieval = getattr(self.cog_config.cog, "chat_history_max_retrieval", None)
        self._chat_history_max_retrieval = max_retrieval if max_retrieval is not None and max_retrieval >= 0 else 20

        self.memory_nodes["chat_history"] = {
            "instance": ChatHistoryMemory(self.cog_name, self.persona),
            "config": None,
        }

    def _initialize_agent_memory_maps(self) -> None:
        """
        Build agent-to-memory node maps for query and update triggers.
        """
        self.query_before_map = self._map_agents_to_memory_nodes(trigger="query_before")
        self.update_after_map = self._map_agents_to_memory_nodes(trigger="update_after")

    # -----------------------------------------------------------------
    # Public Interface Methods
    # -----------------------------------------------------------------

    def query_before(self, agent_id: str, _ctx: dict, _state: dict) -> None:
        """
        Query memory nodes configured to run before the specified agent.
        Calls _query_memory_node for each relevant node.
        """
        self.logger.info(f"Querying memory nodes before agent: {agent_id}")
        queried = 0
        results_found = 0
        for mem_id in self.query_before_map.get(agent_id, []):
            if self._query_memory_node(mem_id, agent_id, _ctx, _state):
                results_found += 1
            queried += 1
        self.logger.info(f"Queried {queried} memory node(s) before agent '{agent_id}'; {results_found} returned results.")

    def update_after(self, agent_id: str, _ctx: dict, _state: dict) -> None:
        """
        Update memory nodes configured to run after the specified agent.
        Calls _update_memory_node for each relevant node.
        """
        self.logger.info(f"Updating memory nodes after agent: {agent_id}")
        updated = 0
        for mem_id in self.update_after_map.get(agent_id, []):
            self._update_memory_node(mem_id, agent_id, _ctx, _state)
            updated += 1
        self.logger.info(f"Updated {updated} memory node(s) after agent '{agent_id}'.")

    def build_mem(self) -> Dict[str, Any]:
        """
        Return a mapping of memory node IDs to their current store for agent execution context.
        Extension point: override to customize memory context building.
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
            mem_obj = self._create_memory_node(mem_def)
            memories[mem_id] = {
                "instance": mem_obj,
                "config": mem_def,
            }
        self.logger.debug(f"Built {len(memories)} memory node(s) from configuration.")
        return memories

    def _create_memory_node(self, mem_def: Any) -> Memory:
        """
        Instantiate a single memory node from its definition.
        Extension point: override to customize memory node instantiation.
        """
        mem_class = self._get_memory_node_class(mem_def)
        collection_id = mem_def.collection_id or mem_def.id
        return mem_class(cog_name=self.cog_name, persona=self.persona, collection_id=collection_id)

    def _get_memory_node_class(self, mem_def: Any) -> Type[Memory]:
        """
        Resolve and return the memory class for a given memory definition.
        Extension point: override to customize class resolution.
        """
        return Config.resolve_class(
            mem_def.type,
            default_class=Memory,
            context=f"memory '{mem_def.id}'"
        )

    def _map_agents_to_memory_nodes(self, trigger: str) -> Dict[str, List[str]]:
        """
        Build a mapping from agent_id to memory node IDs for a given trigger ("query_before" or "update_after").
        Calls _get_agents_for_trigger and _add_agent_to_map for each node.
        Returns:
            Dict[str, List[str]]: Mapping of agent IDs to lists of memory node IDs.
        """
        agent_map: Dict[str, List[str]] = {}
        for mem_id, mem_data in self.memory_nodes.items():
            agents = self._get_agents_for_trigger(mem_data["config"], trigger)
            if not agents:
                continue
            for agent_id in agents:
                self._add_agent_to_map(agent_map, agent_id, mem_id)
        self.logger.debug(f"Built agent-to-memory map for trigger '{trigger}' with {len(agent_map)} entries.")
        return agent_map

    def _get_agents_for_trigger(self, mem_config: Any, trigger: str) -> List[str]:
        """
        Extract agent IDs for a given trigger from a memory node config.
        """
        agents = getattr(mem_config, trigger, None)
        if not agents:
            return []
        if isinstance(agents, str):
            return [agents]
        return list(agents)

    def _add_agent_to_map(self, agent_map: Dict[str, List[str]], agent_id: str, mem_id: str) -> None:
        """
        Add a memory node to the agent map for a given agent.
        """
        if agent_id not in agent_map:
            agent_map[agent_id] = []
        agent_map[agent_id].append(mem_id)

    def _query_memory_node(self, mem_id: str, agent_id: str, _ctx: dict, _state: dict) -> bool:
        """
        Query a single memory node before agent execution.
        Extension point: override to customize query logic.
        Returns True if the memory node's store is non-empty.
        """
        mem_data = self.memory_nodes[mem_id]
        cfg = mem_data["config"]
        mem_obj = mem_data["instance"]
        self.logger.debug(f"Querying memory '{mem_id}' before agent '{agent_id}'")
        mem_obj.query_memory(cfg.query_keys, _ctx, _state)
        return bool(mem_obj.store)

    def _update_memory_node(self, mem_id: str, agent_id: str, _ctx: dict, _state: dict) -> None:
        """
        Update a single memory node after agent execution.
        Extension point: override to customize update logic.
        """
        mem_data = self.memory_nodes[mem_id]
        cfg = mem_data["config"]
        mem_obj = mem_data["instance"]
        self.logger.debug(f"Updating memory '{mem_id}' after agent '{agent_id}'")
        mem_obj.update_memory(cfg.update_keys, _ctx, _state) 

    # -----------------------------------------------------------------
    # Chat History Methods
    # -----------------------------------------------------------------

    def record_chat(self, _ctx, output):
        """
        Record a chat turn in the chat history memory node, if enabled.
        """
        if not self._chat_memory_enabled:
            return
        
        chat_node = self.memory_nodes.get("chat_history").get("instance")
        chat_node.update_memory(_ctx, output)

    def load_chat(self, _ctx: dict = None, _state: dict = None):
        """
        Query the chat history node and load the most recent N messages into its store.
        N is determined by chat_history_max_results in the cog config (default 10, 0 means no limit).
        """
        if not self._chat_memory_enabled or "chat_history" not in self.memory_nodes:
            return
      
        chat_node = self.memory_nodes["chat_history"]["instance"]
        chat_node.query_memory(
            num_results=self._chat_history_max_results,
            max_retrieval=self._chat_history_max_retrieval,
            _ctx=_ctx or {},
            _state=_state or {},
        )