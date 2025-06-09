"""
Unit tests for the TransitionResolver class.

Tests all transition types (direct, decision, end), edge cases, error handling,
and visit count management for the transition resolver.
"""

import pytest
from unittest.mock import Mock, patch

from agentforge.config_structs.cog_config_structs import CogFlow, CogFlowTransition
from agentforge.core.transition_resolver import TransitionResolver, TransitionResolverError


class TestTransitionResolver:
    """Test suite for TransitionResolver functionality."""

    def test_direct_transition(self):
        """Test simple direct transitions."""
        # Setup
        transitions = {
            "agent1": CogFlowTransition(type="direct", next_agent="agent2"),
            "agent2": CogFlowTransition(type="end", end=True)
        }
        flow = CogFlow(start="agent1", transitions=transitions)
        resolver = TransitionResolver(flow)
        
        # Test
        next_agent = resolver.get_next_agent("agent1", {})
        
        # Assert
        assert next_agent == "agent2"

    def test_end_transition(self):
        """Test end transitions that terminate the flow."""
        # Setup
        transitions = {
            "agent1": CogFlowTransition(type="end", end=True)
        }
        flow = CogFlow(start="agent1", transitions=transitions)
        resolver = TransitionResolver(flow)
        
        # Test
        next_agent = resolver.get_next_agent("agent1", {})
        
        # Assert
        assert next_agent is None

    def test_decision_transition_with_match(self):
        """Test decision transitions with matching decision values."""
        # Setup
        transitions = {
            "decide_agent": CogFlowTransition(
                type="decision",
                decision_key="choice",
                decision_map={"approve": "agent2", "reject": "agent3"},
                fallback="agent4"
            )
        }
        flow = CogFlow(start="decide_agent", transitions=transitions)
        resolver = TransitionResolver(flow)
        
        agent_outputs = {
            "decide_agent": {"choice": "approve"}
        }
        
        # Test
        next_agent = resolver.get_next_agent("decide_agent", agent_outputs)
        
        # Assert
        assert next_agent == "agent2"

    def test_decision_transition_with_fallback(self):
        """Test decision transitions using fallback for unmatched values."""
        # Setup
        transitions = {
            "decide_agent": CogFlowTransition(
                type="decision",
                decision_key="choice",
                decision_map={"approve": "agent2", "reject": "agent3"},
                fallback="agent4"
            )
        }
        flow = CogFlow(start="decide_agent", transitions=transitions)
        resolver = TransitionResolver(flow)
        
        agent_outputs = {
            "decide_agent": {"choice": "unknown_value"}
        }
        
        # Test
        next_agent = resolver.get_next_agent("decide_agent", agent_outputs)
        
        # Assert
        assert next_agent == "agent4"

    def test_decision_transition_missing_key_uses_fallback(self):
        """Test decision transitions use fallback when decision key is missing."""
        # Setup
        transitions = {
            "decide_agent": CogFlowTransition(
                type="decision",
                decision_key="choice",
                decision_map={"approve": "agent2"},
                fallback="agent4"
            )
        }
        flow = CogFlow(start="decide_agent", transitions=transitions)
        resolver = TransitionResolver(flow)
        
        agent_outputs = {
            "decide_agent": {"other_key": "value"}  # Missing 'choice' key
        }
        
        # Test
        next_agent = resolver.get_next_agent("decide_agent", agent_outputs)
        
        # Assert
        assert next_agent == "agent4"

    def test_decision_transition_missing_agent_output_uses_fallback(self):
        """Test decision transitions use fallback when agent output is missing."""
        # Setup
        transitions = {
            "decide_agent": CogFlowTransition(
                type="decision",
                decision_key="choice",
                decision_map={"approve": "agent2"},
                fallback="agent4"
            )
        }
        flow = CogFlow(start="decide_agent", transitions=transitions)
        resolver = TransitionResolver(flow)
        
        agent_outputs = {}  # No output for decide_agent
        
        # Test
        next_agent = resolver.get_next_agent("decide_agent", agent_outputs)
        
        # Assert
        assert next_agent == "agent4"

    def test_decision_transition_case_insensitive_matching(self):
        """Test that decision values are matched case-insensitively."""
        # Setup
        transitions = {
            "decide_agent": CogFlowTransition(
                type="decision",
                decision_key="choice",
                decision_map={"approve": "agent2", "reject": "agent3"},
                fallback="agent4"
            )
        }
        flow = CogFlow(start="decide_agent", transitions=transitions)
        resolver = TransitionResolver(flow)
        
        test_cases = [
            ("APPROVE", "agent2"),
            ("Approve", "agent2"),
            ("approve", "agent2"),
            ("REJECT", "agent3"),
            ("Reject", "agent3"),
            ("reject", "agent3")
        ]
        
        for decision_value, expected_agent in test_cases:
            agent_outputs = {
                "decide_agent": {"choice": decision_value}
            }
            
            # Test
            next_agent = resolver.get_next_agent("decide_agent", agent_outputs)
            
            # Assert
            assert next_agent == expected_agent, f"Failed for decision value: {decision_value}"

    def test_max_visits_exceeded_uses_fallback(self):
        """Test that max_visits protection uses fallback when exceeded."""
        # Setup
        transitions = {
            "loop_agent": CogFlowTransition(
                type="decision",
                decision_key="choice",
                decision_map={"continue": "loop_agent"},
                fallback="exit_agent",
                max_visits=2
            )
        }
        flow = CogFlow(start="loop_agent", transitions=transitions)
        resolver = TransitionResolver(flow)
        
        agent_outputs = {
            "loop_agent": {"choice": "continue"}
        }
        
        # Test first visit - should continue looping
        next_agent1 = resolver.get_next_agent("loop_agent", agent_outputs)
        assert next_agent1 == "loop_agent"
        
        # Test second visit - should continue looping
        next_agent2 = resolver.get_next_agent("loop_agent", agent_outputs)
        assert next_agent2 == "loop_agent"
        
        # Test third visit - should use fallback due to max_visits
        next_agent3 = resolver.get_next_agent("loop_agent", agent_outputs)
        assert next_agent3 == "exit_agent"

    def test_visit_count_tracking(self):
        """Test that visit counts are tracked correctly."""
        # Setup
        transitions = {
            "agent1": CogFlowTransition(type="direct", next_agent="agent2"),
            "agent2": CogFlowTransition(type="direct", next_agent="agent1")
        }
        flow = CogFlow(start="agent1", transitions=transitions)
        resolver = TransitionResolver(flow)
        
        # Initial visit counts should be zero
        assert resolver.get_visit_count("agent1") == 0
        assert resolver.get_visit_count("agent2") == 0
        
        # Visit counts should only increase for decision transitions with max_visits
        resolver.get_next_agent("agent1", {})
        assert resolver.get_visit_count("agent1") == 0  # Direct transition doesn't count
        
        resolver.get_next_agent("agent2", {})
        assert resolver.get_visit_count("agent2") == 0  # Direct transition doesn't count

    def test_visit_count_reset(self):
        """Test that visit counts are reset properly."""
        # Setup
        transitions = {
            "loop_agent": CogFlowTransition(
                type="decision",
                decision_key="choice",
                decision_map={"continue": "loop_agent"},
                fallback="exit_agent",
                max_visits=1
            )
        }
        flow = CogFlow(start="loop_agent", transitions=transitions)
        resolver = TransitionResolver(flow)
        
        agent_outputs = {
            "loop_agent": {"choice": "continue"}
        }
        
        # Generate some visits
        resolver.get_next_agent("loop_agent", agent_outputs)
        assert resolver.get_visit_count("loop_agent") == 1
        
        # Reset and verify
        resolver.reset_visit_counts()
        assert resolver.get_visit_count("loop_agent") == 0

    def test_no_decision_key_uses_fallback(self):
        """Test that transitions with no decision key use fallback."""
        # Setup
        transitions = {
            "agent1": CogFlowTransition(
                type="decision",
                decision_key=None,
                decision_map={},
                fallback="agent2"
            )
        }
        flow = CogFlow(start="agent1", transitions=transitions)
        resolver = TransitionResolver(flow)
        
        # Test
        next_agent = resolver.get_next_agent("agent1", {})
        
        # Assert
        assert next_agent == "agent2"

    def test_invalid_agent_raises_exception(self):
        """Test that requesting transition for non-existent agent raises exception."""
        # Setup
        transitions = {
            "agent1": CogFlowTransition(type="direct", next_agent="agent2")
        }
        flow = CogFlow(start="agent1", transitions=transitions)
        resolver = TransitionResolver(flow)
        
        # Test
        with pytest.raises(TransitionResolverError, match="No transition defined for agent: nonexistent"):
            resolver.get_next_agent("nonexistent", {})

    @patch('agentforge.core.transition_resolver.Logger')
    def test_logging_behavior(self, mock_logger_class):
        """Test that TransitionResolver creates its own logger and logs appropriately."""
        # Setup
        mock_logger = Mock()
        mock_logger_class.return_value = mock_logger
        
        transitions = {
            "agent1": CogFlowTransition(type="direct", next_agent="agent2")
        }
        flow = CogFlow(start="agent1", transitions=transitions)
        resolver = TransitionResolver(flow)
        
        # Verify logger initialization
        mock_logger_class.assert_called_once_with(name="TransitionResolver", default_logger="transition_resolver")
        
        # Execute transition
        resolver.get_next_agent("agent1", {})
        
        # Verify logging calls
        assert mock_logger.info.call_count >= 2  # Getting and result logs

    def test_decision_transition_with_no_fallback_returns_none(self):
        """Test decision transitions with no fallback return None for unmatched values."""
        # Setup
        transitions = {
            "decide_agent": CogFlowTransition(
                type="decision",
                decision_key="choice",
                decision_map={"approve": "agent2"},
                fallback=None
            )
        }
        flow = CogFlow(start="decide_agent", transitions=transitions)
        resolver = TransitionResolver(flow)
        
        agent_outputs = {
            "decide_agent": {"choice": "unknown_value"}
        }
        
        # Test
        next_agent = resolver.get_next_agent("decide_agent", agent_outputs)
        
        # Assert
        assert next_agent is None

    def test_mixed_type_decision_values(self):
        """Test that decision values handle different types correctly."""
        # Setup
        transitions = {
            "decide_agent": CogFlowTransition(
                type="decision",
                decision_key="choice",
                decision_map={"true": "agent2", "false": "agent3", "1": "agent4"},
                fallback="agent5"
            )
        }
        flow = CogFlow(start="decide_agent", transitions=transitions)
        resolver = TransitionResolver(flow)
        
        test_cases = [
            (True, "agent2"),   # Boolean True -> "true"
            (False, "agent3"),  # Boolean False -> "false"
            (1, "agent4"),      # Integer 1 -> "1"
            ("true", "agent2"), # String "true"
            ("false", "agent3") # String "false"
        ]
        
        for decision_value, expected_agent in test_cases:
            agent_outputs = {
                "decide_agent": {"choice": decision_value}
            }
            
            # Test
            next_agent = resolver.get_next_agent("decide_agent", agent_outputs)
            
            # Assert
            assert next_agent == expected_agent, f"Failed for decision value: {decision_value} (type: {type(decision_value)})"

    def test_complex_decision_flow(self):
        """Test a complex flow with multiple decision points and edge cases."""
        # Setup
        transitions = {
            "start": CogFlowTransition(type="direct", next_agent="analyze"),
            "analyze": CogFlowTransition(type="direct", next_agent="decide"),
            "decide": CogFlowTransition(
                type="decision",
                decision_key="verdict",
                decision_map={"approve": "process", "reject": "analyze", "escalate": "human_review"},
                fallback="error_handler",
                max_visits=3
            ),
            "process": CogFlowTransition(type="direct", next_agent="finalize"),
            "human_review": CogFlowTransition(type="end", end=True),
            "error_handler": CogFlowTransition(type="end", end=True),
            "finalize": CogFlowTransition(type="end", end=True)
        }
        flow = CogFlow(start="start", transitions=transitions)
        resolver = TransitionResolver(flow)
        
        # Test the flow sequence
        assert resolver.get_next_agent("start", {}) == "analyze"
        assert resolver.get_next_agent("analyze", {}) == "decide"
        
        # Reset visit counts before testing decision routing to ensure clean state
        resolver.reset_visit_counts()
        
        # Test decision routing
        agent_outputs = {"decide": {"verdict": "approve"}}
        assert resolver.get_next_agent("decide", agent_outputs) == "process"
        
        # Reset again before testing escalation
        resolver.reset_visit_counts()
        
        agent_outputs = {"decide": {"verdict": "escalate"}}
        assert resolver.get_next_agent("decide", agent_outputs) == "human_review"
        
        # Reset again before testing max visits protection
        resolver.reset_visit_counts()
        
        # Test max visits protection
        agent_outputs = {"decide": {"verdict": "reject"}}
        assert resolver.get_next_agent("decide", agent_outputs) == "analyze"  # 1st rejection
        assert resolver.get_next_agent("decide", agent_outputs) == "analyze"  # 2nd rejection  
        assert resolver.get_next_agent("decide", agent_outputs) == "analyze"  # 3rd rejection
        assert resolver.get_next_agent("decide", agent_outputs) == "error_handler"  # 4th -> fallback
        
        # Test end transitions
        assert resolver.get_next_agent("finalize", {}) is None
        assert resolver.get_next_agent("human_review", {}) is None
        assert resolver.get_next_agent("error_handler", {}) is None 