import sys
import importlib
import importlib.util
from typing import Dict, Any, Optional
from agentforge.config import Config
from agentforge.agent import Agent


class Cog:
    """
    A cognitive architecture engine that orchestrates agents as defined in a YAML configuration.
    """

    ##########################################################
    # Section 1: Initialization & Configuration Loading
    ##########################################################

    def __init__(self, cog_file: str, enable_trail_logging: bool = True):
        # Set Config and Root Path
        self.config = Config()
        self._module_cache: Dict[str, Any] = {}  # cache for imported modules

        # Set instance variables
        self.cog_file = cog_file
        self.global_context: Dict[str, Any] = {}
        self.thought_flow_trail = [] if enable_trail_logging else None

        # Load and validate configuration
        self._load_cog_config()
        self._validate_config()

        # Set up Cog (build agent nodes)
        self._build_agent_nodes()

    def _load_cog_config(self) -> None:
        self.cog_config = self.config.load_cog_data(self.cog_file).copy()

    ##########################################################
    # Section 2: Validation Methods
    ##########################################################

    def _validate_config(self) -> None:
        """Validate the overall cog configuration."""
        self._validate_cog_config()
        self._validate_agent_config()
        self._validate_flow_config()

    def _validate_cog_config(self) -> None:
        cog = self.cog_config.get("cog")
        if not cog or not isinstance(cog, dict):
            raise ValueError(f"Cog file `{self.cog_file}` must have a `cog` dictionary defined.")

    def _validate_agent_config(self) -> None:
        self.agent_list = self.cog_config.get("cog").get("agents")
        if not self.agent_list or not isinstance(self.agent_list, list):
            raise ValueError(f"Cog file `{self.cog_file}` must have an `agents` list defined.")
        self._validate_agents()

    def _validate_agents(self) -> None:
        """Validate each agent definition."""
        for agent in self.agent_list:
            if not isinstance(agent, dict):
                raise ValueError("Each agent definition must be a dictionary.")

            agent_id = agent.get("id")
            if not agent_id:
                raise ValueError("Every agent must have an 'id'.")

            if "type" not in agent and "template_file" not in agent:
                raise ValueError(f"Agent '{agent_id}' must have at least a 'type' or a 'template_file' defined.")

            if "type" in agent:
                self._validate_module_exists(agent["type"], agent_id)

    def _validate_flow_config(self) -> None:
        self.flow = self.cog_config.get("cog").get("flow")
        if not self.flow or not isinstance(self.flow, dict):
            raise ValueError(f"Cog file `{self.cog_file}` must have a `flow` dictionary defined.")
        self._validate_flow()

    def _validate_flow(self) -> None:
        if "start" not in self.flow:
            raise ValueError("Flow must have a 'start' key.")
        if "transitions" not in self.flow:
            raise ValueError("Flow must have a 'transitions' dictionary defined.")
        if not isinstance(self.flow["transitions"], dict):
            raise ValueError("Flow 'transitions' must be a dictionary.")

    def _validate_module_exists(self, full_class_path: str, agent_id: str) -> None:
        """
        Validate that the module exists and contains the specified class.
        Uses the module cache to avoid duplicate imports.
        """
        parts = full_class_path.split(".")
        if len(parts) < 2:
            raise ValueError(
                f"Agent '{agent_id}' has an invalid type format: '{full_class_path}'. "
                "It must be a fully qualified import path."
            )
        module_path = ".".join(parts[:-1])
        class_name = parts[-1]
        spec = importlib.util.find_spec(module_path)
        if spec is None:
            raise ImportError(
                f"Module '{module_path}' for agent '{agent_id}' not found in the project root."
            )
        module = self._get_module(module_path)
        if not hasattr(module, class_name):
            raise ImportError(
                f"Class '{class_name}' not found in module '{module_path}' for agent '{agent_id}'."
            )

    ##########################################################
    # Section 3: Module Resolution
    ##########################################################

    def _get_module(self, module_path: str):
        """
        Return the module object from cache if available; otherwise, import and cache it.
        """
        if module_path in self._module_cache:
            return self._module_cache[module_path]
        module = importlib.import_module(module_path)
        self._module_cache[module_path] = module
        return module

    def _resolve_agent_class(self, agent_def: Dict[str, Any]) -> type:
        """
        Resolve and return the agent class for a given agent definition.
        Assumes validation has already been performed.
        """
        if "type" not in agent_def:
            return Agent

        parts = agent_def["type"].split(".")
        module_path = ".".join(parts[:-1])
        class_name = parts[-1]
        module = self._get_module(module_path)
        return getattr(module, class_name)

    ##########################################################
    # Section 4: Node Resolution
    ##########################################################

    def _build_agent_nodes(self) -> None:
        """Instantiate all agents defined in the cog configuration."""
        self.agents = {}
        for agent_def in self.agent_list:
            agent_id = agent_def.get("id")
            agent_class = self._resolve_agent_class(agent_def)
            agent_prompt_file = agent_def.get("template_file", agent_class.__name__)
            self.agents[agent_id] = agent_class(agent_prompt_file)

    def get_next_agent(self, current_agent_id: str) -> Optional[str]:
        """
        Determine the next agent (node) ID based on the current node's transition and global context.
        """
        transitions = self.flow.get("transitions", {})
        agent_transition = transitions.get(current_agent_id)
        if agent_transition is None:
            return None

        if isinstance(agent_transition, dict):
            if agent_transition.get("end", False):
                return None
            if "next" in agent_transition:
                return agent_transition["next"]
            # Assume that the first key not 'end' or 'next' is the decision variable name.
            decision_key = next(
                (k for k in agent_transition if k not in {"end", "next"}), None
            )
            if decision_key:
                decision_map = agent_transition[decision_key]
                decision_value = self.global_context[current_agent_id].get(decision_key)
                return decision_map.get(decision_value, decision_map.get("default"))
            return None
        return agent_transition

    ##########################################################
    # Section 5: Execution
    ##########################################################

    def _execute_flow(self) -> None:
        current_agent_id = self.flow.get("start")
        while current_agent_id:
            agent = self.agents.get(current_agent_id)
            output = agent.run(**self.global_context)
            if not output:
                return None
            self.global_context[current_agent_id] = output
            current_agent_id = self.get_next_agent(current_agent_id)

    def _track_thought_flow(self):
        if self.thought_flow_trail is not None:
            self.thought_flow_trail.append(self.global_context.copy())

    def run(self, **kwargs: Any) -> Optional[Dict[str, Any]]:
        """
        Execute the cog by iteratively running agents as defined in the flow.
        """
        self.global_context = {}
        self.global_context.update(kwargs)
        self._execute_flow()
        self._track_thought_flow()
        return self.global_context

