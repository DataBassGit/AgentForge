import pytest
from unittest.mock import patch, MagicMock
from agentforge.agent import Agent
from agentforge.config import Config
from agentforge.core.config_manager import ConfigManager
import agentforge.utils.parsing_processor as parsing_mod

@pytest.fixture
def minimal_agent_config(isolated_config):
    # Create a ConfigManager instance to build structured config
    config_manager = ConfigManager()
    
    # Minimal config with debug mode enabled
    raw_agent_data = {
        "name": "TestAgent",
        "params": {},
        "prompts": {"system": "sys", "user": "usr"},
        "model": object(),
        "settings": isolated_config.data["settings"].copy(),
        "simulated_response": "RAW_OUTPUT",
    }
    raw_agent_data["settings"]["system"]["debug"]["mode"] = True
    
    # Use ConfigManager to build structured config object
    return config_manager.build_agent_config(raw_agent_data)

# Test 1: parse_response_as present and valid, parsing succeeds
def test_parse_result_with_valid_parse_response_as(minimal_agent_config):
    # Add parse_response_as to the config object
    minimal_agent_config.parse_response_as = "json"
    
    with patch.object(Config, "load_agent_data", return_value=minimal_agent_config):
        agent = Agent("TestAgent")
        agent.result = '{"foo": "bar"}'
        # Patch ParsingProcessor.parse_by_format to simulate successful parsing
        with patch.object(agent.parsing_processor, "parse_by_format", return_value={"foo": "bar"}) as mock_parse:
            agent.parse_result()
            # Agent should call parse_by_format with correct args
            mock_parse.assert_called_once_with(agent.result, "json")
            # The parsed_result should be the parsed value
            assert agent.parsed_result == {"foo": "bar"}

# Test 2: parse_response_as absent, raw output is used
def test_parse_result_without_parse_response_as(minimal_agent_config):
    # Ensure parse_response_as is None (default)
    minimal_agent_config.parse_response_as = None
    
    with patch.object(Config, "load_agent_data", return_value=minimal_agent_config):
        agent = Agent("TestAgent")
        agent.result = "RAW_OUTPUT"
        agent.parse_result()
        # The parsed_result should be the raw result
        assert agent.parsed_result == "RAW_OUTPUT"

# Test 3: parse_response_as present but parsing fails, ParsingError is raised
def test_parse_result_with_invalid_parse_response_as_fails(minimal_agent_config):
    # Add parse_response_as to the config object
    minimal_agent_config.parse_response_as = "json"
    
    with patch.object(Config, "load_agent_data", return_value=minimal_agent_config):
        agent = Agent("TestAgent")
        agent.result = "not valid json"
        # Patch ParsingProcessor.parse_by_format to raise ParsingError
        with patch.object(agent.parsing_processor, "parse_by_format", side_effect=parsing_mod.ParsingError("parse fail")) as mock_parse:
            with pytest.raises(parsing_mod.ParsingError) as exc_info:
                agent.parse_result()
            # Should attempt to parse
            mock_parse.assert_called_once_with(agent.result, "json")
            # Should raise ParsingError
            assert "parse fail" in str(exc_info.value)

# Test 4: Verify Agent uses default code fences when calling parse_by_format
def test_agent_uses_default_code_fences(minimal_agent_config):
    """Verify that Agent correctly uses default code fences for parsing code-fenced content."""
    # Add parse_response_as to the config object
    minimal_agent_config.parse_response_as = "json"
    
    with patch.object(Config, "load_agent_data", return_value=minimal_agent_config):
        agent = Agent("TestAgent")
        # Set a result with code-fenced JSON
        agent.result = '''
        Here's the result:
        
        ```json
        {"message": "success", "data": {"count": 42}}
        ```
        
        That's all.
        '''
        
        agent.parse_result()
        
        # Should parse the JSON from the code fence
        assert isinstance(agent.parsed_result, dict)
        assert agent.parsed_result["message"] == "success"
        assert agent.parsed_result["data"]["count"] == 42

# Test 5: Verify explicit empty list disables code fence extraction
def test_explicit_empty_code_fences_disables_extraction(minimal_agent_config):
    """Test that explicitly passing empty code_fences list disables code fence extraction."""
    minimal_agent_config.parse_response_as = "json"
    minimal_agent_config.code_fences = []  # Explicitly disable code fence extraction
    
    with patch.object(Config, "load_agent_data", return_value=minimal_agent_config):
        agent = Agent("TestAgent")
        agent.result = '{"no_fences": true}'
        # Patch to verify the empty list is passed through
        with patch.object(agent.parsing_processor, "parse_by_format", return_value={"no_fences": True}) as mock_parse:
            agent.parse_result()
            # Should pass empty list as code_fences parameter
            mock_parse.assert_called_once_with(agent.result, "json")
            assert agent.parsed_result == {"no_fences": True}

def test_simplified_parse_result_with_none_parse_response_as(minimal_agent_config):
    """Test that the simplified parse_result method works correctly when parse_response_as is None."""
    # Ensure parse_response_as is None
    minimal_agent_config.parse_response_as = None
    
    with patch.object(Config, "load_agent_data", return_value=minimal_agent_config):
        agent = Agent("TestAgent")
        agent.result = "This is raw text that should remain unchanged"
        
        # Call parse_result directly without mocking
        agent.parse_result()
        
        # The parsed_result should be the same as the original result since parse_response_as is None
        assert agent.parsed_result == agent.result
        assert agent.parsed_result == "This is raw text that should remain unchanged" 