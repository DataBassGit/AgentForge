"""
Tests for Cog and AgentRunner integration.

This module ensures that the refactored Cog properly delegates agent execution 
to AgentRunner while maintaining the same external behavior.
"""

import pytest
import yaml
from pathlib import Path
from unittest.mock import Mock, patch

from agentforge.cog import Cog


class TestCogAgentRunnerIntegration:
    """Test suite for Cog and AgentRunner integration."""

    def test_cog_uses_agent_runner_for_execution(self, isolated_config):
        """Test that Cog delegates agent execution to AgentRunner."""
        # Create a test cog config
        cog_config = {
            "cog": {
                "agents": [
                    {"id": "test_agent", "template_file": "test_template"}
                ],
                "flow": {
                    "start": "test_agent",
                    "transitions": {
                        "test_agent": {"end": True}
                    }
                }
            }
        }
        
        # Save the config
        cog_path = Path(isolated_config.project_root) / ".agentforge" / "cogs" / "TestCog.yaml"
        with open(cog_path, 'w') as f:
            yaml.dump(cog_config, f)
        
        # Create template
        template_config = {
            "prompts": {"system": "Test system prompt", "user": "Test user prompt"},
            "settings": {"system": {"debug": {"mode": True}}},
            "simulated_response": "Test response"
        }
        template_path = Path(isolated_config.project_root) / ".agentforge" / "prompts" / "test_template.yaml"
        with open(template_path, 'w') as f:
            yaml.dump(template_config, f)
        
        # Reload configuration
        isolated_config.load_all_configurations()
        
        # Create Cog and verify AgentRunner is initialized
        cog = Cog("TestCog")
        assert hasattr(cog, 'agent_runner')
        assert cog.agent_runner is not None
        
        # Mock the AgentRunner's run_agent method to verify it gets called
        with patch.object(cog.agent_runner, 'run_agent', return_value="mocked output") as mock_run_agent:
            result = cog.run(test_input="test value")
            
            # Verify AgentRunner was called
            mock_run_agent.assert_called_once()
            
            # Verify the call arguments
            call_args = mock_run_agent.call_args
            assert call_args[0][0] == "test_agent"  # agent_id
            assert call_args[0][2] == {"test_input": "test value"}  # context
            assert call_args[0][3] == {"test_agent": "mocked output"}  # state
            
            # Verify result
            assert result == "mocked output"

    def test_cog_agent_runner_preserves_retry_behavior(self, isolated_config):
        """Test that AgentRunner retry behavior is preserved when called from Cog."""
        # Create a test cog config
        cog_config = {
            "cog": {
                "agents": [
                    {"id": "flaky_agent", "template_file": "test_template"}
                ],
                "flow": {
                    "start": "flaky_agent",
                    "transitions": {
                        "flaky_agent": {"end": True}
                    }
                }
            }
        }
        
        # Save the config
        cog_path = Path(isolated_config.project_root) / ".agentforge" / "cogs" / "FlakyCog.yaml"
        with open(cog_path, 'w') as f:
            yaml.dump(cog_config, f)
        
        # Create template
        template_config = {
            "prompts": {"system": "Test system prompt", "user": "Test user prompt"},
            "settings": {"system": {"debug": {"mode": True}}},
            "simulated_response": "Success after retry"
        }
        template_path = Path(isolated_config.project_root) / ".agentforge" / "prompts" / "test_template.yaml"
        with open(template_path, 'w') as f:
            yaml.dump(template_config, f)
        
        # Reload configuration
        isolated_config.load_all_configurations()
        
        # Create Cog
        cog = Cog("FlakyCog")
        
        # Mock the agent to fail first, then succeed
        mock_agent = Mock()
        mock_agent.run.side_effect = [None, "Success after retry"]  # First call fails, second succeeds
        cog.agents["flaky_agent"] = mock_agent
        
        # Run the cog
        result = cog.run()
        
        # Verify the agent was called twice (due to retry)
        assert mock_agent.run.call_count == 2
        assert result == "Success after retry"

    def test_cog_preserves_memory_integration_with_agent_runner(self, isolated_config):
        """Test that memory integration still works properly with AgentRunner."""
        # Create a test cog config with memory
        cog_config = {
            "cog": {
                "agents": [
                    {"id": "memory_agent", "template_file": "test_template"}
                ],
                "memory": [
                    {
                        "id": "test_memory",
                        "type": "agentforge.storage.memory.Memory",
                        "query_before": ["memory_agent"],
                        "update_after": ["memory_agent"]
                    }
                ],
                "flow": {
                    "start": "memory_agent",
                    "transitions": {
                        "memory_agent": {"end": True}
                    }
                }
            }
        }
        
        # Save the config
        cog_path = Path(isolated_config.project_root) / ".agentforge" / "cogs" / "MemoryCog.yaml"
        with open(cog_path, 'w') as f:
            yaml.dump(cog_config, f)
        
        # Create template
        template_config = {
            "prompts": {"system": "Test system prompt", "user": "Test user prompt"},
            "settings": {"system": {"debug": {"mode": True}}},
            "simulated_response": "Memory test response"
        }
        template_path = Path(isolated_config.project_root) / ".agentforge" / "prompts" / "test_template.yaml"
        with open(template_path, 'w') as f:
            yaml.dump(template_config, f)
        
        # Reload configuration
        isolated_config.load_all_configurations()
        
        # Create Cog
        cog = Cog("MemoryCog")
        
        # Mock memory manager methods to verify they're called
        with patch.object(cog.mem_mgr, 'query_before') as mock_query, \
             patch.object(cog.mem_mgr, 'update_after') as mock_update:
            
            result = cog.run()
            
            # Verify memory methods were called with the correct agent_id
            mock_query.assert_called_once()
            mock_update.assert_called_once()
            
            # Check that the calls used the correct agent_id
            query_call_args = mock_query.call_args[0]
            update_call_args = mock_update.call_args[0]
            
            assert query_call_args[0] == "memory_agent"  # agent_id
            assert update_call_args[0] == "memory_agent"  # agent_id
            
            # Verify we got some result (the exact content doesn't matter for this test)
            assert result is not None 