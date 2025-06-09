"""
Test TrailRecorder and ThoughtTrailEntry functionality.

This module tests the new trail recording system to ensure:
- ThoughtTrailEntry dataclass works correctly
- TrailRecorder properly tracks execution
- Timestamps and execution order are recorded
- Error handling works as expected
"""

import pytest
import yaml
from pathlib import Path
from datetime import datetime

from agentforge.cog import Cog
from agentforge.core.trail_recorder import TrailRecorder
from agentforge.config_structs.trail_structs import ThoughtTrailEntry


class TestTrailRecorderFunctionality:
    """Test suite for TrailRecorder and ThoughtTrailEntry functionality."""

    def test_thought_trail_entry_auto_timestamps(self):
        """Test that ThoughtTrailEntry automatically generates timestamps."""
        before_creation = datetime.now()
        
        entry = ThoughtTrailEntry(agent_id="test_agent", output="test_output")
        
        after_creation = datetime.now()
        
        # Verify timestamps were auto-generated
        assert entry.timestamp is not None
        assert entry.unix_timestamp is not None
        
        # Verify timestamps are reasonable (within the test execution window)
        assert before_creation <= entry.timestamp <= after_creation
        assert before_creation.timestamp() <= entry.unix_timestamp <= after_creation.timestamp()
        
        # Verify timestamp consistency
        assert abs(entry.timestamp.timestamp() - entry.unix_timestamp) < 0.001  # Within 1ms

    def test_thought_trail_entry_optional_fields(self):
        """Test ThoughtTrailEntry with all optional fields."""
        entry = ThoughtTrailEntry(
            agent_id="test_agent",
            output="test_output",
            notes="Test notes",
            execution_order=5,
            error="Test error"
        )
        
        assert entry.agent_id == "test_agent"
        assert entry.output == "test_output" 
        assert entry.notes == "Test notes"
        assert entry.execution_order == 5
        assert entry.error == "Test error"
        assert entry.timestamp is not None
        assert entry.unix_timestamp is not None

    def test_trail_recorder_basic_functionality(self):
        """Test basic TrailRecorder functionality."""
        recorder = TrailRecorder(enabled=True)
        
        # Record some outputs
        recorder.record_agent_output("agent1", "output1")
        recorder.record_agent_output("agent2", "output2", notes="Special note")
        
        trail = recorder.get_trail()
        
        # Verify trail structure
        assert len(trail) == 2
        
        # Verify first entry
        entry1 = trail[0]
        assert entry1.agent_id == "agent1"
        assert entry1.output == "output1"
        assert entry1.execution_order == 1
        assert entry1.notes is None
        assert entry1.error is None
        
        # Verify second entry
        entry2 = trail[1]
        assert entry2.agent_id == "agent2"
        assert entry2.output == "output2"
        assert entry2.execution_order == 2
        assert entry2.notes == "Special note"
        assert entry2.error is None
        
        # Verify execution order
        assert entry1.timestamp <= entry2.timestamp

    def test_trail_recorder_disabled(self):
        """Test that disabled TrailRecorder doesn't record anything."""
        recorder = TrailRecorder(enabled=False)
        
        recorder.record_agent_output("agent1", "output1")
        trail = recorder.get_trail()
        
        assert len(trail) == 0

    def test_trail_recorder_reset(self):
        """Test TrailRecorder reset functionality."""
        recorder = TrailRecorder(enabled=True)
        
        # Record some outputs
        recorder.record_agent_output("agent1", "output1")
        recorder.record_agent_output("agent2", "output2")
        
        assert len(recorder.get_trail()) == 2
        
        # Reset and verify
        recorder.reset_trail()
        assert len(recorder.get_trail()) == 0
        
        # Verify execution counter reset
        recorder.record_agent_output("agent3", "output3")
        trail = recorder.get_trail()
        assert len(trail) == 1
        assert trail[0].execution_order == 1  # Should start from 1 again

    def test_cog_trail_integration(self, isolated_config):
        """Test that Cog properly integrates with TrailRecorder."""
        # Create a test cog config
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
        cog_path = Path(isolated_config.project_root) / ".agentforge" / "cogs" / "TrailTestCog.yaml"
        with open(cog_path, 'w') as f:
            yaml.dump(cog_config, f)
        
        # Create minimal agent template
        template_config = {
            "prompts": {"system": "Test system prompt", "user": "Test user prompt"},
            "settings": {"system": {"debug": {"mode": True}}},
            "simulated_response": "Test simulated response"
        }
        template_path = Path(isolated_config.project_root) / ".agentforge" / "prompts" / "test_template.yaml"
        with open(template_path, 'w') as f:
            yaml.dump(template_config, f)
        
        # Reload configuration
        isolated_config.load_all_configurations()
        
        # Test cog execution and trail
        cog = Cog("TrailTestCog")
        result = cog.run(test_input="Hello")
        
        # Verify trail was recorded
        trail = cog.get_track_flow_trail()
        assert len(trail) == 1
        
        entry = trail[0]
        assert isinstance(entry, ThoughtTrailEntry)
        assert entry.agent_id == "test_agent"
        assert entry.output is not None  # Just verify output exists, don't check specific content
        assert entry.execution_order == 1
        assert entry.timestamp is not None
        assert entry.unix_timestamp is not None
        
        # Verify cog result exists (don't check specific content)
        assert result is not None 