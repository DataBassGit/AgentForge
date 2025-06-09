"""
Integration tests for PersonaMemory with full cog workflow.

This module tests the complete PersonaMemory functionality including:
- Full cog execution with understand and respond agents
- Memory query and update cycles
- Agent interaction with persona placeholders
- End-to-end conversation flow
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from agentforge.cog import Cog
from agentforge.storage.persona_memory import PersonaMemory


class TestPersonaMemoryIntegration:
    """Integration test suite for PersonaMemory with full cog workflow."""
    
    @pytest.fixture
    def cog_config_with_persona_memory(self, isolated_config, fake_chroma):
        """Configure the isolated config with PersonaMemory cog setup."""
        fake_chroma.clear_registry()
        
        # Add PersonaMemory cog configuration to the isolated config
        persona_memory_cog = {
            'cog': {
                'name': 'PersonaMemoryExample',
                'description': 'Test workflow with PersonaMemory',
                'persona': 'default_assistant',
                'agents': [
                    {'id': 'understand', 'template_file': 'UnderstandAgent'},
                    {'id': 'respond', 'template_file': 'persona_response_agent'}
                ],
                'memory': [
                    {
                        'id': 'persona_memory',
                        'type': 'agentforge.storage.persona_memory.PersonaMemory',
                        'collection_id': 'user_persona_facts',
                        'query_before': 'understand',
                        'query_keys': ['user_input'],
                        'update_after': 'respond',
                        'update_keys': ['understand.insights', 'understand.persona_relevant', 'user_input']
                    }
                ],
                'flow': {
                    'start': 'understand',
                    'transitions': {
                        'understand': 'respond',
                        'respond': {'end': True}
                    }
                }
            }
        }
        
        # Add PersonaMemory agent templates
        understand_prompts = {
            'prompts': {
                'system': 'You analyze user input for understanding and persona relevance.',
                'user': 'Analyze this input: {user_input}'
            }
        }
        
        persona_response_prompts = {
            'prompts': {
                'system': 'You respond using persona context: {memory.persona_memory._narrative}',
                'user': 'Respond to: {user_input}'
            }
        }
        
        # Add the specialized PersonaMemory agent templates
        retrieval_agent_prompts = {
            'prompts': {
                'system': {
                    'intro': 'You are the Retrieval Agent for persona memory.',
                    'context': '{context}'
                },
                'user': 'Generate semantic queries for persona facts.'
            }
        }
        
        narrative_agent_prompts = {
            'prompts': {
                'system': {
                    'intro': 'You are the Narrative Agent.',
                    'static_persona': '{persona_static}',
                    'retrieved_facts': '{retrieved_facts}'
                },
                'user': 'Create a narrative summary.'
            }
        }
        
        update_agent_prompts = {
            'prompts': {
                'system': {
                    'intro': 'You are the Update Agent for persona memory.',
                    'context': '{context}'
                },
                'user': 'Determine if facts should be updated.'
            }
        }
        
        # Update isolated config with our test configuration
        isolated_config.data.setdefault('cogs', {})['ExampleCogWithPersonaMemory'] = persona_memory_cog
        isolated_config.data.setdefault('prompts', {})['UnderstandAgent'] = understand_prompts
        isolated_config.data.setdefault('prompts', {})['persona_response_agent'] = persona_response_prompts
        isolated_config.data.setdefault('prompts', {})['retrieval_agent'] = retrieval_agent_prompts
        isolated_config.data.setdefault('prompts', {})['narrative_agent'] = narrative_agent_prompts
        isolated_config.data.setdefault('prompts', {})['update_agent'] = update_agent_prompts
        
        # Ensure personas are configured
        isolated_config.data.setdefault('personas', {})['default_assistant'] = {
            'static': {
                'name': 'Test Assistant',
                'description': 'A helpful test assistant',
                'goal': 'Help with testing'
            },
            'retrieval': {
                'tone': 'Professional',
                'expertise': ['Testing', 'AI']
            }
        }
        
        # Mock the config methods that Cog uses
        with patch.object(isolated_config, 'load_cog_data') as mock_load_cog, \
             patch.object(isolated_config, 'load_agent_data') as mock_load_agent, \
             patch.object(isolated_config, 'resolve_persona') as mock_resolve_persona:
            
            mock_load_cog.return_value = persona_memory_cog
            
            def load_agent_side_effect(agent_name):
                base_data = {
                    'name': agent_name,
                    'settings': isolated_config.data.get('settings', {}),
                    'model': Mock(),
                    'params': {},
                    'persona': isolated_config.data['personas']['default_assistant'],
                    'prompts': isolated_config.data['prompts'].get(agent_name, {}).get('prompts', {}),
                    'simulated_response': f'Simulated response from {agent_name}'
                }
                return base_data
                
            mock_load_agent.side_effect = load_agent_side_effect
            mock_resolve_persona.return_value = isolated_config.data['personas']['default_assistant']
            
            yield isolated_config

    @pytest.fixture
    def mock_persona_agents(self, monkeypatch):
        """Mock the specialized persona agents used by PersonaMemory by patching the stubbed_agents behavior."""
        from agentforge.agent import Agent
        
        # Get the original stubbed run method that was already patched
        stubbed_run = Agent.run
        
        # Create our custom responses for PersonaMemory agents
        def enhanced_fake_run(self: Agent, **context):
            agent_name = getattr(self, 'agent_name', 'unknown')
            
            if agent_name == "retrieval_agent":
                return {"queries": ["user preferences", "interaction patterns"]}
            elif agent_name == "narrative_agent":
                return {"narrative": "User is a developer who prefers concise explanations and enjoys Python programming."}
            elif agent_name == "update_agent":
                return {"action": "add", "new_facts": [{"fact": "User enjoys discussing programming topics"}]}
            else:
                # Fall back to the original stubbed behavior for other agents
                return stubbed_run(self, **context)
        
        # Replace the stubbed run method with our enhanced version
        monkeypatch.setattr(Agent, "run", enhanced_fake_run, raising=True)
        
        # Return mock objects for assertion tracking (though they won't be called directly)
        # We'll track calls by patching the enhanced_fake_run method
        call_counts = {'retrieval': 0, 'narrative': 0, 'update': 0}
        original_enhanced = enhanced_fake_run
        
        def tracking_fake_run(self: Agent, **context):
            agent_name = getattr(self, 'agent_name', 'unknown')
            if agent_name == "retrieval_agent":
                call_counts['retrieval'] += 1
            elif agent_name == "narrative_agent":  
                call_counts['narrative'] += 1
            elif agent_name == "update_agent":
                call_counts['update'] += 1
            return original_enhanced(self, **context)
        
        monkeypatch.setattr(Agent, "run", tracking_fake_run, raising=True)
        
        # Create mock-like objects to match the expected interface
        class CallTracker:
            def __init__(self, agent_type):
                self.agent_type = agent_type
                
            @property
            def call_count(self):
                return call_counts[self.agent_type]
                
            def assert_called(self):
                if self.call_count == 0:
                    raise AssertionError(f"Expected '{self.agent_type}' agent to have been called")
        
        yield {
            'retrieval': CallTracker('retrieval'),
            'narrative': CallTracker('narrative'), 
            'update': CallTracker('update'),
            'call_counts': call_counts
        } 