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
    # Setup
    persona_name = os.path.basename(test_persona_file).replace('.yaml', '')
    
    # Add the test persona to the Config data
    isolated_config.data['personas'] = {persona_name: yaml.safe_load(open(test_persona_file))}
    
    # Mock agent data
    agent_data = {
        'name': 'test_agent',
        'settings': {
            'system': {
                'persona': {
                    'enabled': True
                }
            }
        },
        'persona': isolated_config.data['personas'][persona_name],
        'prompts': {'system': 'Test prompt', 'user': 'Test user prompt'},
        'params': {}
    }
    
    # Create agent and manually set properties rather than initializing
    with patch.object(Agent, 'initialize_agent_config'):
        agent = Agent()
        agent.agent_data = agent_data
        agent.persona = agent_data['persona']
        agent.template_data = {}
        agent.logger = MagicMock()
        
        # Call the method
        agent.load_persona_data()
        
        # Assert that persona data is added directly to template_data
        assert 'persona' in agent.template_data
        assert agent.template_data['persona'] == agent_data['persona']
        assert 'static' in agent.template_data['persona']
        assert 'retrieval' in agent.template_data['persona']
        
        # Verify the original structure is preserved
        assert agent.template_data['persona']['static']['name'] == 'Test Agent'
        assert agent.template_data['persona']['retrieval']['setting'] == 'Virtual test environment'


def test_persona_disabled(isolated_config, test_persona_file):
    """Tests that persona data is not loaded when personas are disabled."""
    # Setup
    persona_name = os.path.basename(test_persona_file).replace('.yaml', '')
    
    # Add the test persona to the Config data
    isolated_config.data['personas'] = {persona_name: yaml.safe_load(open(test_persona_file))}
    
    # Mock agent data with personas disabled
    agent_data = {
        'name': 'test_agent',
        'settings': {
            'system': {
                'persona': {
                    'enabled': False
                }
            }
        },
        'persona': isolated_config.data['personas'][persona_name],
        'prompts': {'system': 'Test prompt', 'user': 'Test user prompt'},
        'params': {}
    }
    
    # Create agent and manually set properties rather than initializing
    with patch.object(Agent, 'initialize_agent_config'):
        agent = Agent()
        agent.agent_data = agent_data
        agent.persona = agent_data['persona']
        agent.template_data = {}
        agent.logger = MagicMock()
        
        # Call the method
        agent.load_persona_data()
        
        # Assert that no persona data is added when disabled
        assert 'persona' not in agent.template_data


def test_prompt_rendering_with_persona_context(isolated_config, test_persona_file):
    """Tests that prompt rendering integrates persona context data correctly."""
    # Setup
    persona_name = os.path.basename(test_persona_file).replace('.yaml', '')
    
    # Add the test persona to the Config data
    isolated_config.data['personas'] = {persona_name: yaml.safe_load(open(test_persona_file))}
    
    # Mock agent data
    agent_data = {
        'name': 'test_agent',
        'settings': {
            'system': {
                'persona': {
                    'enabled': True
                }
            }
        },
        'persona': isolated_config.data['personas'][persona_name],
        'prompts': {'system': 'Test prompt', 'user': 'Test user prompt'},
        'params': {}
    }
    
    # Create agent and manually set properties rather than initializing
    with patch.object(Agent, 'initialize_agent_config'):
        agent = Agent()
        agent.agent_data = agent_data
        agent.persona = agent_data['persona']
        agent.prompt_template = {'system': 'System prompt', 'user': 'User prompt'}
        agent.template_data = {'persona': agent_data['persona']}
        
        # Create and set the prompt processor mock
        prompt_processor_mock = MagicMock()
        
        # Setup render_prompts to return a mock rendered prompt
        rendered_prompts = {'system': 'Rendered system prompt', 'user': 'Rendered user prompt'}
        prompt_processor_mock.render_prompts.return_value = rendered_prompts
        
        agent.prompt_processor = prompt_processor_mock
        agent.logger = MagicMock()
        
        # Call the method
        agent.render_prompt()
        
        # Assert
        assert agent.prompt == rendered_prompts
        
        # Verify prompt processor is called with template data including persona
        prompt_processor_mock.render_prompts.assert_called_once_with(agent.prompt_template, agent.template_data)
        prompt_processor_mock.validate_rendered_prompts.assert_called_once_with(rendered_prompts)


def test_legacy_persona_format_preserved(isolated_config):
    """Tests that legacy persona format (flat structure) is preserved as-is."""
    # Create a legacy format persona
    legacy_persona = {
        'name': 'Test Agent',
        'description': 'A test agent with legacy format',
        'goal': 'Test legacy compatibility'
    }
    
    # Mock agent data with legacy persona
    agent_data = {
        'name': 'test_agent',
        'settings': {
            'system': {
                'persona': {
                    'enabled': True
                }
            }
        },
        'persona': legacy_persona,
        'prompts': {'system': 'Test prompt', 'user': 'Test user prompt'},
        'params': {}
    }
    
    # Create agent and manually set properties rather than initializing
    with patch.object(Agent, 'initialize_agent_config'):
        agent = Agent()
        agent.agent_data = agent_data
        agent.persona = agent_data['persona']
        agent.template_data = {}
        agent.logger = MagicMock()
        
        # Call the method
        agent.load_persona_data()
        
        # Assert that legacy persona data is preserved exactly as-is
        assert 'persona' in agent.template_data
        assert agent.template_data['persona'] == legacy_persona
        assert agent.template_data['persona']['name'] == 'Test Agent'
        assert agent.template_data['persona']['description'] == 'A test agent with legacy format' 