import importlib
import importlib.util
from typing import Dict, Any, Optional, List
from agentforge.config import Config
from agentforge.agent import Agent
from agentforge.utils.logger import Logger
from agentforge.utils.parsing_processor import ParsingProcessor, ParsingError


class Cog:
    """
    A cognitive architecture engine that orchestrates agents as defined in a YAML configuration.
    """

    ##########################################################
    # Section 1: Initialization & Configuration Loading
    ##########################################################

    def __init__(self, cog_file: str, enable_trail_logging: bool = True, log_file: Optional[str] = 'cog'):
        # Set instance variables
        self.cog_file = cog_file
        self.enable_trail_logging = enable_trail_logging
        self._module_cache: Dict[str, Any] = {}  # cache for imported modules
        self._reset_context_and_thoughts()

        # Set Config and Logger
        self.config = Config()
        self.logger: Logger = Logger(self.cog_file, log_file)

        # Load and validate configuration
        self._load_cog_config()
        self._validate_config()

        # Set up Cog (build agent nodes)
        self._build_agent_nodes()

    def _load_cog_config(self) -> None:
        self.cog_config = self.config.load_cog_data(self.cog_file).copy()

    def _reset_context_and_thoughts(self):
        self._reset_global_context()
        self._reset_thought_flow_trail()

    def _reset_global_context(self):
        self.global_context: Dict[str, Any] = {}

    def _reset_thought_flow_trail(self):
        self.thought_flow_trail: List[Dict] = []

    ##########################################################
    # Section 2: Interface Methods
    ##########################################################

    def get_track_flow_trail(self) -> []:
        return self.thought_flow_trail

    ##########################################################
    # Section 3: Validation Methods
    ##########################################################

    def _validate_config(self) -> None:
        """Validate the overall cog configuration."""
        self._validate_cog_config()
        self._validate_agent_config()
        self._validate_flow_config()
        self._validate_response_format()

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

    def _validate_response_format(self) -> None:
        # Check for a cog-level response_format; if not defined, we simply use None.
        self._parser = ParsingProcessor()
        self.default_response_format = self.cog_config.get("cog", {}).get("response_format", None)
        valid_options = set(self._parser.list_supported_formats() + ['auto', 'none'])
        if self.default_response_format and self.default_response_format.lower() not in valid_options:
            raise ValueError(
                f"Response format '{self.default_response_format}' is not valid. "
                f"Use one of: {', '.join(valid_options)}."
            )

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
    # Section 4: Module Resolution
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
    # Section 5: Node Resolution
    ##########################################################

    @staticmethod
    def _get_decision_key(transition: dict, reserved_keys: set) -> Optional[str]:
        """Extracts the decision key from the transition, excluding reserved keys."""
        return next((k for k in transition if k not in reserved_keys), None)

    @staticmethod
    def _is_end_transition(agent_transition: dict) -> bool:
        """Return True if the agent transition is marked as an end."""
        return agent_transition.get("end", False)

    def _build_agent_nodes(self) -> None:
        """Instantiate all agents defined in the cog configuration."""
        self.agents = {}
        self.agent_response_format = {}
        for agent_def in self.agent_list:
            agent_id = agent_def.get("id")
            agent_class = self._resolve_agent_class(agent_def)
            agent_prompt_file = agent_def.get("template_file", agent_class.__name__)
            self.agents[agent_id]= agent_class(agent_prompt_file)
            self.agent_response_format[agent_id] = self._get_response_format_for_agent(agent_def)

    def _check_max_visits(self, current_agent_id: str, transition: dict) -> Optional[str]:
        """
        Check if the max_visits limit for the given agent is exceeded.
        If it is exceeded, return the 'default' branch specified in the transition.
        Otherwise, return None.
        """
        max_visits = transition.get("max_visits")
        if max_visits is not None:
            if not hasattr(self, "agent_visit_counts"):
                self.agent_visit_counts = {}
            self.agent_visit_counts[current_agent_id] = self.agent_visit_counts.get(current_agent_id, 0) + 1
            if self.agent_visit_counts[current_agent_id] > max_visits:
                return transition.get("default")
        return None

    def _get_next_agent(self, current_agent_id: str) -> Optional[str]:
        """
        Determine the next agent (node) ID based on the current node's transition and global context.
        """
        transitions = self.flow.get("transitions", {})
        agent_transition = transitions.get(current_agent_id)
        if agent_transition is None:
            return None

        # If the transition is not a dictionary, it's a direct next agent.
        if not isinstance(agent_transition, dict):
            return agent_transition

        # Check if this transition indicates termination.
        if self._is_end_transition(agent_transition):
            return None

        # Otherwise, handle it as a decision-based transition.
        return self._handle_decision_transition(current_agent_id, agent_transition)

    def _handle_decision(self, current_agent_id: str, transition: dict) -> Optional[str]:
        """
        Handles decision-based transitions by determining the decision key
        and selecting the appropriate branch based on the agent's output.
        """
        reserved_keys = {"end", "max_visits"}
        decision_key = self._get_decision_key(transition, reserved_keys)
        if decision_key:
            decision_map = transition[decision_key]
            decision_value = self.global_context[current_agent_id].get(decision_key)
            return decision_map.get(decision_value, decision_map.get("default"))
        return None

    def _handle_decision_transition(self, current_agent_id: str, transition: dict) -> Optional[str]:
        """
        Handle decision-based transitions:
          - Check if the max_visits limit for this agent is exceeded.
          - Otherwise, use the decision variable to select the next agent.
        """
        default_branch = self._check_max_visits(current_agent_id, transition)
        if default_branch is not None:
            return default_branch

        return self._handle_decision(current_agent_id, transition)

    ##########################################################
    # Section 6: Execution
    ##########################################################

    def _get_response_format_for_agent(self, agent_def):
        response_format = agent_def.get("response_format", self.default_response_format).lower()
        if response_format == "none" or not response_format:
            return None

        return response_format

    def _call_agent(self, current_agent_id):
        attempts = 0
        max_attempts = 3
        agent = self.agents.get(current_agent_id)

        while attempts < max_attempts:
            attempts += 1
            raw_output = agent.run(**self.global_context)

            # If the agent returned no output, just retry (unless we've exceeded attempts)
            if not raw_output:
                self.logger.log(f"No output from agent '{current_agent_id}', retrying... (Attempt {attempts})",
                                'warning')
                continue

            # Try parsing the agent's output
            try:
                parsed_output = self._parse_agent_output(current_agent_id, raw_output)
                # If parsing was successful, return
                return parsed_output
            except ParsingError as e:
                self.logger.log(f"Parsing error for agent '{current_agent_id}': {e} (Attempt {attempts})", 'warning')
                # We'll loop again if we have attempts left

        # If we exit the loop, either we never got valid output or we gave up parsing it
        self.logger.log(f"Max attempts reached for agent '{current_agent_id}' with no valid parsed output.", 'error')
        # Decide if you want to return the raw output, None, or raise an exception
        raise Exception(f"Failed to get valid response from {current_agent_id}. We recommend checking the agent's input/output logs." )

    def _execute_flow(self) -> None:
        current_agent_id = self.flow.get("start")
        while current_agent_id:
            parsed_output = self._call_agent(current_agent_id)
            self._track_agent_output(current_agent_id, parsed_output)
            self.global_context[current_agent_id] = parsed_output
            current_agent_id = self._get_next_agent(current_agent_id)

    def _parse_agent_output(self, agent_id: str, output: str) -> Any:
        # Get the response format for the current agent
        response_format = self.agent_response_format[agent_id]

        if not response_format:
            return output

        if response_format == "auto":
            return self._parser.auto_parse_content(output)

        if response_format in self._parser.list_supported_formats():
            return self._parser.parse_by_format(output, response_format)

        # Should never get here because validation should catch it, but just in case:
        self.logger.warning(f"Unrecognized response_format '{response_format}' for agent '{agent_id}'. "
                            f"Returning raw output.")
        return output

    def _track_agent_output(self, agent_id: str, output: Dict[str, Any]) -> None:
        if self.enable_trail_logging:
            self.thought_flow_trail.append({agent_id: output})
            self.logger.log(f'******\n{agent_id}\n******\n{output}\n******', 'debug')

    def run(self, **kwargs: Any) -> Optional[Dict[str, Any]]:
        """
        Execute the cog by iteratively running agents as defined in the flow.
        """

        self._reset_context_and_thoughts()
        self.global_context.update(kwargs)
        self._execute_flow()
        return self.global_context
