"""
TransitionResolver module for AgentForge.

The TransitionResolver class handles all agent transition logic for Cog workflows,
including direct transitions, decision-based transitions, and end transitions.
Extracted from Cog class to improve testability and separation of concerns.
"""

from typing import Any, Dict, Optional
from agentforge.config_structs.cog_config_structs import CogFlow, CogFlowTransition
from agentforge.utils.logger import Logger


class TransitionResolver:
    """
    Resolves agent transitions based on current state and flow configuration.
    
    This class encapsulates all transition logic for Cog workflows, including:
    - Direct transitions to next agents
    - Decision-based transitions using agent output
    - End transitions that terminate the flow
    - Visit count tracking for loop prevention
    """
    
    def __init__(self, flow: CogFlow):
        """
        Initialize the TransitionResolver.
        
        Args:
            flow: The CogFlow configuration containing transition definitions
        """
        self.flow = flow
        self.logger = Logger(name="TransitionResolver", default_logger="transition_resolver")
        self.visit_counts: Dict[str, int] = {}
    
    def get_next_agent(self, current_agent_id: str, agent_outputs: Dict[str, Any]) -> Optional[str]:
        """
        Determines the next agent in the flow based on transition rules.
        
        Args:
            current_agent_id: The ID of the current agent
            agent_outputs: Dictionary mapping agent_id -> agent_output
            
        Returns:
            The ID of the next agent, or None if the flow should terminate
            
        Raises:
            Exception: If no transition is defined for the agent
        """
        # Debug logging
        self.logger.log(f"Getting next agent for {current_agent_id}", "debug", "Transition")
        
        # Get the transition for the current agent
        agent_transition = self._get_agent_transition(current_agent_id)
        
        # Log the transition details
        self.logger.log(f"Transition data: {agent_transition}", "debug", "Transition")
        
        # Check if the transition is an "end" transition
        if agent_transition.type == "end" or agent_transition.end:
            self.logger.log(f"End transition for {current_agent_id}, returning None", "debug", "Transition")
            return None
                
        # Process and handle the transition
        next_agent = self._handle_decision_transition(current_agent_id, agent_transition, agent_outputs)
        
        # Log the next agent ID
        self.logger.log(f"Next agent for {current_agent_id}: {next_agent}", "debug", "Transition")
        
        return next_agent
    
    def reset_visit_counts(self) -> None:
        """Reset visit tracking for new flow execution."""
        self.visit_counts = {}
        self.logger.log("Reset visit counts for new flow execution", "debug", "Transition")
    
    def get_visit_count(self, agent_id: str) -> int:
        """
        Get current visit count for an agent.
        
        Args:
            agent_id: The agent ID to check
            
        Returns:
            The number of times this agent has been visited
        """
        return self.visit_counts.get(agent_id, 0)
    
    def _get_agent_transition(self, agent_id: str) -> CogFlowTransition:
        """
        Get the transition definition for the specified agent.
        
        Args:
            agent_id: The ID of the agent to get the transition for
            
        Returns:
            The structured transition object
            
        Raises:
            Exception: If no transition is defined for the agent
        """
        transitions = self.flow.transitions
        agent_transition = transitions.get(agent_id)
        
        # Runtime protection: ConfigManager validates flow references during config construction,
        # but this check protects against potential flow execution bugs
        if agent_transition is None:
            raise Exception(f"There is no transition defined for agent: {agent_id}")

        return agent_transition
    
    def _handle_decision_transition(self, current_agent_id: str, transition: CogFlowTransition, 
                                  agent_outputs: Dict[str, Any]) -> Optional[str]:
        """
        Handle decision-based transitions:
          - Check if the max_visits limit for this agent is exceeded.
          - Otherwise, use the decision variable to select the next agent.
          
        Args:
            current_agent_id: The ID of the current agent
            transition: CogFlowTransition object
            agent_outputs: Dictionary mapping agent_id -> agent_output
            
        Returns:
            The ID of the next agent, or None if the flow should terminate
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
            self.visit_counts[current_agent_id] = self.visit_counts.get(current_agent_id, 0) + 1

            # If the visit count exceeds the max_visits, return the 'fallback' branch specified in the transition.
            if self.visit_counts[current_agent_id] > transition.max_visits:
                self.logger.log(f"Max visits ({transition.max_visits}) exceeded for {current_agent_id}, using fallback: {transition.fallback}", "debug", "Transition")
                return transition.fallback

        # Handle decision-based transition
        return self._handle_decision(current_agent_id, transition, agent_outputs)
    
    def _handle_decision(self, current_agent_id: str, transition: CogFlowTransition, 
                        agent_outputs: Dict[str, Any]) -> Optional[str]:
        """
        Handles decision-based transitions by determining the decision key
        and selecting the appropriate branch based on the agent's output.
        
        Args:
            current_agent_id: The ID of the current agent
            transition: CogFlowTransition object (must be decision type)
            agent_outputs: Dictionary mapping agent_id -> agent_output
            
        Returns:
            The ID of the next agent, or None if no matching branch is found
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
        if current_agent_id not in agent_outputs:
            self.logger.log(f"No output found for agent '{current_agent_id}' in agent outputs", "warning", "Decision")
            self.logger.log(f"No agent output, returning fallback", "debug", "Decision")
            return fallback_branch
            
        decision_value = agent_outputs[current_agent_id].get(decision_key)
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