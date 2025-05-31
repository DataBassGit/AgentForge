"""Tests for the MemoryManager class."""

import pytest
from agentforge.core.memory_manager import MemoryManager
from agentforge.utils.parsing_processor import ParsingProcessor
from unittest.mock import MagicMock, patch, PropertyMock


def test_memory_manager_initialization(isolated_config):
    """Test that MemoryManager initializes correctly with a cog config."""
    from agentforge.cog import Cog
    cog = Cog("ExampleCog")
    
    # MemoryManager should be initialized
    assert hasattr(cog, 'mem_mgr')
    assert isinstance(cog.mem_mgr, MemoryManager)
    
    # Should have the correct attributes
    assert cog.mem_mgr.cog_name == "ExampleCog"
    assert cog.mem_mgr.cog_config is not None
    assert hasattr(cog.mem_mgr, 'memories')


def test_memory_manager_extract_keys():
    """Test the _extract_keys helper method."""
    context = {"user_input": "hello", "nested": {"key": "value"}}
    state = {"agent_output": "response", "other": {"data": "test"}}
    
    # Test with empty key list - should return merged dict
    result = MemoryManager._extract_keys([], context, state)
    expected = {**state, **context}  # context overwrites state
    assert result == expected
    
    # Test with specific keys
    result = MemoryManager._extract_keys(["user_input", "agent_output"], context, state)
    assert result == {"user_input": "hello", "agent_output": "response"}
    
    # Test with dot notation
    result = MemoryManager._extract_keys(["nested.key", "other.data"], context, state)
    assert result == {"nested.key": "value", "other.data": "test"}
    
    # Test with missing key should raise ValueError
    with pytest.raises(ValueError, match="Key 'missing' not found"):
        MemoryManager._extract_keys(["missing"], context, state)


def test_memory_manager_get_dot_notated():
    """Test the get_dot_notated helper method via ParsingProcessor."""
    # Test data with nested structure
    data = {
        "direct": "value",
        "level1": {
            "simple": "test",
            "level2": {
                "value": "found"
            }
        }
    }
    
    # Test direct key access
    assert ParsingProcessor.get_dot_notated(data, "direct") == "value"
    
    # Test single level dot notation
    assert ParsingProcessor.get_dot_notated(data, "level1.simple") == "test"
    
    # Test multi-level dot notation
    assert ParsingProcessor.get_dot_notated(data, "level1.level2.value") == "found"
    
    # Test missing keys
    assert ParsingProcessor.get_dot_notated(data, "missing") is None
    assert ParsingProcessor.get_dot_notated(data, "level1.missing") is None
    
    # Test non-dict input
    assert ParsingProcessor.get_dot_notated("not a dict", "key") is None


def test_memory_manager_build_mem(example_cog):
    """Test that build_mem returns the correct structure."""
    mem_dict = example_cog.mem_mgr.build_mem()
    
    # Should return a dictionary mapping memory IDs to their stores
    assert isinstance(mem_dict, dict)
    
    # Each value should be a memory store
    for mem_id, store in mem_dict.items():
        assert isinstance(mem_id, str)
        assert hasattr(store, 'update')  # Basic dict-like interface


def test_memory_manager_hooks_called_during_cog_execution(example_cog, monkeypatch):
    """Test that query_before and update_after are called during cog execution."""
    query_calls = []
    update_calls = []
    
    # Mock the memory manager methods to track calls
    original_query = example_cog.mem_mgr.query_before
    original_update = example_cog.mem_mgr.update_after
    
    def mock_query(agent_id, context, state):
        query_calls.append((agent_id, context, state))
        return original_query(agent_id, context, state)
    
    def mock_update(agent_id, context, state):
        update_calls.append((agent_id, context, state))
        return original_update(agent_id, context, state)
    
    monkeypatch.setattr(example_cog.mem_mgr, 'query_before', mock_query)
    monkeypatch.setattr(example_cog.mem_mgr, 'update_after', mock_update)
    
    # Run the cog
    example_cog.run(user_input="test")
    
    # Verify that memory hooks were called for each agent execution
    assert len(query_calls) > 0, "query_before should be called for agents"
    assert len(update_calls) > 0, "update_after should be called for agents"
    
    # Verify the calls have the expected structure
    for agent_id, context, state in query_calls:
        assert isinstance(agent_id, str)
        assert isinstance(context, dict)
        assert isinstance(state, dict)
        
    for agent_id, context, state in update_calls:
        assert isinstance(agent_id, str)
        assert isinstance(context, dict)
        assert isinstance(state, dict) 