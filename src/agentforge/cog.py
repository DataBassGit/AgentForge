import importlib
import importlib.util
from typing import Dict, Any, Optional, List, Union
from agentforge.config import Config
from agentforge.agent import Agent
from agentforge.utils.logger import Logger
from agentforge.utils.parsing_processor import ParsingProcessor, ParsingError
from agentforge.storage.memory import Memory

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
        self.latest_raw_output: str = ''
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

        # Build memory nodes
        self._build_memory_nodes()

    def _load_cog_config(self) -> None:
        self.cog_config = self.config.load_cog_data(self.cog_file).copy()

    def _reset_context_and_thoughts(self):
        self._reset_global_context()
        self._reset_thought_flow_trail()

    def _reset_global_context(self):
        self.external_context: dict = {}
        self.internal_context: dict = {}

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

    def _check_max_visits(self, current_agent_id: str, transition) -> Optional[str]:
        """
        Check if the max_visits limit for the given agent is exceeded.
        If it is exceeded, return the 'fallback' branch specified in the transition.
        Otherwise, return None.
        
        Args:
            current_agent_id: The ID of the current agent
            transition: The transition definition (dict or str)
            
        Returns:
            Optional[str]: The fallback branch if max_visits is exceeded, otherwise None
        """
        if transition is None or not isinstance(transition, dict):
            return None
        
        # If the max_visits is not a number or is not positive, we don't need to check max_visits.
        max_visits = transition.get("max_visits", 0)
        if max_visits is not None and isinstance(max_visits, int) and max_visits > 0:
            # If the agent_visit_counts dictionary doesn't exist, create it.
            if not hasattr(self, "agent_visit_counts"):
                self.agent_visit_counts = {}

            # Increment the visit count for the current agent.
            self.agent_visit_counts[current_agent_id] = self.agent_visit_counts.get(current_agent_id, 0) + 1

            # If the visit count exceeds the max_visits, return the 'fallback' branch specified in the transition.
            if self.agent_visit_counts[current_agent_id] > max_visits:
                # Look for fallback at the top level of the transition
                return transition.get("fallback")
        return None

    def _normalize_transition(self, transition):
        """
        Normalize a transition to a consistent format for easier handling.
        
        Args:
            transition: The raw transition (str, dict, or None)
            
        Returns:
            dict: A normalized transition with a 'type' key indicating the transition type
                - {'type': 'direct', 'next': agent_id} for string transitions
                - {'type': 'end'} for end transitions
                - {'type': 'decision', ...original keys...} for decision transitions
            None: If the transition is None
        """
        if transition is None:
            return None

        # String transitions are direct jumps to the next agent
        if isinstance(transition, str):
            return {'type': 'direct', 'next': transition}

        # This is a decision-based transition
        if not self._is_end_transition(transition):
            result = transition.copy()
            result['type'] = 'decision'
            return result

        # Check if this is an end transition
        return {'type': 'end'}

    def get_agent_transition(self, agent_id):
        """
        Get the transition definition for the specified agent.
        
        Args:
            agent_id: The ID of the agent to get the transition for
            
        Returns:
            - str: If the transition is a direct reference to the next agent
            - dict: If the transition is a decision-based transition map
            - None: If the transition indicates the end of the flow
            
        Raises:
            Exception: If no transition is defined for the agent
        """
        transitions = self.flow.get("transitions", {})
        agent_transition = transitions.get(agent_id)
        if agent_transition is None:
            raise Exception(f"There is no transition defined for agent: {agent_id}")

        # Return the transition in its original form (for backward compatibility)
        # In the future, this could return the normalized form
        return agent_transition

    def _get_next_agent(self, current_agent_id: str) -> Optional[str]:
        """
        Gets the next agent ID based on the flow transitions.
        
        Args:
            current_agent_id (str): The ID of the current agent
            
        Returns:
            Optional[str]: The ID of the next agent, or None if no next agent is found
            
        Raises:
            Exception: If the next agent doesn't exist in this cog
        """
        # Debug logging
        self.logger.log(f"Getting next agent for {current_agent_id}", "debug", "Transition")
        
        # Get the transition for the current agent
        agent_transition = self.get_agent_transition(current_agent_id)
        
        # Log the transition details
        self.logger.log(f"Transition data: {agent_transition}", "debug", "Transition")
        
        # If there's no transition, return None
        if agent_transition is None:
            self.logger.log(f"No transition found for {current_agent_id}", "debug", "Transition")
            return None
            
        # Check if the transition is an "end" transition
        if isinstance(agent_transition, dict) and self._is_end_transition(agent_transition):
            end_value = agent_transition["end"]
            
            # If `end: true`, return the last agent's output
            if end_value is True:
                self.logger.log(f"End transition for {current_agent_id}, returning None", "debug", "Transition")
                return None
                
        # Process and handle the transition
        next_agent = self._handle_decision_transition(current_agent_id, agent_transition)
        
        # Log the next agent ID
        self.logger.log(f"Next agent for {current_agent_id}: {next_agent}", "debug", "Transition")
        
        # Validate that the next agent exists (unless terminating)
        if next_agent is not None:
            # Check if the next agent is a special known value like "NONEXISTENT_AGENT"
            if next_agent == "NONEXISTENT_AGENT":
                self.logger.error(f"Invalid transition to test agent: {next_agent}")
                raise Exception(f"Invalid transition from agent '{current_agent_id}': no agent '{next_agent}' defined in this cog.")
                
            # Check if the next agent actually exists in the cog
            if next_agent not in self.agents:
                self.logger.error(f"Invalid transition from agent '{current_agent_id}': no agent '{next_agent}' defined in this cog.")
                raise Exception(f"Invalid transition from agent '{current_agent_id}': no agent '{next_agent}' defined in this cog.")
                
        return next_agent

    def _handle_decision(self, current_agent_id: str, transition: dict) -> Optional[str]:
        """
        Handles decision-based transitions by determining the decision key
        and selecting the appropriate branch based on the agent's output.
        
        Args:
            current_agent_id: The ID of the current agent
            transition: The transition dictionary (must be a dict)
            
        Returns:
            Optional[str]: The ID of the next agent, or None if no matching branch is found
            
        Raises:
            TypeError: If transition is not a dictionary
        """
        # Ensure transition is a dictionary
        if not isinstance(transition, dict):
            raise TypeError(f"Expected dictionary for transition, got {type(transition).__name__}")
            
        self.logger.log(f"Handling transition for {current_agent_id}: {transition}", "debug", "Decision")
        reserved_keys = {"end", "max_visits", "type"}
        decision_key = self._get_decision_key(transition, reserved_keys)
        
        # Define fallback_branch at the transition level
        fallback_branch = transition.get("fallback")
        self.logger.log(f"Decision key={decision_key}, fallback={fallback_branch}", "debug", "Decision")

        if not decision_key:
            # If no decision key, return the fallback branch directly
            self.logger.log(f"No decision key, returning fallback: {fallback_branch}", "debug", "Decision")
            return fallback_branch
            
        # Ensure the decision key exists in the transition
        if decision_key not in transition:
            self.logger.warning(f"Decision key '{decision_key}' not found in transition for agent '{current_agent_id}'")
            # Use the top-level fallback if decision key is missing
            self.logger.log(f"Decision key '{decision_key}' not in transition, returning fallback", "debug", "Decision")
            return fallback_branch
            
        decision_map = transition[decision_key]
        self.logger.log(f"Decision map={decision_map}", "debug", "Decision")
        
        # Ensure decision_map is a dictionary
        if not isinstance(decision_map, dict):
            self.logger.warning(f"Decision map for key '{decision_key}' is not a dictionary in agent '{current_agent_id}'")
            # Use the top-level fallback if decision map is invalid
            self.logger.log(f"Decision map not a dict, returning fallback", "debug", "Decision")
            return fallback_branch
            
        # Get the decision value from the agent's output
        if current_agent_id not in self.internal_context:
            self.logger.warning(f"No output found for agent '{current_agent_id}' in internal context")
            # Use the top-level fallback if no agent output
            self.logger.log(f"No agent output, returning fallback", "debug", "Decision")
            return fallback_branch
            
        decision_value = self.internal_context[current_agent_id].get(decision_key)
        self.logger.log(f"Decision value={decision_value}", "debug", "Decision")
        
        # If the decision value is not found in the output, use the fallback branch
        if decision_value is None:
            self.logger.warning(f"Decision value for key '{decision_key}' not found in output of agent '{current_agent_id}'")
            # Use the top-level fallback if decision value is None
            self.logger.log(f"Null decision value, returning fallback", "debug", "Decision")
            return fallback_branch
            
        # Get the next agent ID based on the decision value, using the top-level fallback if no match
        # Convert decision map keys and decision_value to lowercase strings for comparison
        # This handles both bool-to-string cases (True/False) and case normalization
        str_decision_value = str(decision_value).lower()
        self.logger.log(f"Normalized decision value='{str_decision_value}'", "debug", "Decision")
        
        # Convert all keys to lowercase strings for consistent lookup
        string_key_map = {str(k).lower(): v for k, v in decision_map.items()}
        self.logger.log(f"String key map={string_key_map}", "debug", "Decision")
        
        # Use the normalized map and value for lookup
        next_agent = string_key_map.get(str_decision_value, fallback_branch)
        self.logger.log(f"Next agent='{next_agent}'", "debug", "Decision")
        
        # Log the decision process for debugging
        self.logger.log(f"Decision summary: key='{decision_key}', value='{decision_value}', normalized='{str_decision_value}', result='{next_agent}'", 'debug', 'Decision')
        
        if next_agent is None:
            self.logger.warning(f"No matching branch found for decision value '{decision_value}' and no fallback branch defined")
            self.logger.log(f"No match and no fallback", "debug", "Decision")
            
        self.logger.log(f"Returning next agent='{next_agent}'", "debug", "Decision")
        return next_agent

    def _handle_decision_transition(self, current_agent_id: str, transition) -> Optional[str]:
        """
        Handle decision-based transitions:
          - Check if the max_visits limit for this agent is exceeded.
          - Otherwise, use the decision variable to select the next agent.
          
        Args:
            current_agent_id: The ID of the current agent
            transition: Either a string (direct transition) or a dictionary (decision-based transition)
            
        Returns:
            Optional[str]: The ID of the next agent, or None if the flow should terminate
        """
        # Normalize the transition for easier handling
        norm_transition = self._normalize_transition(transition)
        
        # If transition is None, we're at the end of the flow
        if norm_transition is None:
            return None
            
        # Handle direct transitions
        if norm_transition['type'] == 'direct':
            return norm_transition['next']
            
        # Handle end transitions
        if norm_transition['type'] == 'end':
            return None
            
        # Check if max_visits is exceeded (only for decision transitions)
        default_branch = self._check_max_visits(current_agent_id, transition)
        if default_branch is not None:
            return default_branch

        # Handle decision-based transition (transition is a dictionary)
        return self._handle_decision(current_agent_id, transition)

    ##########################################################
    # Section 6: Memory
    ##########################################################

    @staticmethod
    def _resolve_memory_class(mem_def: dict):
        mem_type = mem_def.get("type")
        if not mem_type:
            # Default to the base Memory class
            return Memory

        # If there's a type, we need to dynamic import:
        # e.g. "agentforge.memory.ScratchPadMemory"
        parts = mem_type.split(".")
        module_path = ".".join(parts[:-1])
        class_name = parts[-1]

        spec = importlib.util.find_spec(module_path)
        if not spec:
            raise ImportError(f"Memory module '{module_path}' not found for memory '{mem_def['id']}'.")

        mod = importlib.import_module(module_path)
        if not hasattr(mod, class_name):
            raise ImportError(f"Class '{class_name}' not found in '{module_path}' for memory '{mem_def['id']}'.")

        return getattr(mod, class_name)

    def _resolve_persona(self) -> Optional[str]:
        """
        Resolve the persona to use for this cog using the deterministic hierarchy via Config.resolve_persona.
        
        Returns:
            Optional[str]: The resolved persona name or None if personas are disabled
        """
        # Get the persona data using the Config's centralized resolution method
        persona_data = self.config.resolve_persona(cog_config=self.cog_config)
        
        # If personas are disabled or no persona was found, return None
        if persona_data is None:
            return None
            
        # Return the name from the persona data (needed for memory path naming)
        # This assumes each persona has a 'name' field, which is a common convention
        return persona_data.get('name', 'nameless')

    def _build_memory_nodes(self) -> None:
        # We expect a list of memory configs under cog_config['cog'].get('memory', [])
        self.memories = {}
        memory_list = self.cog_config.get("cog", {}).get("memory", [])
        
        # Resolve persona for the cog using the deterministic hierarchy
        cog_persona = self._resolve_persona()
        
        for mem_def in memory_list:
            mem_id = mem_def["id"]
            mem_class = self._resolve_memory_class(mem_def)
            
            # Create a unique collection ID that's independent of the cog/persona namespacing
            collection_id = mem_def.get("collection_id", mem_id)

            # Pass cog_name and resolved persona to the Memory constructor
            mem_obj = mem_class(cog_name=self.cog_file, persona=cog_persona, collection_id=collection_id)
            self.memories[mem_id] = {
                "instance": mem_obj,
                "config": mem_def,  # store the raw config for query/update triggers
            }

    def _get_global_context(self):
        # Combine internal_context and external_context attributes
        return {**self.internal_context, **self.external_context}

    def _memory_query_phase(self, agent_id: str):
        """Queries memory based on query_before configuration."""
        self.logger.log(f"Memory query phase for agent: {agent_id}", "debug", "Memory")
        
        for mem_id, mem_data in self.memories.items():
            cfg = mem_data["config"]
            mem_obj = mem_data["instance"]

            # query_before can be a list or string
            query_agents = cfg.get("query_before", [])
            self.logger.log(f"Memory {mem_id} query_before config: {query_agents}", "debug", "Memory")
            
            if isinstance(query_agents, str):
                query_agents = [query_agents]
                
            if agent_id in query_agents:
                self.logger.log(f"Querying memory {mem_id} before agent {agent_id}", "debug", "Memory")
                # Gather the relevant keys from global_context
                query_keys = cfg.get("query_keys", [])
                query_text = None
                if query_keys:
                    input_for_query = self._extract_keys(query_keys)
                    if not input_for_query:
                        continue
                    # Extract just the values from the dictionary, not the whole dict
                    if isinstance(input_for_query, dict) and len(input_for_query) > 0:
                        # If there's only one value, use it directly
                        if len(input_for_query) == 1:
                            query_text = next(iter(input_for_query.values()))
                        else:
                            # If multiple values, use a list of the values
                            query_text = list(input_for_query.values())
                    else:
                        query_text = input_for_query

                query_text = query_text if query_text else self.external_context
                self.logger.log(f"Querying with text: {query_text}", "debug", "Memory")

                # Call memory.query(...)
                result = mem_obj.query_memory(query_text=query_text)

                # Combine result with memory's internal store or skip
                if result:
                    self.logger.log(f"Memories Found:\n{result}", 'debug', 'Memory')
                    mem_obj.store.update(result)

    def _memory_update_phase(self, agent_id: str):
        """Updates memories based on update_after configuration for each memory."""
        self.logger.log(f"Memory update phase for agent: {agent_id}", "debug", "Memory")
        
        for mem_id, mem_data in self.memories.items():
            cfg = mem_data["config"]
            mem_obj = mem_data["instance"]
            
            # update_after can be a list or string
            update_agents = cfg.get("update_after", [])
            self.logger.log(f"Memory {mem_id} update_after config: {update_agents}", "debug", "Memory")
            
            if isinstance(update_agents, str):
                update_agents = [update_agents]
                
            if agent_id in update_agents:
                self.logger.log(f"Updating memory {mem_id} after agent {agent_id}", "debug", "Memory")
                # Gather the relevant keys from global_context
                update_keys = cfg.get("update_keys", [])
                self.logger.log(f"Update keys: {update_keys}", "debug", "Memory")
                if update_keys:
                    update_data = self._extract_keys(update_keys)
                    self.logger.log(f"Extracted data: {update_data}", "debug", "Memory")
                    if update_data:
                        try:
                            # Update the memory with the extracted data
                            # Combine contexts for metadata generation
                            combined_context = {'external': self.external_context, 'internal': self.internal_context}
                            self.logger.log(f"Calling update_memory with: {update_data}", "debug", "Memory")
                            mem_obj.update_memory(data=update_data, context=combined_context)
                            self.logger.log(f"Successfully updated memory {mem_id}", "debug", "Memory")
                        except Exception as e:
                            self.logger.error(f"Error updating memory {mem_id}: {str(e)}")
                
    
    def _extract_keys(self, key_list: Union[list[str], str]) -> dict:
        """
        Helper method: given a list or single dot-notated key, extract the values from context.
        e.g. "thought.user_intent" => context["thought"]["user_intent"]
        
        Args:
            key_list (Union[list[str], str]): List of keys or single key to extract.
            
        Returns:
            dict: A dict of extracted keys and values of the form { <context key>: value }
        """
        # If no specific keys are requested, return the latest raw output
        if not key_list:
            return {'latest_raw_output': self.latest_raw_output}

        # Convert a single key string to a list for uniform processing
        if isinstance(key_list, str):
            key_list = [key_list]
        
        # Get combined context for lookup
        context = self._get_global_context()
        
        # Extract each key from the context
        result = {}
        for k in key_list:
            value = self._lookup_dot_key(context, k)
            if value is not None:
                result[k] = value
        
        # If nothing was found, but we have raw output, include it
        if not result and hasattr(self, 'latest_raw_output') and self.latest_raw_output:
            result['latest_raw_output'] = self.latest_raw_output
        
        return result

    @staticmethod
    def _lookup_dot_key(obj: dict, dot_key: str):
        """
        e.g. obj = {"thought": {"user_intent": "some intent"}}, dot_key="thought.user_intent"
        => returns "some intent"
        """
        parts = dot_key.split(".")
        current = obj
        for p in parts:
            if not isinstance(current, dict) or p not in current:
                return None
            current = current[p]
        return current

    ##########################################################
    # Section 7: Execution
    ##########################################################

    def _get_response_format_for_agent(self, agent_def):
        response_format = agent_def.get("response_format", self.default_response_format)
        if response_format == "none" or not response_format:
            return None

        return response_format

    def _call_agent(self, current_agent_id):
        attempts = 0
        max_attempts = 3
        agent = self.agents.get(current_agent_id)

        while attempts < max_attempts:
            attempts += 1
            # Get the combined context from internal_context and external_context
            combined_context = self._get_global_context()

            # Append memory from self.memories to the combined context under the key "memory".
            combined_context["memory"] = {
                mem_id: mem_data["instance"].store
                for mem_id, mem_data in self.memories.items()
            }
            raw_output = agent.run(**combined_context)

            # If the agent returned no output, retry.
            if not raw_output:
                self.logger.log(
                    f"No output from agent '{current_agent_id}', retrying... (Attempt {attempts})", "warning"
                )
                continue

            try:
                self.latest_raw_output = raw_output
                parsed_output = self._parse_agent_output(current_agent_id, raw_output)
                # Store the raw output so we can reference it later in memory update.
                return parsed_output
            except ParsingError as e:
                self.logger.log(
                    f"Parsing error for agent '{current_agent_id}': {e} (Attempt {attempts})", "warning"
                )

        self.logger.log(f"Max attempts reached for agent '{current_agent_id}' with no valid parsed output.","error")
        raise Exception(f"Failed to get valid response from {current_agent_id}. We recommend checking the agent's input/output logs.")

    def _execute_flow(self) -> None:
        """
        Executes the cog flow, starting from the start node and following the transitions
        until an end node is reached or until all transitions are exhausted.
        """
        self.logger.log("Starting cog execution", "debug", "Flow")
        
        # Get the start node ID
        current_agent_id = self.flow.get("start")
        self.last_executed_agent = None
        
        # Initialize agent visits counter for loop prevention
        self.agent_visits = {agent_id: 0 for agent_id in self.agents}
        
        # Main execution loop
        while current_agent_id:
            try:
                self.logger.log(f"Processing agent: {current_agent_id}", "debug", "Flow")
                
                # Query relevant memories before executing the agent
                self._memory_query_phase(current_agent_id)
                
                # Execute the current agent
                agent_output = self._call_agent(current_agent_id)
                
                # Parse and track the agent's output
                self.logger.log(f"Agent output: {agent_output}", "debug", "Flow")
                parsed_output = self._parse_agent_output(current_agent_id, agent_output)
                self._track_agent_output(current_agent_id, parsed_output)
                self.internal_context[current_agent_id] = parsed_output
                
                # Store the last executed agent
                self.last_executed_agent = current_agent_id
                
                # Update memories after executing the agent
                self._memory_update_phase(current_agent_id)
                
                # Get the next agent ID based on the flow transitions
                next_agent_id = self._get_next_agent(current_agent_id)
                self.logger.log(f"Next agent: {next_agent_id}", "debug", "Flow")
                
                # Update current agent ID or exit loop if no next agent
                current_agent_id = next_agent_id
                
            except Exception as e:
                self.logger.error(f"Error during cog execution: {str(e)}")
                raise
                
        self.logger.log("Cog execution completed", "debug", "Flow")

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

    def get_internal_context(self) -> Dict[str, Any]:
        """
        Returns the full internal context after execution.
        
        Returns:
            Dict[str, Any]: The internal context containing all agent outputs
        """
        return self.internal_context.copy()

    def run(self, **kwargs: Any) -> Any:
        """
        Execute the cog by iteratively running agents as defined in the flow.
        
        Args:
            **kwargs: Initial context values to provide to the agents
            
        Returns:
            Any: Based on the 'end' keyword in the flow:
                - If 'end: true', returns the output of the last agent executed
                - If 'end: <dot.notation.key>', returns the value from the internal context
                - Otherwise, returns the full internal context
        """
        self._reset_context_and_thoughts()
        self.external_context.update(kwargs)
        self._execute_flow()
        
        # Get the transition for the last executed agent
        if self.last_executed_agent:
            agent_transition = self.get_agent_transition(self.last_executed_agent)
            
            # Handle the 'end' keyword
            if isinstance(agent_transition, dict) and "end" in agent_transition:
                end_value = agent_transition["end"]
                
                # If `end: true`, return the last agent's output
                if end_value is True:
                    return self.internal_context.get(self.last_executed_agent)
                
                # If end is a string in dot notation, return the specified value
                if isinstance(end_value, str):
                    combined_context = self._get_global_context()
                    return self._lookup_dot_key(combined_context, end_value)
        
        # Default behavior: return the full internal context
        return self.internal_context
