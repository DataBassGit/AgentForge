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
                'goal': 'Test the persona v2 implementation'
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


@pytest.fixture
def oversized_persona_file():
    """Creates a temporary persona file with oversized static content."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp:
        # Create a test persona with large static content
        persona_data = {
            'static': {
                'name': 'Test Agent',
                'description': 'A' * 10000  # Create a string larger than static_char_cap
            }
        }
        yaml.dump(persona_data, tmp)
    
    yield tmp.name
    
    # Clean up
    os.unlink(tmp.name)


def test_static_and_retrieval_blocks(isolated_config, test_persona_file):
    """Tests that static and retrieval blocks are properly loaded and flattened."""
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
                    'enabled': True,
                    'auto_inject_persona': True,
                    'static_char_cap': 8000,
                    'allow_legacy_placeholders': True
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
        
        # Assert
        assert 'name' in agent.template_data
        assert agent.template_data['name'] == 'Test Agent'  # Static should override retrieval
        assert 'setting' in agent.template_data
        assert 'persona_md' in agent.template_data
        assert '**name**: Test Agent' in agent.template_data['persona_md']


def test_oversized_static_content(isolated_config, oversized_persona_file):
    """Tests that oversized static content is truncated according to static_char_cap."""
    # Setup
    persona_name = os.path.basename(oversized_persona_file).replace('.yaml', '')
    
    # Add the test persona to the Config data
    isolated_config.data['personas'] = {persona_name: yaml.safe_load(open(oversized_persona_file))}
    
    # Mock agent data with smaller char cap
    agent_data = {
        'name': 'test_agent',
        'settings': {
            'system': {
                'persona': {
                    'enabled': True,
                    'auto_inject_persona': True,
                    'static_char_cap': 100,  # Small cap to force truncation
                    'allow_legacy_placeholders': True
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
        
        # Assert
        assert 'persona_md' in agent.template_data
        assert len(agent.template_data['persona_md']) <= 103  # 100 chars + "..." suffix
        assert agent.template_data['persona_md'].endswith('...')


def test_legacy_placeholder_handling(isolated_config, test_persona_file):
    """Tests that legacy placeholders are only applied when enabled."""
    # Setup
    persona_name = os.path.basename(test_persona_file).replace('.yaml', '')
    
    # Add the test persona to the Config data
    isolated_config.data['personas'] = {persona_name: yaml.safe_load(open(test_persona_file))}
    
    # Mock agent data with legacy placeholders disabled
    agent_data = {
        'name': 'test_agent',
        'settings': {
            'system': {
                'persona': {
                    'enabled': True,
                    'auto_inject_persona': True,
                    'static_char_cap': 2048,
                    'allow_legacy_placeholders': False  # Disable legacy placeholders
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
        
        # Assert that template_data doesn't have the flattened keys
        assert 'name' not in agent.template_data
        assert 'setting' not in agent.template_data
        # But it should still have persona_md since auto_inject_persona is True
        assert 'persona_md' in agent.template_data


def test_persona_md_injection(isolated_config, test_persona_file):
    """Tests that persona_md is correctly injected into the system prompt."""
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
                    'enabled': True,
                    'auto_inject_persona': True,
                    'static_char_cap': 2048,
                    'allow_legacy_placeholders': True
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
        agent.persona_settings = agent_data['settings']['system']['persona'] 
        agent.prompt_template = {'system': 'System prompt', 'user': 'User prompt'}
        agent.template_data = {}
        
        # Create and set the prompt processor mock
        prompt_processor_mock = MagicMock()
        
        # Setup build_persona_markdown to return a mock persona_md
        persona_md = "**name**: Test Agent\n**description**: A test agent for unit tests"
        prompt_processor_mock.build_persona_markdown.return_value = persona_md
        
        # Setup render_prompts to return a mock rendered prompt
        rendered_prompts = {'system': 'Rendered system prompt', 'user': 'Rendered user prompt'}
        prompt_processor_mock.render_prompts.return_value = rendered_prompts
        
        # Setup check_inject_persona_md to modify and return the prompt
        modified_prompts = {'system': f"Rendered system prompt\n\n{persona_md}", 'user': 'Rendered user prompt'}
        prompt_processor_mock.check_inject_persona_md.return_value = modified_prompts
        
        agent.prompt_processor = prompt_processor_mock
        agent.logger = MagicMock()
        
        # Call load_persona_data to set up template_data (this will add persona_md to template_data)
        with patch.object(Agent, '_build_persona_markdown') as mock_build_md:
            # Make the method set persona_md directly
            def set_persona_md():
                agent.template_data['persona_md'] = persona_md
            mock_build_md.side_effect = set_persona_md
            agent.load_persona_data()
        
        # Call the method
        agent.render_prompt()
        
        # Assert
        assert agent.prompt == modified_prompts
        assert 'system' in agent.prompt
        
        # Verify the persona_md is included in the system prompt
        assert persona_md in agent.prompt['system']
        
        # Verify correct method calls
        prompt_processor_mock.render_prompts.assert_called_once_with(agent.prompt_template, agent.template_data)
        prompt_processor_mock.check_inject_persona_md.assert_called_once_with(
            rendered_prompts, agent.template_data, agent.persona_settings
        )


def test_no_truncation_when_cap_is_zero(isolated_config, oversized_persona_file):
    """Tests that no truncation happens when static_char_cap is set to 0."""
    # Setup
    persona_name = os.path.basename(oversized_persona_file).replace('.yaml', '')
    
    # Add the test persona to the Config data
    isolated_config.data['personas'] = {persona_name: yaml.safe_load(open(oversized_persona_file))}
    
    # Mock agent data with static_char_cap set to 0
    agent_data = {
        'name': 'test_agent',
        'settings': {
            'system': {
                'persona': {
                    'enabled': True,
                    'auto_inject_persona': True,
                    'static_char_cap': 0,  # Set to 0 to disable truncation
                    'allow_legacy_placeholders': True
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
        
        # Assert that persona_md is in template_data and has not been truncated
        assert 'persona_md' in agent.template_data
        
        # The description in the persona is 10,000 characters
        # Verify it's not truncated (length should be more than 10,000 including markdown formatting)
        assert len(agent.template_data['persona_md']) > 10000
        assert not agent.template_data['persona_md'].endswith('...')  # Should not end with truncation indicator 