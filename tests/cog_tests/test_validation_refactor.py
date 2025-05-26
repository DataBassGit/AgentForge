"""
Test the simplified validation refactor (warning instead of error).
"""

import pytest
import yaml
from pathlib import Path

from agentforge.cog import Cog


class TestValidationRefactor:
    """Test suite focused specifically on the validation refactor."""

    def test_no_end_state_warning(self, isolated_config, monkeypatch):
        """Test that a warning is issued when no end state is present."""
        # Track warning calls
        warning_calls = []
        
        # Mock the logger's log method to capture calls
        def mock_log(msg, level=None, tag=None):
            if level == "warning":
                warning_calls.append(msg)
        
        cog_config = {
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
        
        cog_path = Path(isolated_config.project_root) / ".agentforge" / "cogs" / "NoEndStateCog.yaml"
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
        cog = Cog("NoEndStateCog")
        monkeypatch.setattr(cog.logger, 'log', mock_log)
        
        # Re-run validation to trigger the warning
        cog._validate_flow()
        
        # Check that warning was called with the expected message
        assert any("Flow has no 'end:' transition; cog may loop forever." in call for call in warning_calls)

    def test_valid_end_state_no_warning(self, isolated_config, monkeypatch):
        """Test that flows with valid end states don't generate warnings."""
        # Track warning calls
        warning_calls = []
        
        # Mock the logger's log method to capture calls
        def mock_log(msg, level=None, tag=None):
            if level == "warning":
                warning_calls.append(msg)
        
        cog_config = {
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
        cog = Cog("ValidEndStateCog")
        monkeypatch.setattr(cog.logger, 'log', mock_log)
        
        # Re-run validation to ensure no warning is triggered
        cog._validate_flow()
        
        # Should not have any warnings about missing end state
        assert not any("Flow has no 'end:' transition; cog may loop forever." in call for call in warning_calls)

    def test_cycles_allowed_with_warning(self, isolated_config, monkeypatch):
        """Test that cycles are allowed, but a warning is issued if no end state exists."""
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