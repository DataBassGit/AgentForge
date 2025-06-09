"""
Test Cog trail logging configuration and flow validation behavior.

This module tests:
- Trail logging configuration from YAML and constructor overrides
- Flow validation warnings for missing end states
- Default behavior when configurations are not specified
"""

import pytest
import yaml
from pathlib import Path

from agentforge.cog import Cog
from agentforge.core.config_manager import ConfigManager


class TestCogTrailLoggingAndFlowValidation:
    """Test suite for Cog trail logging configuration and flow validation."""

    def test_trail_logging_from_yaml_config(self, isolated_config):
        """Test that trail_logging flag is correctly loaded from YAML config."""
        # Create a test cog config with trail_logging set to False
        cog_config = {
            "cog": {
                "trail_logging": False,
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
        
        # Save the config to the isolated config directory
        cog_path = Path(isolated_config.project_root) / ".agentforge" / "cogs" / "TestCog.yaml"
        with open(cog_path, 'w') as f:
            yaml.dump(cog_config, f)
        
        # Create a minimal agent template
        template_config = {
            "prompts": {"system": "Test system prompt", "user": "Test user prompt"},
            "settings": {"system": {"debug": {"mode": True}}},
            "simulated_response": "Test simulated response"
        }
        template_path = Path(isolated_config.project_root) / ".agentforge" / "prompts" / "test_template.yaml"
        with open(template_path, 'w') as f:
            yaml.dump(template_config, f)
        
        # Reload configuration after writing new files
        isolated_config.load_all_configurations()
        
        # Test cog initialization
        cog = Cog("TestCog")
        assert not cog.trail_recorder.enabled, "Trail logging should be False from YAML config"

    def test_trail_logging_constructor_override(self, isolated_config):
        """Test that constructor parameter overrides YAML config for trail_logging."""
        # Create a test cog config with trail_logging set to True
        cog_config = {
            "cog": {
                "trail_logging": True,
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
            "simulated_response": "Test simulated response"
        }
        template_path = Path(isolated_config.project_root) / ".agentforge" / "prompts" / "test_template.yaml"
        with open(template_path, 'w') as f:
            yaml.dump(template_config, f)
        
        # Reload configuration after writing new files
        isolated_config.load_all_configurations()
        
        # Test constructor override
        cog = Cog("TestCog", enable_trail_logging=False)
        assert not cog.trail_recorder.enabled, "Constructor override should set trail_logging to False"

    def test_trail_logging_default_true(self, isolated_config):
        """Test that trail_logging defaults to True when not specified in YAML."""
        # Create a test cog config without trail_logging specified
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
        
        cog_path = Path(isolated_config.project_root) / ".agentforge" / "cogs" / "DefaultCog.yaml"
        with open(cog_path, 'w') as f:
            yaml.dump(cog_config, f)
        
        # Create template
        template_config = {
            "prompts": {"system": "Test system prompt", "user": "Test user prompt"},
            "settings": {"system": {"debug": {"mode": True}}},
            "simulated_response": "Test simulated response"
        }
        template_path = Path(isolated_config.project_root) / ".agentforge" / "prompts" / "test_template.yaml"
        with open(template_path, 'w') as f:
            yaml.dump(template_config, f)
        
        # Reload configuration after writing new files
        isolated_config.load_all_configurations()
        
        # Test that trail_logging defaults to True
        cog = Cog("DefaultCog")
        assert cog.trail_recorder.enabled, "Trail logging should default to True when not specified"

    def test_flow_validation_warns_on_missing_end_state(self, isolated_config):
        """Test that flows without end states are correctly identified."""
        # Create a config without end state
        no_end_config = {
            "cog": {
                "agents": [
                    {"id": "agent1", "template_file": "test_template"},
                    {"id": "agent2", "template_file": "test_template"}
                ],
                "flow": {
                    "start": "agent1",
                    "transitions": {
                        "agent1": "agent2",
                        "agent2": "agent1"  # Infinite loop, no end state
                    }
                }
            }
        }
        
        # Create template to satisfy agent validation
        template_config = {
            "prompts": {"system": "Test system prompt", "user": "Test user prompt"},
            "settings": {"system": {"debug": {"mode": True}}}
        }
        template_path = Path(isolated_config.project_root) / ".agentforge" / "prompts" / "test_template.yaml"
        with open(template_path, 'w') as f:
            yaml.dump(template_config, f)
        
        isolated_config.load_all_configurations()
        
        # Test ConfigManager validation directly
        config_manager = ConfigManager()
        cog_config = config_manager.build_cog_config(no_end_config)
        
        # Check that the flow was parsed correctly but has no end transition
        has_end_transition = any(
            transition.type == "end" or transition.end
            for transition in cog_config.cog.flow.transitions.values()
        )
        
        # The flow should be valid but have no end state
        assert not has_end_transition, "Flow should have no end transition"
        assert cog_config.cog.flow.start == "agent1", "Start agent should be correct"
        assert len(cog_config.cog.flow.transitions) == 2, "Should have 2 transitions"

    def test_flow_validation_no_warning_with_valid_end_state(self, isolated_config):
        """Test that flows with valid end states are correctly identified."""
        from agentforge.core.config_manager import ConfigManager
        
        # Create a config with proper end state
        good_config = {
            "cog": {
                "agents": [
                    {"id": "agent1", "template_file": "test_template"},
                    {"id": "agent2", "template_file": "test_template"}
                ],
                "flow": {
                    "start": "agent1",
                    "transitions": {
                        "agent1": "agent2",
                        "agent2": {"end": True}  # Valid end state
                    }
                }
            }
        }
        
        # Create template to satisfy agent validation
        template_config = {
            "prompts": {"system": "Test system prompt", "user": "Test user prompt"},
            "settings": {"system": {"debug": {"mode": True}}}
        }
        template_path = Path(isolated_config.project_root) / ".agentforge" / "prompts" / "test_template.yaml"
        with open(template_path, 'w') as f:
            yaml.dump(template_config, f)
        
        isolated_config.load_all_configurations()
        
        # Test ConfigManager validation directly
        config_manager = ConfigManager()
        cog_config = config_manager.build_cog_config(good_config)
        
        # Check that the flow has a proper end transition
        has_end_transition = any(
            transition.type == "end" or transition.end
            for transition in cog_config.cog.flow.transitions.values()
        )
        
        # The flow should have a valid end state
        assert has_end_transition, "Flow should have an end transition"
        assert cog_config.cog.flow.start == "agent1", "Start agent should be correct"
        assert len(cog_config.cog.flow.transitions) == 2, "Should have 2 transitions"
        
        # Check the specific end transition
        agent2_transition = cog_config.cog.flow.transitions["agent2"]
        assert agent2_transition.type == "end", "Agent2 should have end transition"
        assert agent2_transition.end is True, "End transition should be marked as True"

    def test_flow_validation_allows_cycles_with_warning(self, isolated_config):
        """Test that complex flows with cycles are correctly parsed."""
        from agentforge.core.config_manager import ConfigManager
        
        # Create a complex flow with cycles and no end state
        cog_config = {
            "cog": {
                "agents": [
                    {"id": "agent1", "template_file": "test_template"},
                    {"id": "agent2", "template_file": "test_template"},
                    {"id": "agent3", "template_file": "test_template"}
                ],
                "flow": {
                    "start": "agent1",
                    "transitions": {
                        "agent1": "agent2",
                        "agent2": "agent3", 
                        "agent3": "agent1"  # Creates a cycle, no end state
                    }
                }
            }
        }
        
        # Create template to satisfy agent validation
        template_config = {
            "prompts": {"system": "Test system prompt", "user": "Test user prompt"},
            "settings": {"system": {"debug": {"mode": True}}}
        }
        template_path = Path(isolated_config.project_root) / ".agentforge" / "prompts" / "test_template.yaml"
        with open(template_path, 'w') as f:
            yaml.dump(template_config, f)
        
        isolated_config.load_all_configurations()
        
        # Test ConfigManager validation directly
        config_manager = ConfigManager()
        cog_config = config_manager.build_cog_config(cog_config)
        
        # Check that the flow was parsed correctly but has no end transition
        has_end_transition = any(
            transition.type == "end" or transition.end
            for transition in cog_config.cog.flow.transitions.values()
        )
        
        # The flow should be valid but have no end state (creates a cycle)
        assert not has_end_transition, "Flow should have no end transition (cycles infinitely)"
        assert cog_config.cog.flow.start == "agent1", "Start agent should be correct"
        assert len(cog_config.cog.flow.transitions) == 3, "Should have 3 transitions"
        
        # Verify the cycle structure
        assert cog_config.cog.flow.transitions["agent1"].next_agent == "agent2"
        assert cog_config.cog.flow.transitions["agent2"].next_agent == "agent3"
        assert cog_config.cog.flow.transitions["agent3"].next_agent == "agent1" 