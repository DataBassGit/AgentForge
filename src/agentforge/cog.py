from typing import Dict, Any, Optional, List, Union
from agentforge.config import Config
from agentforge.utils.logger import Logger
from agentforge.config_structs import CogConfig
from agentforge.core.agent_registry import AgentRegistry
from agentforge.core.agent_runner import AgentRunner
from agentforge.core.memory_manager import MemoryManager
from agentforge.utils.parsing_processor import ParsingProcessor

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

        # Set Config and Logger
        self.config = Config()
        self.logger: Logger = Logger(self.cog_file, log_file)

        # Load and validate configuration - returns structured CogConfig object
        self.cog_config: CogConfig = self.config.load_cog_data(self.cog_file)
        
        # Set trail logging flag from structured config or constructor override
        self.enable_trail_logging = enable_trail_logging if enable_trail_logging is not None else self.cog_config.cog.trail_logging

        # Set up Cog Agent Nodes, Memory Manager, and Agent Runner
        self.agents = AgentRegistry.build_agents(self.cog_config)
        self.mem_mgr = MemoryManager(self.cog_config, self.cog_file)
        self.agent_runner = AgentRunner()

    def _reset_context_and_thoughts(self):
        self.context: dict = {}  # external context (runtime/user input)
        self.state: dict = {}    # internal state (agent-local/internal data)
        self.agent_visit_counts: dict = {} # track visit counts for each agent
        self._reset_thought_flow_trail()

    def _reset_thought_flow_trail(self):
        self.thought_flow_trail: List[Dict] = []

    ##########################################################
    # Section 2: Interface Methods
    ##########################################################

    def get_track_flow_trail(self) -> List[Dict]:
        return self.thought_flow_trail

    ##########################################################
    # Section 3: Agent Transitions
    ##########################################################

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
        
        # Runtime protection: ConfigManager validates flow references during config construction,
        # but this check protects against potential flow execution bugs
        if agent_transition is None:
            raise Exception(f"There is no transition defined for agent: {agent_id}")

        return agent_transition

    ##########################################################
    # Section 4: Node Resolution
    ##########################################################

    def _get_next_agent(self, current_agent_id: str) -> Optional[str]:
        """
        Gets the next agent ID based on the flow transitions.
        
        Args:
            current_agent_id (str): The ID of the current agent
            
        Returns:
            Optional[str]: The ID of the next agent, or None if no next agent is found
        """
        # Debug logging
        self.logger.log(f"Getting next agent for {current_agent_id}", "debug", "Transition")
        
        # Get the transition for the current agent - ConfigManager has already validated this exists
        agent_transition = self.get_agent_transition(current_agent_id)
        
        # Log the transition details
        self.logger.log(f"Transition data: {agent_transition}", "debug", "Transition")
        
        # Check if the transition is an "end" transition
        if agent_transition.type == "end" or agent_transition.end:
            self.logger.log(f"End transition for {current_agent_id}, returning None", "debug", "Transition")
            return None
                
        # Process and handle the transition
        next_agent = self._handle_decision_transition(current_agent_id, agent_transition)
        
        # Log the next agent ID
        self.logger.log(f"Next agent for {current_agent_id}: {next_agent}", "debug", "Transition")
        
        # ConfigManager has already validated that all flow references are valid
        # Trust the structured config and assume next_agent exists in self.agents
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
    # Section 5: Execution
    ##########################################################

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
                self.mem_mgr.query_before(current_agent_id, self.context, self.state)
                
                # Execute the current agent
                agent = self.agents.get(current_agent_id)
                mem = self.mem_mgr.build_mem()
                agent_output = self.agent_runner.run_agent(current_agent_id, agent, self.context, self.state, mem)
                
                # Store agent output in state
                self.state[current_agent_id] = agent_output
                self.last_executed_agent = current_agent_id
                
                # Track output for logging if enabled
                self._track_agent_output(current_agent_id, agent_output)
                
                # Update memory nodes after agent execution
                self.mem_mgr.update_after(current_agent_id, self.context, self.state)
                
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
                    return ParsingProcessor.get_dot_notated(self.state, agent_transition.end)
        # Default behavior: return the full internal state
        return self.state
