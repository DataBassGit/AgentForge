"""
Tests for PersonaMemory deduplication functionality.

This module tests the enhanced PersonaMemory that now checks for exact duplicates
before adding new facts to storage.
"""

import pytest
from unittest.mock import Mock, patch
from agentforge.storage.persona_memory import PersonaMemory


class TestPersonaMemoryDeduplication:
    """Test suite for PersonaMemory deduplication functionality."""
    
    @pytest.fixture
    def persona_memory(self, isolated_config, fake_chroma):
        """Create a PersonaMemory instance with mocked dependencies using conftest infrastructure."""
        # The fake_chroma fixture clears the registry, so we start fresh
        fake_chroma.clear_registry()
        
        # Mock the agents using the same pattern as existing tests
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
            
            # Create the PersonaMemory instance
            memory = PersonaMemory("test_cog", collection_id="test_facts", persona=None)
            
            # Store references to mocks for test access
            memory._test_agents = {
                'retrieval': retrieval_mock,
                'narrative': narrative_mock,
                'update': update_mock
            }
            memory._test_storage = memory.storage  # Use the actual FakeChromaStorage instance
            
            yield memory
    
    def test_exact_duplicate_exists_true(self, persona_memory):
        """Test that _exact_duplicate_exists returns True for exact matches."""
        # Add some existing facts to storage, including an exact match
        persona_memory._test_storage.save_to_storage(
            collection_name=persona_memory.collection_name,
            data=['User prefers Python programming', 'Other fact'],
            ids=['1', '2'],
            metadata=[{}, {}]
        )
        
        result = persona_memory.is_duplicate_fact('User prefers Python programming')
        assert result is True
    
    def test_exact_duplicate_exists_false(self, persona_memory):
        """Test that _exact_duplicate_exists returns False for no matches."""
        # Add some existing facts to storage, but no exact matches
        persona_memory._test_storage.save_to_storage(
            collection_name=persona_memory.collection_name,
            data=['User likes Java', 'User enjoys coding'],
            ids=['1', '2'],
            metadata=[{}, {}]
        )
        
        result = persona_memory.is_duplicate_fact('User prefers Python programming')
        assert result is False
    
    def test_exact_duplicate_exists_text_match(self, persona_memory):
        """Test that _exact_duplicate_exists detects text matches even with whitespace."""
        # Add existing fact with extra whitespace
        persona_memory._test_storage.save_to_storage(
            collection_name=persona_memory.collection_name,
            data=['  User prefers Python programming  ', 'Other fact'],
            ids=['1', '2'],
            metadata=[{}, {}]
        )
        
        result = persona_memory.is_duplicate_fact('User prefers Python programming')
        assert result is True
    
    def test_exact_duplicate_exists_error_handling(self, persona_memory):
        """Test that _exact_duplicate_exists handles errors gracefully."""
        # Mock the query_storage method to raise an exception
        with patch.object(persona_memory._test_storage, 'query_storage', side_effect=Exception("Storage error")):
            result = persona_memory.is_duplicate_fact('Any fact')
            assert result is False  # Should return False on error to allow addition
    
    def test_update_memory_skips_duplicate_add(self, persona_memory):
        """Test that update_memory skips adding duplicate facts."""
        # Setup agent responses
        persona_memory._test_agents['retrieval'].run.return_value = {"queries": ["existing facts"]}
        persona_memory._test_agents['update'].run.return_value = {
            "action": "add",
            "new_facts": [
                {
                    "fact": "User enjoys classical music"
                }
            ]
        }
        
        # Add the exact same fact to storage first (will cause duplicate detection)
        persona_memory._test_storage.save_to_storage(
            collection_name=persona_memory.collection_name,
            data=["User enjoys classical music"],
            metadata=[{}]
        )
        
        # Count facts before update
        initial_count = persona_memory._test_storage.count_collection(persona_memory.collection_name)
        
        # Execute update
        test_data = {'user_preference': 'classical music'}
        persona_memory.update_memory(["user_preference"], _ctx=test_data, _state={})
        
        # Verify storage count hasn't increased (duplicate was skipped)
        final_count = persona_memory._test_storage.count_collection(persona_memory.collection_name)
        assert final_count == initial_count
    
    def test_update_memory_adds_non_duplicate(self, persona_memory):
        """Test that update_memory adds facts that are not duplicates."""
        # Setup agent responses
        persona_memory._test_agents['retrieval'].run.return_value = {"queries": ["existing facts"]}
        persona_memory._test_agents['update'].run.return_value = {
            "action": "add",
            "new_facts": [
                {
                    "fact": "User enjoys classical music"
                }
            ]
        }
        
        # Add some different facts to storage (not the one we're about to add)
        persona_memory._test_storage.save_to_storage(
            collection_name=persona_memory.collection_name,
            data=["User likes jazz", "User prefers morning meetings"],
            metadata=[{}, {}]
        )
        
        # Count facts before update
        initial_count = persona_memory._test_storage.count_collection(persona_memory.collection_name)
        
        # Execute update
        test_data = {'user_preference': 'classical music'}
        persona_memory.update_memory(["user_preference"], _ctx=test_data, _state={})
        
        # Verify storage count increased (new fact was added)
        final_count = persona_memory._test_storage.count_collection(persona_memory.collection_name)
        assert final_count == initial_count + 1
        
        # Verify the new fact is in storage
        all_facts = persona_memory._test_storage.query_storage(
            collection_name=persona_memory.collection_name,
            num_results=final_count
        )
        assert "User enjoys classical music" in all_facts['documents']
    
    def test_update_memory_update_action_not_affected(self, persona_memory):
        """Test that update action (not add) is not affected by deduplication."""
        # Setup agent responses
        persona_memory._test_agents['retrieval'].run.return_value = {"queries": ["music preferences"]}
        persona_memory._test_agents['update'].run.return_value = {
            "action": "update",
            "new_facts": [
                {
                    "fact": "User now prefers jazz music",
                    "supersedes": ["fact123"]
                }
            ]
        }
        
        # Add some existing facts to storage
        persona_memory._test_storage.save_to_storage(
            collection_name=persona_memory.collection_name,
            data=['User likes rock music'],
            ids=['fact123'],
            metadata=[{'type': 'preference'}]
        )
        
        # Count facts before update
        initial_count = persona_memory._test_storage.count_collection(persona_memory.collection_name)
        
        # Execute update (deduplication should not apply to update actions)
        test_data = {'user_preference': 'jazz music'}
        persona_memory.update_memory(["user_preference"], _ctx=test_data, _state={})
        
        # Verify storage count increased (update actions always add new facts)
        final_count = persona_memory._test_storage.count_collection(persona_memory.collection_name)
        assert final_count == initial_count + 1
        
        # Verify the new fact is in storage
        all_facts = persona_memory._test_storage.query_storage(
            collection_name=persona_memory.collection_name,
            num_results=final_count
        )
        assert "User now prefers jazz music" in all_facts['documents'] 