from typing import Dict, Any, Optional, List, Union
from agentforge.config import Config
from agentforge.agent import Agent
from agentforge.utils.logger import Logger
from agentforge.storage.memory import Memory
from agentforge.config_structs import CogConfig

class Cog:
    """
    A cognitive architecture engine that orchestrates agents as defined in a YAML configuration.
    """

    ##########################################################
    # Section 1: Initialization & Configuration Loading
    ##########################################################

    def __init__(self, cog_file: str, enable_trail_logging: Optional[bool] = None, log_file: Optional[str] = 'cog'):
        # Set instance variables
        self.cog_file = cog_file
        self._reset_context_and_thoughts()

        # Initialize visit counter
        self.agent_visit_counts = {}

        # Set Config and Logger
        self.config = Config()
        self.logger: Logger = Logger(self.cog_file, log_file)

        # Load and validate configuration - now returns structured CogConfig object
        self.cog_config: CogConfig = self.config.load_cog_data(self.cog_file)
        
        # Set trail logging flag from structured config or constructor override
        self.enable_trail_logging = enable_trail_logging if enable_trail_logging is not None else self.cog_config.cog.trail_logging

        # Set up Cog (build agent nodes)
        self._build_agent_nodes()

        # Build memory nodes
        self._build_memory_nodes()

    def _reset_context_and_thoughts(self):
        self.context: dict = {}  # external context (runtime/user input)
        self.state: dict = {}    # internal state (agent-local/internal data)
        self._reset_thought_flow_trail()
        self.agent_visit_counts = {}

    def _reset_thought_flow_trail(self):
        self.thought_flow_trail: List[Dict] = []

    ##########################################################
    # Section 2: Interface Methods
    ##########################################################

    def get_track_flow_trail(self) -> List[Dict]:
        return self.thought_flow_trail

    ##########################################################
    # Section 3: Module Resolution
    ##########################################################

    def _resolve_agent_class(self, agent_def) -> type:
        """
        Resolve and return the agent class for a given agent definition.
        Assumes validation has already been performed by ConfigManager.
        """
        return self.config.resolve_class(
            agent_def.type, 
            default_class=Agent,
            context=f"agent '{agent_def.id}'"
        )

    ##########################################################
    # Section 4: Node Resolution
    ##########################################################

    def _build_agent_nodes(self) -> None:
        """Instantiate all agents defined in the cog configuration."""
        self.agents = {}
        for agent_def in self.cog_config.cog.agents:
            agent_id = agent_def.id
            agent_class = self._resolve_agent_class(agent_def)
            agent_prompt_file = agent_def.template_file or agent_class.__name__
            self.agents[agent_id] = agent_class(agent_prompt_file)

    def get_agent_transition(self, agent_id):
        """
        Get the transition definition for the specified agent.
        
        Args:
            agent_id: The ID of the agent to get the transition for
            
        Returns:
            - CogFlowTransition: The structured transition object
            
        Raises:
            Exception: If no transition is defined for the agent
        """
        transitions = self.cog_config.cog.flow.transitions
        agent_transition = transitions.get(agent_id)
        if agent_transition is None:
            raise Exception(f"There is no transition defined for agent: {agent_id}")

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
        if agent_transition.type == "end" or agent_transition.end:
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
                self.logger.log(f"Invalid transition to test agent: {next_agent}", "error", "Transition")
                raise Exception(f"Invalid transition from agent '{current_agent_id}': no agent '{next_agent}' defined in this cog.")
                
            # Check if the next agent actually exists in the cog
            if next_agent not in self.agents:
                self.logger.log(f"Invalid transition from agent '{current_agent_id}': no agent '{next_agent}' defined in this cog.", "error", "Transition")
                raise Exception(f"Invalid transition from agent '{current_agent_id}': no agent '{next_agent}' defined in this cog.")
                
        return next_agent

    def _handle_decision_transition(self, current_agent_id: str, transition) -> Optional[str]:
        """
        Handle decision-based transitions:
          - Check if the max_visits limit for this agent is exceeded.
          - Otherwise, use the decision variable to select the next agent.
          
        Args:
            current_agent_id: The ID of the current agent
            transition: CogFlowTransition object
            
        Returns:
            Optional[str]: The ID of the next agent, or None if the flow should terminate
        """
        # Handle direct transitions
        if transition.type == 'direct':
            return transition.next_agent
            
        # Handle end transitions
        if transition.type == 'end':
            return None
            
        # Check if max_visits is exceeded (only for decision transitions)
        if transition.max_visits:
            # Increment the visit count for the current agent.
            self.agent_visit_counts[current_agent_id] = self.agent_visit_counts.get(current_agent_id, 0) + 1

            # If the visit count exceeds the max_visits, return the 'fallback' branch specified in the transition.
            if self.agent_visit_counts[current_agent_id] > transition.max_visits:
                return transition.fallback

        # Handle decision-based transition
        return self._handle_decision(current_agent_id, transition)

    def _handle_decision(self, current_agent_id: str, transition) -> Optional[str]:
        """
        Handles decision-based transitions by determining the decision key
        and selecting the appropriate branch based on the agent's output.
        
        Args:
            current_agent_id: The ID of the current agent
            transition: CogFlowTransition object (must be decision type)
            
        Returns:
            Optional[str]: The ID of the next agent, or None if no matching branch is found
        """
        self.logger.log(f"Handling transition for {current_agent_id}: {transition}", "debug", "Decision")
        
        decision_key = transition.decision_key
        fallback_branch = transition.fallback
        decision_map = transition.decision_map
        
        self.logger.log(f"Decision key={decision_key}, fallback={fallback_branch}", "debug", "Decision")

        if not decision_key:
            # If no decision key, return the fallback branch directly
            self.logger.log(f"No decision key, returning fallback: {fallback_branch}", "debug", "Decision")
            return fallback_branch
            
        self.logger.log(f"Decision map={decision_map}", "debug", "Decision")
        
        # Get the decision value from the agent's output
        if current_agent_id not in self.state:
            self.logger.log(f"No output found for agent '{current_agent_id}' in internal state", "warning", "Decision")
            self.logger.log(f"No agent output, returning fallback", "debug", "Decision")
            return fallback_branch
            
        decision_value = self.state[current_agent_id].get(decision_key)
        self.logger.log(f"Decision value={decision_value}", "debug", "Decision")
        
        # If the decision value is not found in the output, use the fallback branch
        if decision_value is None:
            self.logger.log(f"Decision value for key '{decision_key}' not found in output of agent '{current_agent_id}'", "warning", "Decision")
            self.logger.log(f"Null decision value, returning fallback", "debug", "Decision")
            return fallback_branch
            
        # Get the next agent ID based on the decision value, using the fallback if no match
        # Convert decision map keys and decision_value to lowercase strings for comparison
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
            self.logger.log(f"No matching branch found for decision value '{decision_value}' and no fallback branch defined", "warning", "Decision")
            self.logger.log(f"No match and no fallback", "debug", "Decision")
            
        self.logger.log(f"Returning next agent='{next_agent}'", "debug", "Decision")
        return next_agent

    ##########################################################
    # Section 5: Memory
    ##########################################################

    @staticmethod
    def _resolve_memory_class(mem_def):
        """
        Resolve and return the memory class for a given memory definition.
        """
        return Config.resolve_class(
            mem_def.type,
            default_class=Memory,
            context=f"memory '{mem_def.id}'"
        )

    def _resolve_persona(self) -> Optional[str]:
        """
        Resolve the persona to use for this cog using the deterministic hierarchy via Config.resolve_persona.
        
        Returns:
            Optional[str]: The resolved persona name or None if personas are disabled
        """
        # Get the persona data using the Config's centralized resolution method
        # Pass the raw dict for compatibility with existing resolve_persona method
        persona_data = self.config.resolve_persona(cog_config={"cog": {"persona": self.cog_config.cog.persona}})
        
        # If personas are disabled or no persona was found, return None
        if persona_data is None:
            return None
            
        # Return the name from the persona data (needed for memory path naming)
        # This assumes each persona has a 'name' field, which is a common convention
        return persona_data.get('name', 'nameless')

    def _build_memory_nodes(self) -> None:
        # We expect a list of memory configs under cog_config.cog.memory
        self.memories = {}
        memory_list = self.cog_config.cog.memory
        
        # Resolve persona for the cog using the deterministic hierarchy
        cog_persona = self._resolve_persona()
        
        for mem_def in memory_list:
            mem_id = mem_def.id
            mem_class = self._resolve_memory_class(mem_def)
            
            # Create a unique collection ID that's independent of the cog/persona namespacing
            collection_id = mem_def.collection_id or mem_id

            # Pass cog_name and resolved persona to the Memory constructor
            mem_obj = mem_class(cog_name=self.cog_file, persona=cog_persona, collection_id=collection_id)
            self.memories[mem_id] = {
                "instance": mem_obj,
                "config": mem_def,  # store the structured config for query/update triggers
            }

    def _build_mem(self) -> dict:
        """
        Build the memory structure for agent execution.
        
        Returns:
            dict: Memory stores indexed by memory node ID
        """
        return {mem_id: mem_data["instance"].store for mem_id, mem_data in self.memories.items()}

    def _query_memory_nodes(self, agent_id: str) -> None:
        """
        Query memory nodes configured to run before the specified agent.
        
        Args:
            agent_id: The agent ID about to be executed
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
                query_text = {**self.context, **self.state}
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
                input_for_query = self._extract_keys(query_keys)
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

    def _update_memory_nodes(self, agent_id: str) -> None:
        """
        Update memory nodes configured to run after the specified agent.
        
        Args:
            agent_id: The agent ID that just completed execution
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
                update_data = {**self.context, **self.state}
                if update_data:
                    self.logger.log(f"Using merged context/state for memory {mem_id} update", "debug", "Memory")
                    mem_obj.update_memory(data=update_data, context={**self.context, **self.state})
                    self.logger.log(f"Successfully updated memory {mem_id}", "debug", "Memory")
                else:
                    self.logger.log(f"No context or state available for memory {mem_id} update", "debug", "Memory")
                continue
                
            try:
                update_data = self._extract_keys(update_keys)
                if not update_data:
                    self.logger.log(f"No update data extracted for memory {mem_id}", "debug", "Memory")
                    continue
                
                self.logger.log(f"Updating memory {mem_id} with: {list(update_data.keys())}", "debug", "Memory")
                
                # Update memory with extracted data and merged context/state for metadata
                mem_obj.update_memory(data=update_data, context={**self.context, **self.state})
                self.logger.log(f"Successfully updated memory {mem_id}", "debug", "Memory")
                
            except Exception as e:
                # Storage-level errors should be fatal
                self.logger.log(f"Memory update failed for {mem_id}: {e}", "error", "Memory")
                raise

    def _extract_keys(self, key_list):
        """
        Extract values for the given keys from self.context (external) first, then self.state (internal).
        Supports dot-notated keys for nested dict access.
        If key_list is empty or None, returns a merged dict of self.context and self.state.
        """
        if not key_list:
            merged = {**self.state, **self.context}
            return merged
        result = {}
        for key in key_list:
            value = self._get_dot_notated(self.context, key)
            if value is not None:
                result[key] = value
                continue
            value = self._get_dot_notated(self.state, key)
            if value is not None:
                result[key] = value
                continue
            raise ValueError(f"Key '{key}' not found in context or state.")
        return result

    @staticmethod
    def _get_dot_notated(source, key):
        """
        Helper to get a value from a dict using dot notation (e.g., 'foo.bar.baz').
        Returns None if any part of the path is missing.
        """
        if not isinstance(source, dict):
            return None
        parts = key.split('.')
        current = source
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current

    ##########################################################
    # Section 7: Execution
    ##########################################################

    def _call_agent(self, current_agent_id: str):
        """
        Execute an agent with retry logic.
        
        Args:
            current_agent_id: The agent to execute
            
        Returns:
            Agent output on success
            
        Raises:
            Exception: If agent fails after max attempts
        """
        attempts = 0
        max_attempts = 3
        agent = self.agents.get(current_agent_id)

        while attempts < max_attempts:
            attempts += 1
            mem = self._build_mem()
            agent_output = agent.run(_ctx=self.context, _state=self.state, _mem=mem)
            if not agent_output:
                self.logger.log(f"No output from agent '{current_agent_id}', retrying... (Attempt {attempts})", "warning")
                continue
            return agent_output

        self.logger.log(f"Max attempts reached for agent '{current_agent_id}' with no valid output.", "error")
        raise Exception(f"Failed to get valid response from {current_agent_id}. We recommend checking the agent's input/output logs.")

    def _execute_flow(self) -> None:
        """
        Execute the cog flow from start to completion.
        Orchestrates agent execution with memory query/update cycles.
        """
        self.logger.log("Starting cog execution", "debug", "Flow")
        
        current_agent_id = self.cog_config.cog.flow.start
        self.last_executed_agent = None
        self.agent_visit_counts = {}
        
        while current_agent_id:
            try:
                self.logger.log(f"Processing agent: {current_agent_id}", "debug", "Flow")
                
                # Query memory nodes before agent execution
                self._query_memory_nodes(current_agent_id)
                
                # Execute the current agent
                agent_output = self._call_agent(current_agent_id)
                
                # Store agent output in state
                self.state[current_agent_id] = agent_output
                self.last_executed_agent = current_agent_id
                
                # Track output for logging if enabled
                self._track_agent_output(current_agent_id, agent_output)
                
                # Update memory nodes after agent execution
                self._update_memory_nodes(current_agent_id)
                
                # Determine next agent in flow
                next_agent_id = self._get_next_agent(current_agent_id)
                self.logger.log(f"Next agent: {next_agent_id}", "debug", "Flow")
                
                current_agent_id = next_agent_id
                
            except Exception as e:
                self.logger.log(f"Error during cog execution: {e}", "error", "Flow")
                raise
        self.logger.log("Cog execution completed", "debug", "Flow")

    def _track_agent_output(self, agent_id: str, output: Any) -> None:
        """Track agent output in thought flow trail if logging is enabled."""
        if self.enable_trail_logging:
            self.thought_flow_trail.append({agent_id: output})
            self.logger.log(f"******\n{agent_id}\n******\n{output}\n******", "debug", "Trail")

    def get_internal_context(self) -> Dict[str, Any]:
        """
        Returns the full internal state after execution.
        
        Returns:
            Dict[str, Any]: The internal state containing all agent outputs
        """
        return self.state.copy()

    def run(self, **kwargs: Any) -> Any:
        """
        Execute the cog by iteratively running agents as defined in the flow.
        
        Args:
            **kwargs: Initial context values to provide to the agents
            
        Returns:
            Any: Based on the 'end' keyword in the final transition:
                - If 'end: true', returns the output of the last agent executed
                - If 'end: <agent_id>', returns the output of that specific agent
                - If 'end: <agent_id>.field.subfield', returns that nested value
                - Otherwise, returns the full internal state
        """
        self._reset_context_and_thoughts()
        self.context.update(kwargs)
        self._execute_flow()
        
        # Get the transition for the last executed agent
        if self.last_executed_agent:
            agent_transition = self.get_agent_transition(self.last_executed_agent)
            
            # Handle the 'end' keyword - check for end transition
            if agent_transition.type == "end" or agent_transition.end:
                # If `end: true`, return the last agent's output
                if agent_transition.end is True:
                    return self.state.get(self.last_executed_agent)
                
                # If end is a string, it could be an agent_id or dot notation
                if isinstance(agent_transition.end, str):
                    # Check if it's just an agent ID
                    if agent_transition.end in self.state:
                        return self.state[agent_transition.end]
                    # Otherwise treat as dot notation in state
                    return self._get_dot_notated(self.state, agent_transition.end)
        # Default behavior: return the full internal state
        return self.state
