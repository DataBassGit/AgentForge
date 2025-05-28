"""
Test the flexible config loading functionality that preserves additional YAML fields.
"""

import pytest
from pathlib import Path


def test_flexible_config_preserves_additional_fields(isolated_config):
    """Test that additional YAML fields are preserved in agent_data."""
    
    # Create a test agent YAML with additional fields
    test_agent_path = Path(isolated_config.config_path) / "prompts" / "TestFlexibleAgent.yaml"
    
    agent_content = """
prompts:
  system: "You are a helpful assistant."
  user: "Please respond to: {user_input}"

parse_response_as: "json"
custom_field: "test_value"
another_flag: true
numeric_field: 42
nested_field:
  sub_field: "nested_value"
  sub_number: 123
list_field:
  - "item1"
  - "item2"
  - "item3"
"""
    
    test_agent_path.write_text(agent_content)
    
    # Reload configurations to pick up the new file
    isolated_config.load_all_configurations()
    
    # Load agent data
    agent_data = isolated_config.load_agent_data("TestFlexibleAgent")
    
    # Verify core fields are present (these should never be overwritten)
    assert agent_data["name"] == "TestFlexibleAgent"
    assert "settings" in agent_data
    assert "model" in agent_data
    assert "params" in agent_data
    assert "prompts" in agent_data
    assert "simulated_response" in agent_data
    assert "persona" in agent_data
    
    # Verify additional fields are preserved
    assert agent_data["parse_response_as"] == "json"
    assert agent_data["custom_field"] == "test_value"
    assert agent_data["another_flag"] is True
    assert agent_data["numeric_field"] == 42
    assert agent_data["nested_field"]["sub_field"] == "nested_value"
    assert agent_data["nested_field"]["sub_number"] == 123
    assert agent_data["list_field"] == ["item1", "item2", "item3"]


def test_core_fields_not_overwritten_by_yaml(isolated_config):
    """Test that core fields from YAML don't overwrite derived fields."""
    
    # Create a test agent YAML that tries to override core fields
    test_agent_path = Path(isolated_config.config_path) / "prompts" / "TestCoreOverride.yaml"
    
    agent_content = """
prompts:
  system: "You are a helpful assistant."
  user: "Please respond to: {user_input}"

# These should NOT override the derived values (reserved fields)
name: "WrongName"
settings: {"wrong": "settings"}
model: "WrongModel"
params: {"wrong": "params"}
persona: {"wrong": "persona"}
model_overrides: {"wrong": "overrides"}

# These should be preserved (non-reserved fields)
custom_field: "preserved_value"
parse_response_as: "json"
"""
    
    test_agent_path.write_text(agent_content)
    
    # Reload configurations to pick up the new file
    isolated_config.load_all_configurations()
    
    # Load agent data
    agent_data = isolated_config.load_agent_data("TestCoreOverride")
    
    # Verify core fields are correctly derived, not from YAML
    assert agent_data["name"] == "TestCoreOverride"  # Should be agent name, not YAML value
    assert isinstance(agent_data["settings"], dict)  # Should be system settings
    assert agent_data["settings"] != {"wrong": "settings"}
    
    # The model should be a proper model instance, not a string
    assert hasattr(agent_data["model"], "__class__")
    assert agent_data["model"] != "WrongModel"
    
    # Reserved fields should not appear in agent_data even if they were in the YAML
    assert "WrongName" not in str(agent_data["name"])  # name should be derived correctly
    assert agent_data["params"] != {"wrong": "params"}  # params should be derived correctly
    
    # Non-reserved fields should still be preserved
    assert agent_data["custom_field"] == "preserved_value"
    assert agent_data["parse_response_as"] == "json"


def test_agent_can_use_parse_response_as_field(isolated_config):
    """Test that an Agent instance can access and use the parse_response_as field."""
    from agentforge.agent import Agent
    from unittest.mock import patch
    
    # Create a test agent YAML with parse_response_as
    test_agent_path = Path(isolated_config.config_path) / "prompts" / "TestParseAgent.yaml"
    
    agent_content = """
prompts:
  system: "You are a helpful assistant."
  user: "Please respond to: {user_input}"

parse_response_as: "yaml"
custom_setting: "test_value"
"""
    
    test_agent_path.write_text(agent_content)
    
    # Reload configurations to pick up the new file
    isolated_config.load_all_configurations()
    
    # Create an agent instance
    agent = Agent("TestParseAgent")
    
    # Verify the agent can see the parse_response_as field
    assert agent.agent_data["parse_response_as"] == "yaml"
    assert agent.agent_data["custom_setting"] == "test_value"
    
    # Test that parse_result method uses the field correctly
    agent.result = '{"test": "data"}'
    
    # Mock the parsing processor to verify it gets called with the right format
    with patch.object(agent.parsing_processor, "parse_by_format", return_value={"parsed": "data"}) as mock_parse:
        agent.parse_result()
        mock_parse.assert_called_once_with('{"test": "data"}', "yaml")
        assert agent.parsed_result == {"parsed": "data"}


def test_legacy_response_format_field_backward_compatibility(isolated_config):
    """Test that the old response_format field name still works (if someone hasn't migrated yet)."""
    from agentforge.agent import Agent
    from unittest.mock import patch
    
    # Create a test agent YAML with the old field name (for backward compatibility testing)
    test_agent_path = Path(isolated_config.config_path) / "prompts" / "TestLegacyAgent.yaml"
    
    agent_content = """
prompts:
  system: "You are a helpful assistant."
  user: "Please respond to: {user_input}"

response_format: "json"
"""
    
    test_agent_path.write_text(agent_content)
    
    # Reload configurations to pick up the new file
    isolated_config.load_all_configurations()
    
    # Create an agent instance
    agent = Agent("TestLegacyAgent")
    
    # Verify the agent can see the legacy field
    assert agent.agent_data["response_format"] == "json"
    
    # The new code should look for parse_response_as, so this shouldn't be used
    agent.result = '{"test": "data"}'
    
    # Mock the parsing processor - it should NOT be called since we look for parse_response_as
    with patch.object(agent.parsing_processor, "parse_by_format") as mock_parse:
        agent.parse_result()
        mock_parse.assert_not_called()
        # Result should remain unparsed
        assert agent.parsed_result == '{"test": "data"}' 