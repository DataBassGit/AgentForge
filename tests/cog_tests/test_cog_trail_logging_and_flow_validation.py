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
        assert not cog.enable_trail_logging, "Trail logging should be False from YAML config"

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
        assert not cog.enable_trail_logging, "Constructor override should set trail_logging to False"

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
        assert cog.enable_trail_logging, "Trail logging should default to True when not specified"

    def test_flow_validation_warns_on_missing_end_state(self, isolated_config, monkeypatch):
        """Test that a warning is issued when cog flow has no end state."""
        # Track warning calls
        warning_calls = []
        
        # Mock the logger's log method to capture calls
        def mock_log(msg, level=None, tag=None):
            if level == "warning":
                warning_calls.append(msg)
        
        # Create a config without end state - should warn but not fail
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
        
        cog_path = Path(isolated_config.project_root) / ".agentforge" / "cogs" / "NoEndCog.yaml"
        with open(cog_path, 'w') as f:
            yaml.dump(no_end_config, f)
        
        # Create template
        template_config = {
            "prompts": {"system": "Test system prompt", "user": "Test user prompt"},
            "settings": {"system": {"debug": {"mode": True}}}
        }
        template_path = Path(isolated_config.project_root) / ".agentforge" / "prompts" / "test_template.yaml"
        with open(template_path, 'w') as f:
            yaml.dump(template_config, f)
        
        # Reload configuration after writing new files
        isolated_config.load_all_configurations()
        
        # Create cog instance and patch its logger's log method
        cog = Cog("NoEndCog")
        monkeypatch.setattr(cog.logger, 'log', mock_log)
        
        # Re-run validation to trigger the warning
        cog._validate_flow()
        
        # Check that warning was called with the expected message
        assert any("Flow has no 'end:' transition; cog may loop forever." in call for call in warning_calls)

    def test_flow_validation_no_warning_with_valid_end_state(self, isolated_config, monkeypatch):
        """Test that flows with valid end states don't generate warnings."""
        # Track warning calls
        warning_calls = []
        
        # Mock the logger's log method to capture calls
        def mock_log(msg, level=None, tag=None):
            if level == "warning":
                warning_calls.append(msg)
        
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
        
        cog_path = Path(isolated_config.project_root) / ".agentforge" / "cogs" / "ValidEndStateCog.yaml"
        with open(cog_path, 'w') as f:
            yaml.dump(good_config, f)
        
        # Create minimal template
        template_config = {
            "prompts": {"system": "Test system prompt", "user": "Test user prompt"},
            "settings": {"system": {"debug": {"mode": True}}}
        }
        template_path = Path(isolated_config.project_root) / ".agentforge" / "prompts" / "test_template.yaml"
        with open(template_path, 'w') as f:
            yaml.dump(template_config, f)
        
        isolated_config.load_all_configurations()
        
        # Create cog instance and patch its logger's log method
        cog = Cog("ValidEndStateCog")
        monkeypatch.setattr(cog.logger, 'log', mock_log)
        
        # Re-run validation to ensure no warning is triggered
        cog._validate_flow()
        
        # Should not have any warnings about missing end state
        assert not any("Flow has no 'end:' transition; cog may loop forever." in call for call in warning_calls)

    def test_flow_validation_allows_cycles_with_warning(self, isolated_config, monkeypatch):
        """Test that complex flows with cycles are allowed but warn if no end state exists."""
        # Track warning calls
        warning_calls = []
        
        # Mock the logger's log method to capture calls
        def mock_log(msg, level=None, tag=None):
            if level == "warning":
                warning_calls.append(msg)
        
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
        
        cog_path = Path(isolated_config.project_root) / ".agentforge" / "cogs" / "CycleTestCog.yaml"
        with open(cog_path, 'w') as f:
            yaml.dump(cog_config, f)
        
        # Create minimal template
        template_config = {
            "prompts": {"system": "Test system prompt", "user": "Test user prompt"},
            "settings": {"system": {"debug": {"mode": True}}}
        }
        template_path = Path(isolated_config.project_root) / ".agentforge" / "prompts" / "test_template.yaml"
        with open(template_path, 'w') as f:
            yaml.dump(template_config, f)
        
        isolated_config.load_all_configurations()
        
        # Create cog instance and patch its logger's log method
        cog = Cog("CycleTestCog")
        monkeypatch.setattr(cog.logger, 'log', mock_log)
        
        # Re-run validation to trigger the warning
        cog._validate_flow()
        
        # Check that warning was called with the expected message
        assert any("Flow has no 'end:' transition; cog may loop forever." in call for call in warning_calls) 