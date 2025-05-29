"""
Test the flexible config loading functionality that preserves additional YAML fields.
"""

import pytest
from pathlib import Path
from unittest.mock import patch


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
    
    # Load agent data (now returns structured AgentConfig object)
    agent_config = isolated_config.load_agent_data("TestFlexibleAgent")
    
    # Verify core fields are present (these should never be overwritten)
    assert agent_config.name == "TestFlexibleAgent"
    assert agent_config.model is not None
    assert agent_config.settings is not None
    assert agent_config.params is not None
    assert agent_config.prompts is not None
    
    # Verify additional fields are preserved
    assert agent_config.parse_response_as == "json"
    assert "custom_field" in agent_config.custom_fields
    assert agent_config.custom_fields["custom_field"] == "test_value"
    assert "another_flag" in agent_config.custom_fields
    assert agent_config.custom_fields["another_flag"] is True
    assert "numeric_field" in agent_config.custom_fields
    assert agent_config.custom_fields["numeric_field"] == 42
    assert "nested_field" in agent_config.custom_fields
    assert agent_config.custom_fields["nested_field"]["sub_field"] == "nested_value"
    assert "list_field" in agent_config.custom_fields
    assert agent_config.custom_fields["list_field"] == ["item1", "item2", "item3"]


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
    
    # Load agent data (now returns structured AgentConfig object)
    agent_config = isolated_config.load_agent_data("TestCoreOverride")
    
    # Verify core fields are correctly derived, not from YAML
    assert agent_config.name == "TestCoreOverride"  # Should be agent name, not YAML value
    assert isinstance(agent_config.settings.system, object)  # Should be proper Settings object, not YAML dict
    assert agent_config.model is not None  # Should be instantiated model object, not string
    assert isinstance(agent_config.params, dict)  # Should be resolved params, not YAML value
    
    # Verify non-reserved fields are preserved
    assert "custom_field" in agent_config.custom_fields
    assert agent_config.custom_fields["custom_field"] == "preserved_value"
    assert agent_config.parse_response_as == "json"


def test_agent_parse_response_field_integration(isolated_config):
    """Test that agents can use the parse_response_as field for output parsing."""
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
    
    # Verify the agent can see the parse_response_as field through structured config
    assert agent.agent_config.parse_response_as == "yaml"
    assert "custom_setting" in agent.agent_config.custom_fields
    assert agent.agent_config.custom_fields["custom_setting"] == "test_value"
    
    # Verify the field works correctly for parsing
    agent.result = "test: value\nfoo: bar"
    
    # Mock parsing processor to avoid actual YAML parsing complexity in test
    with patch.object(agent.parsing_processor, 'parse_by_format', return_value={"test": "value", "foo": "bar"}) as mock_parse:
        agent.parse_result()
        
        # Should have called parse_by_format with the correct format
        mock_parse.assert_called_once_with(agent.result, "yaml")
        
        # Should have parsed result
        assert agent.parsed_result == {"test": "value", "foo": "bar"} 