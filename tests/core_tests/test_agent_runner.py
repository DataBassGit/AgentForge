"""
Tests for the AgentRunner class.

This module tests the agent execution and retry logic that was extracted from Cog.
"""

import pytest
from unittest.mock import Mock, patch
from agentforge.core.agent_runner import AgentRunner


class TestAgentRunner:
    """Test suite for AgentRunner functionality."""

    def test_successful_agent_execution(self):
        """Test that a successful agent execution returns the expected output."""
        # Setup
        runner = AgentRunner()
        mock_agent = Mock()
        mock_agent.run.return_value = "test output"
        
        # Execute
        result = runner.run_agent(
            agent_id="test_agent",
            agent=mock_agent,
            context={"key": "value"},
            state={"state_key": "state_value"},
            memory={"mem_key": "mem_value"}
        )
        
        # Verify
        assert result == "test output"
        mock_agent.run.assert_called_once_with(
            _ctx={"key": "value"},
            _state={"state_key": "state_value"},
            _mem={"mem_key": "mem_value"}
        )

    def test_retry_on_empty_output(self):
        """Test that agent runner retries when agent returns empty output."""
        # Setup
        runner = AgentRunner()
        mock_agent = Mock()
        # First call returns None, second call returns valid output
        mock_agent.run.side_effect = [None, "valid output"]
        
        # Execute
        result = runner.run_agent(
            agent_id="test_agent",
            agent=mock_agent,
            context={},
            state={},
            memory={}
        )
        
        # Verify
        assert result == "valid output"
        assert mock_agent.run.call_count == 2

    def test_retry_on_exception(self):
        """Test that agent runner propagates exception immediately when agent raises an exception (no retry)."""
        runner = AgentRunner()
        mock_agent = Mock()
        # First call raises exception, should not retry
        mock_agent.run.side_effect = Exception("temporary failure")

        with pytest.raises(Exception) as exc_info:
            runner.run_agent(
                agent_id="test_agent",
                agent=mock_agent,
                context={},
                state={},
                memory={}
            )
        assert "temporary failure" in str(exc_info.value)
        assert mock_agent.run.call_count == 1

    def test_max_attempts_exceeded_with_empty_output(self):
        """Test that agent runner raises exception after max attempts with empty output."""
        # Setup
        runner = AgentRunner()
        mock_agent = Mock()
        mock_agent.run.return_value = None  # Always returns empty
        
        # Execute and verify exception
        with pytest.raises(Exception) as exc_info:
            runner.run_agent(
                agent_id="test_agent",
                agent=mock_agent,
                context={},
                state={},
                memory={},
                max_attempts=2
            )
        
        assert "Failed to get valid response from test_agent" in str(exc_info.value)
        assert mock_agent.run.call_count == 2

    def test_max_attempts_exceeded_with_exception(self):
        """Test that agent runner propagates exception after first attempt (no retry on exception)."""
        runner = AgentRunner()
        mock_agent = Mock()
        test_exception = Exception("persistent failure")
        mock_agent.run.side_effect = test_exception

        with pytest.raises(Exception) as exc_info:
            runner.run_agent(
                agent_id="test_agent",
                agent=mock_agent,
                context={},
                state={},
                memory={},
                max_attempts=2
            )
        assert exc_info.value is test_exception
        assert mock_agent.run.call_count == 1

    def test_custom_max_attempts(self):
        """Test that custom max_attempts parameter is respected."""
        # Setup
        runner = AgentRunner()
        mock_agent = Mock()
        mock_agent.run.return_value = None  # Always returns empty
        
        # Execute and verify exception
        with pytest.raises(Exception):
            runner.run_agent(
                agent_id="test_agent",
                agent=mock_agent,
                context={},
                state={},
                memory={},
                max_attempts=5
            )
        
        assert mock_agent.run.call_count == 5

    @patch('agentforge.core.agent_runner.Logger')
    def test_logging_behavior(self, mock_logger_class):
        """Test that AgentRunner creates its own logger and logs appropriately (debug/warning/error)."""
        mock_logger = Mock()
        mock_logger_class.return_value = mock_logger

        runner = AgentRunner()
        mock_agent = Mock()
        mock_agent.run.return_value = "test output"

        mock_logger_class.assert_called_once_with("AgentRunner", "agent_runner")

        runner.run_agent(
            agent_id="test_agent",
            agent=mock_agent,
            context={},
            state={},
            memory={}
        )

        # Check that debug was called for execution start and success
        debug_calls = [call for call in mock_logger.debug.call_args_list]
        assert len(debug_calls) >= 2
        # No longer check for .log, but for .debug/.warning/.error 