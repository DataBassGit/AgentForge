"""
Test persona context data integration with agent template processing.

This module tests:
- Loading and integrating persona data into agent template context
- Enable/disable functionality for persona system
- Legacy persona format compatibility
- Template rendering with persona data
"""

import pytest
from unittest.mock import MagicMock, patch
import os
import tempfile
import yaml
from agentforge.agent import Agent
from agentforge.config import Config
from agentforge.core.config_manager import ConfigManager


@pytest.fixture
def test_persona_file():
    """Creates a temporary persona file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp:
        # Create a test persona with both static and retrieval blocks
        persona_data = {
            'static': {
                'name': 'Test Agent',
                'description': 'A test agent for unit tests',
                'goal': 'Test persona context data integration'
            },
            'retrieval': {
                'setting': 'Virtual test environment',
                'name': 'Override Name'  # Deliberately duplicate to test override
            }
        }
        yaml.dump(persona_data, tmp)
    
    yield tmp.name
    
    # Clean up
    os.unlink(tmp.name)


def test_persona_data_loading(isolated_config, test_persona_file):
    """Tests that persona data is properly loaded and added to template_data."""
    # Create a ConfigManager instance to build structured config
    config_manager = ConfigManager()
    
    # Setup
    persona_name = os.path.basename(test_persona_file).replace('.yaml', '')
    
    # Add the test persona to the Config data
    isolated_config.data['personas'] = {persona_name: yaml.safe_load(open(test_persona_file))}
    
    # Create raw agent data with personas enabled
    raw_agent_data = {
        'name': 'test_agent',
        'settings': isolated_config.data['settings'].copy(),
        'persona': isolated_config.data['personas'][persona_name],
        'prompts': {'system': 'Test prompt', 'user': 'Test user prompt'},
        'params': {},
        'model': object(),
        'simulated_response': 'test'
    }
    # Enable personas
    raw_agent_data['settings']['system']['persona']['enabled'] = True
    
    # Build structured config object
    agent_config = config_manager.build_agent_config(raw_agent_data)
    
    # Mock load_agent_data to return our structured config
    with patch.object(Config, 'load_agent_data', return_value=agent_config):
        agent = Agent('test_agent')
        
        # Assert that persona data is added directly to template_data
        assert 'persona' in agent.template_data
        assert agent.template_data['persona'] == raw_agent_data['persona']
        assert 'static' in agent.template_data['persona']
        assert 'retrieval' in agent.template_data['persona']
        
        # Verify the original structure is preserved
        assert agent.template_data['persona']['static']['name'] == 'Test Agent'
        assert agent.template_data['persona']['retrieval']['setting'] == 'Virtual test environment'


def test_persona_disabled(isolated_config, test_persona_file):
    """Tests that persona data is not loaded when personas are disabled."""
    # Create a ConfigManager instance to build structured config
    config_manager = ConfigManager()
    
    # Setup
    persona_name = os.path.basename(test_persona_file).replace('.yaml', '')
    
    # Add the test persona to the Config data
    isolated_config.data['personas'] = {persona_name: yaml.safe_load(open(test_persona_file))}
    
    # Create raw agent data with personas disabled
    raw_agent_data = {
        'name': 'test_agent',
        'settings': isolated_config.data['settings'].copy(),
        'persona': isolated_config.data['personas'][persona_name],
        'prompts': {'system': 'Test prompt', 'user': 'Test user prompt'},
        'params': {},
        'model': object(),
        'simulated_response': 'test'
    }
    # Disable personas
    raw_agent_data['settings']['system']['persona']['enabled'] = False
    
    # Build structured config object
    agent_config = config_manager.build_agent_config(raw_agent_data)
    
    # Mock load_agent_data to return our structured config
    with patch.object(Config, 'load_agent_data', return_value=agent_config):
        agent = Agent('test_agent')
        
        # Assert that no persona data is added when disabled
        assert 'persona' not in agent.template_data


def test_prompt_rendering_with_persona_context(isolated_config, test_persona_file):
    """Tests that prompt rendering integrates persona context data correctly."""
    # Create a ConfigManager instance to build structured config
    config_manager = ConfigManager()
    
    # Setup
    persona_name = os.path.basename(test_persona_file).replace('.yaml', '')
    
    # Add the test persona to the Config data
    isolated_config.data['personas'] = {persona_name: yaml.safe_load(open(test_persona_file))}
    
    # Create raw agent data with personas enabled
    raw_agent_data = {
        'name': 'test_agent',
        'settings': isolated_config.data['settings'].copy(),
        'persona': isolated_config.data['personas'][persona_name],
        'prompts': {'system': 'System prompt', 'user': 'User prompt'},
        'params': {},
        'model': object(),
        'simulated_response': 'test'
    }
    # Enable personas
    raw_agent_data['settings']['system']['persona']['enabled'] = True
    
    # Build structured config object
    agent_config = config_manager.build_agent_config(raw_agent_data)
    
    # Mock load_agent_data to return our structured config
    with patch.object(Config, 'load_agent_data', return_value=agent_config):
        # Create and set the prompt processor mock
        with patch('agentforge.agent.PromptProcessor') as MockPromptProcessor:
            prompt_processor_mock = MagicMock()
            MockPromptProcessor.return_value = prompt_processor_mock
            
            # Setup render_prompts to return a mock rendered prompt
            rendered_prompts = {'system': 'Rendered system prompt', 'user': 'Rendered user prompt'}
            prompt_processor_mock.render_prompts.return_value = rendered_prompts
            
            agent = Agent('test_agent')
            
            # Set some template data that will include persona
            agent.template_data['test_var'] = 'test_value'
            
            # Call the method
            agent.render_prompt()
            
            # Assert
            assert agent.prompt == rendered_prompts
            
            # Verify prompt processor is called with template data including persona
            prompt_processor_mock.render_prompts.assert_called_once_with(agent.prompt_template, agent.template_data)
            
            # Verify persona is in template_data
            assert 'persona' in agent.template_data


def test_legacy_persona_format_preserved(isolated_config):
    """Tests that legacy persona format (flat structure) is preserved as-is."""
    # Create a ConfigManager instance to build structured config
    config_manager = ConfigManager()
    
    # Create a legacy format persona
    legacy_persona = {
        'name': 'Test Agent',
        'description': 'A test agent with legacy format',
        'goal': 'Test legacy compatibility'
    }
    
    # Create raw agent data with legacy persona and personas enabled
    raw_agent_data = {
        'name': 'test_agent',
        'settings': isolated_config.data['settings'].copy(),
        'persona': legacy_persona,
        'prompts': {'system': 'Test prompt', 'user': 'Test user prompt'},
        'params': {},
        'model': object(),
        'simulated_response': 'test'
    }
    # Enable personas
    raw_agent_data['settings']['system']['persona']['enabled'] = True
    
    # Build structured config object
    agent_config = config_manager.build_agent_config(raw_agent_data)
    
    # Mock load_agent_data to return our structured config
    with patch.object(Config, 'load_agent_data', return_value=agent_config):
        agent = Agent('test_agent')
        
        # Assert that legacy persona data is preserved exactly as-is
        assert 'persona' in agent.template_data
        assert agent.template_data['persona'] == legacy_persona
        assert agent.template_data['persona']['name'] == 'Test Agent'
        assert agent.template_data['persona']['description'] == 'A test agent with legacy format' 