"""
TransitionResolver module for AgentForge.

The TransitionResolver class handles all agent transition logic for Cog workflows,
including direct transitions, decision-based transitions, and end transitions.
Extracted from Cog class to improve testability and separation of concerns.
"""

from typing import Any, Dict, Optional
from agentforge.config_structs.cog_config_structs import CogFlow, CogFlowTransition
from agentforge.utils.logger import Logger


class TransitionResolverError(Exception):
    """Custom exception for TransitionResolver errors."""
    pass


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
        Initialize the TransitionResolver with the given flow configuration.
        """
        self.flow = flow
        self.logger = Logger(name="TransitionResolver", default_logger="transition_resolver")
        self.visit_counts = {}
    
    def get_next_agent(self, current_agent_id: str, agent_outputs: Dict[str, Any]) -> Optional[str]:
        """
        Determines the next agent in the flow based on transition rules.
        Delegates each step to focused helper methods for clarity.
        """
        self.logger.info(f"Getting next agent for {current_agent_id}")
        agent_transition = self._get_agent_transition(current_agent_id)
        if self._is_end_transition(agent_transition):
            return self._handle_end_transition(current_agent_id)
        next_agent = self._handle_transition(current_agent_id, agent_transition, agent_outputs)
        self.logger.info(f"Next agent for {current_agent_id}: {next_agent}")
        return next_agent

    def _is_end_transition(self, transition: CogFlowTransition) -> bool:
        """Check if the transition is an end transition."""
        return transition.type == "end" or getattr(transition, 'end', False)

    def _handle_end_transition(self, current_agent_id: str) -> None:
        """Handle end transition logic and log appropriately."""
        self.logger.log(f"End transition for {current_agent_id}, returning None", "debug", "Transition")
        return None

    def _handle_transition(self, current_agent_id: str, transition: CogFlowTransition, agent_outputs: Dict[str, Any]) -> Optional[str]:
        """Delegate to the appropriate transition handler based on type."""
        if transition.type == 'direct':
            return self._handle_direct_transition(transition)
        if transition.type == 'end':
            return self._handle_end_transition(current_agent_id)
        return self._handle_decision_transition(current_agent_id, transition, agent_outputs)

    def _handle_direct_transition(self, transition: CogFlowTransition) -> Optional[str]:
        """Handle direct transition type."""
        return transition.next_agent

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
        Raises TransitionResolverError if no transition is defined.
        """
        transitions = self.flow.transitions
        agent_transition = transitions.get(agent_id)
        if agent_transition is None:
            raise TransitionResolverError(f"No transition defined for agent: {agent_id}")
        self.logger.log(f"Transition data: {agent_transition}", "debug", "Transition")
        return agent_transition
    
    def _increment_visit_count(self, agent_id: str) -> int:
        """
        Increment the visit count for the given agent and return the new count.
        """
        self.visit_counts[agent_id] = self.visit_counts.get(agent_id, 0) + 1
        return self.visit_counts[agent_id]

    def _has_exceeded_max_visits(self, agent_id: str, max_visits: int) -> bool:
        """
        Check if the visit count for the agent exceeds max_visits.
        """
        return self.visit_counts.get(agent_id, 0) > max_visits

    def _handle_decision_transition(self, current_agent_id: str, transition: CogFlowTransition, 
                                  agent_outputs: Dict[str, Any]) -> Optional[str]:
        """
        Handle decision-based transitions:
          - Check if the max_visits limit for this agent is exceeded.
          - Otherwise, use the decision variable to select the next agent.
        """
        # Check if max_visits is exceeded (only for decision transitions)
        if transition.max_visits:
            self._increment_visit_count(current_agent_id)
            if self._has_exceeded_max_visits(current_agent_id, transition.max_visits):
                self.logger.log(f"Max visits ({transition.max_visits}) exceeded for {current_agent_id}, using fallback: {transition.fallback}", "debug", "Transition")
                return transition.fallback
        # Handle decision-based transition
        return self._handle_decision(current_agent_id, transition, agent_outputs)
    
    def _get_decision_value(self, agent_outputs: Dict[str, Any], agent_id: str, decision_key: str) -> Any:
        """
        Retrieve the decision value from the agent's output using the decision key.
        """
        if agent_id not in agent_outputs:
            return None
        return agent_outputs[agent_id].get(decision_key)

    def _map_decision_to_next_agent(self, decision_value: Any, decision_map: Dict[Any, str], fallback_branch: Optional[str]) -> Optional[str]:
        """
        Map the decision value to the next agent using the decision map, with normalization and fallback.
        """
        if decision_value is None:
            return fallback_branch
        str_decision_value = str(decision_value).lower()
        string_key_map = {str(k).lower(): v for k, v in decision_map.items()}
        return string_key_map.get(str_decision_value, fallback_branch)

    def _handle_decision(self, current_agent_id: str, transition: CogFlowTransition, 
                        agent_outputs: Dict[str, Any]) -> Optional[str]:
        """
        Handles decision-based transitions by determining the decision key
        and selecting the appropriate branch based on the agent's output.
        """
        self.logger.log(f"Handling transition for {current_agent_id}: {transition}", "debug", "Decision")
        decision_key = transition.decision_key
        fallback_branch = transition.fallback
        decision_map = transition.decision_map
        self.logger.log(f"Decision key={decision_key}, fallback={fallback_branch}", "debug", "Decision")
        if not decision_key:
            self.logger.log(f"No decision key, returning fallback: {fallback_branch}", "debug", "Decision")
            return fallback_branch
        self.logger.log(f"Decision map={decision_map}", "debug", "Decision")
        decision_value = self._get_decision_value(agent_outputs, current_agent_id, decision_key)
        self.logger.log(f"Decision value={decision_value}", "debug", "Decision")
        next_agent = self._map_decision_to_next_agent(decision_value, decision_map, fallback_branch)
        self.logger.log(f"Next agent='{next_agent}'", "debug", "Decision")
        self.logger.log(f"Decision summary: key='{decision_key}', value='{decision_value}', result='{next_agent}'", 'debug', 'Decision')
        if next_agent is None:
            self.logger.log(f"No matching branch found for decision value '{decision_value}' and no fallback branch defined", "warning", "Decision")
            self.logger.log(f"No match and no fallback", "debug", "Decision")
        self.logger.log(f"Returning next agent='{next_agent}'", "debug", "Decision")
        return next_agent 