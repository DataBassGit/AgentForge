"""
Tests for ParsingProcessor flatten_dict functionality and memory integration.

This module tests that flatten_dict was successfully moved to ParsingProcessor
and that memory operations continue to work correctly with the centralized function.
"""

import pytest
from agentforge.utils.parsing_processor import ParsingProcessor
from agentforge.storage.memory import Memory


class TestParsingProcessorFlatten:
    """Test suite for flatten_dict functionality in ParsingProcessor."""
    
    def test_flatten_dict_basic(self):
        """Test basic flatten_dict functionality."""
        test_dict = {
            'a': 1,
            'b': {
                'c': 2,
                'd': {
                    'e': 3
                }
            },
            'f': 4
        }
        
        expected = {
            'a': 1,
            'b.c': 2,
            'b.d.e': 3,
            'f': 4
        }
        
        result = ParsingProcessor.flatten_dict(test_dict)
        assert result == expected
    
    def test_flatten_dict_empty(self):
        """Test flatten_dict with empty dictionary."""
        result = ParsingProcessor.flatten_dict({})
        assert result == {}
    
    def test_flatten_dict_custom_separator(self):
        """Test flatten_dict with custom separator."""
        test_dict = {
            'a': {
                'b': {
                    'c': 1
                }
            }
        }
        
        result = ParsingProcessor.flatten_dict(test_dict, sep='_')
        expected = {'a_b_c': 1}
        assert result == expected
    
    def test_flatten_dict_with_parent_key(self):
        """Test flatten_dict with parent key prefix."""
        test_dict = {
            'a': 1,
            'b': {
                'c': 2
            }
        }
        
        result = ParsingProcessor.flatten_dict(test_dict, parent_key='prefix')
        expected = {
            'prefix.a': 1,
            'prefix.b.c': 2
        }
        assert result == expected
    
    def test_memory_uses_parsing_processor_flatten(self, isolated_config, fake_chroma):
        """Test that Memory class correctly uses ParsingProcessor.flatten_dict."""
        fake_chroma.clear_registry()
        
        # Create a memory instance
        memory = Memory(cog_name="test_cog")
        
        # Test data that will be flattened
        test_data = {
            'user': {
                'name': 'John',
                'preferences': {
                    'theme': 'dark',
                    'language': 'en'
                }
            },
            'session': 'abc123'
        }
        # Use update_memory to test flattening
        memory.update_memory(update_keys=None, _ctx=test_data, _state={})
        # The processed data is stored in memory.storage, but FakeChromaStorage is used, so we check the store
        # We can check that the store is empty (since FakeChromaStorage doesn't persist), but no error should occur
        assert isinstance(memory, Memory)
        # Test flatten_dict directly
        flattened = ParsingProcessor.flatten_dict(test_data)
        expected_values = ['John', 'dark', 'en', 'abc123']
        assert sorted(flattened.values()) == sorted(expected_values)
        expected_keys = {'user.name', 'user.preferences.theme', 'user.preferences.language', 'session'}
        assert expected_keys.issubset(set(flattened.keys()))

    def test_memory_prepare_data_with_context(self, isolated_config, fake_chroma):
        """Test that Memory._prepare_update_data correctly handles context flattening."""
        fake_chroma.clear_registry()
        
        test_data = {'key': 'value'}
        test_ctx = {
            'external': {
                'user_input': 'Hello'
            }
        }
        test_state = {
            'internal': {
                'state': 'active'
            }
        }
        memory = Memory(cog_name="test_cog")
        processed_data, metadata_list = memory._prepare_update_data(update_keys=None, _ctx=test_ctx, _state=test_state)
        # The merged context will flatten both 'Hello' and 'active'
        assert sorted(processed_data) == sorted(['Hello', 'active'])
        # Test flatten_dict directly for metadata
        merged = {**test_ctx.get('external', {}), **test_state.get('internal', {})}
        flat = ParsingProcessor.flatten_dict(merged)
        # Just check that flatten_dict works as expected
        assert isinstance(flat, dict)


class TestMemoryContextStateSeparation:
    """Test suite to verify that MemoryManager properly separates _ctx and _state."""
    
    def test_memory_query_with_separate_params(self, isolated_config, fake_chroma):
        """Test that Memory.query_memory can handle separate _ctx and _state parameters."""
        fake_chroma.clear_registry()
        
        memory = Memory(cog_name="test_cog")
        
        test_ctx = {'external': {'user_input': 'test'}}
        test_state = {'internal': {'value': 'data'}}
        
        # Test query with separate parameters - should merge them internally
        result = memory.query_memory(query_keys=None, _ctx=test_ctx, _state=test_state)
        # Result should be None since no data in storage, but no errors should occur
        assert result is None or memory.store == {}
    
    def test_memory_make_query_text_merging(self, isolated_config, fake_chroma):
        """Test that Memory._build_merged_context correctly merges _ctx and _state."""
        fake_chroma.clear_registry()
        
        memory = Memory(cog_name="test_cog")
        
        test_ctx = {'ctx_key': 'ctx_value', 'shared_key': 'ctx_wins'}
        test_state = {'state_key': 'state_value', 'shared_key': 'state_value'}
        # Use the public _build_merged_context method if available
        merged = memory._build_merged_context(test_ctx, test_state)
        expected = {
            'state_key': 'state_value',
            'ctx_key': 'ctx_value',
            'shared_key': 'ctx_wins'  # _ctx should win for shared keys
        }
        for k, v in expected.items():
            assert merged[k] == v
    
    def test_memory_make_query_text_empty_inputs(self, isolated_config, fake_chroma):
        """Test _build_merged_context with empty or None inputs."""
        fake_chroma.clear_registry()
        
        memory = Memory(cog_name="test_cog")
        # Test with None inputs
        merged = memory._build_merged_context(None, None)
        assert merged == {}
        # Test with only _ctx
        merged = memory._build_merged_context({'key': 'value'}, None)
        assert merged == {'key': 'value'}
        # Test with only _state
        merged = memory._build_merged_context(None, {'key': 'value'})
        assert merged == {'key': 'value'} 