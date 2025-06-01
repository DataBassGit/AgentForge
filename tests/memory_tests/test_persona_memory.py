"""
Tests for PersonaMemory functionality.

This module tests the PersonaMemory class implementation including:
- Query operations with specialized agents
- Update operations with fact management
- JSON parsing and error handling
- Integration with ChromaStorage
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from agentforge.storage.persona_memory import PersonaMemory
from agentforge.utils.parsing_processor import ParsingError


class TestPersonaMemory:
    """Test suite for PersonaMemory class."""
    
    @pytest.fixture
    def mock_agents(self):
        """Mock the specialized agents used by PersonaMemory."""
        with patch('agentforge.storage.persona_memory.Agent') as mock_agent_class:
            # Create mock instances for each agent
            retrieval_mock = Mock()
            narrative_mock = Mock()
            update_mock = Mock()
            
            # Configure the Agent class to return different mocks based on agent_name
            def agent_side_effect(agent_name):
                if agent_name == "retrieval_agent":
                    return retrieval_mock
                elif agent_name == "narrative_agent":
                    return narrative_mock
                elif agent_name == "update_agent":
                    return update_mock
                    
            mock_agent_class.side_effect = agent_side_effect
            
            yield {
                'retrieval': retrieval_mock,
                'narrative': narrative_mock,
                'update': update_mock,
                'class': mock_agent_class
            }
            
    @pytest.fixture
    def persona_memory(self, mock_agents, isolated_config, fake_chroma):
        """Create a PersonaMemory instance with mocked dependencies leveraging conftest infrastructure."""
        # The fake_chroma fixture clears the registry, and ChromaStorage is already replaced globally
        fake_chroma.clear_registry()
        
        # Override the persona data in the isolated config
        test_persona_data = {
            'static': {
                'name': 'Test Assistant',
                'description': 'A helpful test assistant',
                'goal': 'Help with testing'
            },
            'retrieval': {
                'tone': 'Professional',
                'expertise': ['Testing', 'Mocking']
            }
        }
        
        # Update the config data with our test settings
        isolated_config.data['settings']['system']['persona'] = {
            'enabled': True,
            'static_char_cap': 8000
        }
        
        # Override the default persona
        isolated_config.data['personas']['default_assistant'] = test_persona_data
        
        # Mock persona resolution in the isolated config
        with patch.object(isolated_config, 'resolve_persona') as mock_resolve_persona:
            mock_resolve_persona.return_value = test_persona_data
            
            # Create PersonaMemory instance - it will use FakeChromaStorage automatically
            memory = PersonaMemory(cog_name="test_cog", persona="TestPersona")
            
            # Store references to mocks for testing
            memory._test_agents = mock_agents
            memory._test_storage = memory.storage  # Use the actual FakeChromaStorage instance
            memory._test_config = isolated_config
            
            return memory
            
    def test_initialization(self, persona_memory):
        """Test PersonaMemory initialization."""
        assert persona_memory.cog_name == "test_cog"
        assert persona_memory.persona == "TestPersona"
        assert persona_memory.narrative is None
        
        # Verify agents were initialized
        persona_memory._test_agents['class'].assert_any_call(agent_name="retrieval_agent")
        persona_memory._test_agents['class'].assert_any_call(agent_name="narrative_agent")
        persona_memory._test_agents['class'].assert_any_call(agent_name="update_agent")
        
    def test_build_collection_name(self, mock_agents, isolated_config, fake_chroma):
        """Test collection name building for PersonaMemory."""
        fake_chroma.clear_registry()
        
        # Default collection name
        memory = PersonaMemory(cog_name="test_cog", persona="TestPersona")
        collection_name = memory._build_collection_name()
        assert collection_name == "persona_facts_TestPersona"
        
        # With custom collection_id
        memory_with_id = PersonaMemory(
            cog_name="test_cog",
            persona="TestPersona",
            collection_id="custom_facts"
        )
        assert memory_with_id._build_collection_name() == "custom_facts_TestPersona"
        
    def test_query_memory_success(self, persona_memory):
        """Test successful query memory operation."""
        # Setup mocks
        persona_memory._test_agents['retrieval'].run.return_value = {
            "queries": [
                "assistant preferences and settings",
                "user interaction history"
            ]
        }
        
        # Setup FakeChromaStorage to return results for each query
        storage = persona_memory._test_storage
        
        # We need to simulate the storage.query_storage calls
        def query_side_effect(**kwargs):
            query = kwargs.get('query', '')
            if 'preferences' in str(query):
                return {
                    'documents': ['User prefers concise responses'],
                    'ids': ['fact1'],
                    'metadatas': [{'type': 'preference'}]
                }
            else:
                return {
                    'documents': ['User asked about Python programming'],
                    'ids': ['fact2'],
                    'metadatas': [{'type': 'interaction'}]
                }
        
        # Mock the query_storage method
        with patch.object(storage, 'query_storage', side_effect=query_side_effect):
            persona_memory._test_agents['narrative'].run.return_value = {
                "narrative": "The assistant is configured for a user who prefers concise responses and has shown interest in Python programming."
            }
            
            # Execute query
            persona_memory.query_memory(query_keys=["user_preferences"], _ctx={"user_preferences": "What does the user prefer?"}, _state={})
            
            # Verify results
            result = persona_memory.store
            assert result is not None
            assert result['_narrative'] == "The assistant is configured for a user who prefers concise responses and has shown interest in Python programming."
            assert '_static' in result
            assert "Test Assistant" in result['_static']
            
            # Verify agent calls
            persona_memory._test_agents['retrieval'].run.assert_called_once()
            persona_memory._test_agents['narrative'].run.assert_called_once()
        
    def test_query_memory_no_queries_generated(self, persona_memory):
        """Test query memory when retrieval agent returns no queries."""
        # Setup mocks
        persona_memory._test_agents['retrieval'].run.return_value = {"queries": []}
        
        # Execute query
        persona_memory.query_memory(query_keys=["test_query"], _ctx={"test_query": "Test query"}, _state={})
        
        # Should return static-only narrative
        result = persona_memory.store
        assert result is not None
        assert "Based on the static persona information" in result['_narrative']
        assert result.get('raw_facts') == []
        
    def test_query_memory_invalid_response(self, persona_memory):
        """Test query memory with invalid response format."""
        # Setup mock to return invalid response format
        persona_memory._test_agents['retrieval'].run.return_value = "Invalid response format"
        
        # Execute query - should handle gracefully
        persona_memory.query_memory(query_keys=["test_query"], _ctx={"test_query": "Test query"}, _state={})
        
        # Should return static-only narrative
        result = persona_memory.store
        assert result is not None
        assert "Based on the static persona information" in result['_narrative']
        
    def test_update_memory_add_action(self, persona_memory):
        """Test update memory with add action."""
        # Setup mocks
        persona_memory._test_agents['retrieval'].run.return_value = {"queries": ["existing facts"]}
        
        # Mock empty query result
        with patch.object(persona_memory._test_storage, 'query_storage') as mock_query:
            mock_query.return_value = {
                'documents': [],
                'ids': [],
                'metadatas': []
            }
            
            persona_memory._test_agents['update'].run.return_value = {
                "action": "add",
                "new_facts": [
                    {
                        "fact": "User enjoys classical music"
                    }
                ]
            }
            
            # Mock save_to_storage to capture the call
            with patch.object(persona_memory._test_storage, 'save_to_storage') as mock_save:
                # Execute update
                test_data = {'user_preference': 'classical music'}
                persona_memory.update_memory(update_keys=["test_data"], _ctx=test_data, _state={})
                
                # Verify storage was called to save the new fact
                mock_save.assert_called_once()
                call_args = mock_save.call_args
                
                assert call_args[1]['data'] == ["User enjoys classical music"]
                assert call_args[1]['metadata'][0]['type'] == 'persona_fact'
                assert call_args[1]['metadata'][0]['source'] == 'update_agent'
        
    def test_update_memory_update_action(self, persona_memory):
        """Test update memory with update action (superseding facts)."""
        # Setup mocks
        persona_memory._test_agents['retrieval'].run.return_value = {"queries": ["music preferences"]}
        
        with patch.object(persona_memory._test_storage, 'query_storage') as mock_query:
            mock_query.return_value = {
                'documents': ['User likes rock music'],
                'ids': ['fact123'],
                'metadatas': [{'type': 'preference'}]
            }
            
            persona_memory._test_agents['update'].run.return_value = {
                "action": "update",
                "new_facts": [
                    {
                        "fact": "User now prefers jazz music",
                        "supersedes": ["fact123"]
                    }
                ]
            }
            
            with patch.object(persona_memory._test_storage, 'save_to_storage') as mock_save:
                # Execute update
                test_data = {'user_preference': 'jazz music'}
                persona_memory.update_memory(update_keys=["test_data"], _ctx=test_data, _state={})
                
                # Verify storage was called
                mock_save.assert_called_once()
                call_args = mock_save.call_args
                
                assert call_args[1]['data'] == ["User now prefers jazz music"]
                assert call_args[1]['metadata'][0]['supersedes'] == 'fact123'
        
    def test_update_memory_no_action(self, persona_memory):
        """Test update memory with no action required."""
        # Setup mocks
        persona_memory._test_agents['retrieval'].run.return_value = {"queries": []}
        persona_memory._test_agents['update'].run.return_value = {"action": "none"}
        
        with patch.object(persona_memory._test_storage, 'save_to_storage') as mock_save:
            # Execute update
            test_data = {'irrelevant': 'data'}
            persona_memory.update_memory(update_keys=["test_data"], _ctx=test_data, _state={})
            
            # Verify storage was NOT called
            mock_save.assert_not_called()
        
    def test_get_static_persona_markdown(self, persona_memory):
        """Test static persona markdown generation."""
        markdown = persona_memory._get_static_persona_markdown()
        
        # Verify content
        assert "**name**: Test Assistant" in markdown
        assert "**description**: A helpful test assistant" in markdown
        assert "**goal**: Help with testing" in markdown
        
    def test_narrative_placeholder_access(self, persona_memory):
        """Test that narrative is accessible via placeholder after query."""
        # Setup successful query
        persona_memory._test_agents['retrieval'].run.return_value = {"queries": ["test"]}
        
        with patch.object(persona_memory._test_storage, 'query_storage') as mock_query:
            mock_query.return_value = {
                'documents': ['Test fact'],
                'ids': ['1'],
                'metadatas': [{}]
            }
            persona_memory._test_agents['narrative'].run.return_value = {"narrative": "Test narrative content"}
            
            # Execute query
            persona_memory.query_memory(query_keys=["test_query"], _ctx={"test_query": "Test"}, _state={})
            
            # Verify narrative is stored
            assert persona_memory.narrative == "Test narrative content"
            assert persona_memory.store['_narrative'] == "Test narrative content"
            assert persona_memory.store['_static'] is not None
        
    def test_context_no_duplication_regression(self, persona_memory):
        """
        Regression test to ensure context contains only one copy of each datum (no duplicates).
        This test verifies that the fix for context duplication works correctly:
        - The context should contain only nested structure (external/internal)
        - Each datum should appear only once in the context dict
        """
        # Setup test context with nested structure
        test_context = {
            "external": {
                "user_input": "Hello, how are you?"
            },
            "internal": {
                "understand": {
                    "insights": "User is greeting and asking about well-being",
                    "persona_relevant": "User is friendly and conversational"
                }
            }
        }

        # Mock agents to capture the context passed to them
        captured_contexts = []

        def capture_context(**kwargs):
            captured_contexts.append(kwargs.get('_ctx', {}))
            return {"queries": ["test query"]}

        persona_memory._test_agents['retrieval'].run.side_effect = capture_context

        with patch.object(persona_memory._test_storage, 'query_storage') as mock_query:
            mock_query.return_value = {'documents': []}
            # Test query_memory
            persona_memory.query_memory(query_keys=["test_query"], _ctx=test_context, _state={})
            context_dict = captured_contexts[0]
            # The context should be a dict with correct nested structure
            assert "external" in context_dict
            assert "internal" in context_dict
            assert "user_input" in context_dict["external"]
            assert "understand" in context_dict["internal"]
            assert "insights" in context_dict["internal"]["understand"]
            assert "persona_relevant" in context_dict["internal"]["understand"]
            # No duplicate keys
            assert list(context_dict.keys()).count("external") == 1
            assert list(context_dict.keys()).count("internal") == 1

        # Reset captured contexts for update_memory test
        captured_contexts.clear()
        # Test update_memory with same checks
        persona_memory._test_agents['update'].run.side_effect = lambda **kwargs: (
            captured_contexts.append(kwargs.get('_ctx', {})),
            {"action": "none"}
        )[1]
        persona_memory.update_memory(update_keys=["test_data"], _ctx=test_context, _state={})
        update_context_dict = captured_contexts[0]
        assert "external" in update_context_dict
        assert "internal" in update_context_dict
        assert "user_input" in update_context_dict["external"]
        assert "insights" in update_context_dict["internal"]["understand"]
        assert "persona_relevant" in update_context_dict["internal"]["understand"]
        # No duplicate keys
        assert list(update_context_dict.keys()).count("external") == 1
        assert list(update_context_dict.keys()).count("internal") == 1 