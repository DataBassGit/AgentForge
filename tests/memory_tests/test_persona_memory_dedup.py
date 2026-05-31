"""
Tests for PersonaMemory deduplication functionality.

This module tests the enhanced PersonaMemory that now checks for exact duplicates
before adding new facts to storage.
"""

from dataclasses import dataclass
from typing import Any
from unittest.mock import Mock, patch

import pytest

from agentforge.storage.persona_memory import PersonaMemory


@dataclass
class PersonaMemorySubject:
    """PersonaMemory plus its mocked production agents."""

    memory: PersonaMemory
    retrieval_agent: Any
    narrative_agent: Any
    update_agent: Any


class TestPersonaMemoryDeduplication:
    """Test suite for PersonaMemory deduplication functionality."""

    @pytest.fixture
    def persona_memory(self, isolated_config, fake_chroma) -> PersonaMemorySubject:
        """Create a PersonaMemory instance with mocked dependencies using conftest infrastructure."""
        fake_chroma.clear_registry()

        with patch("agentforge.storage.persona_memory.Agent") as mock_agent_class:
            retrieval_mock: Any = Mock()
            narrative_mock: Any = Mock()
            update_mock: Any = Mock()
            agent_map = {
                "persona_retrieval_agent": retrieval_mock,
                "persona_narrative_agent": narrative_mock,
                "persona_update_agent": update_mock,
            }
            mock_agent_class.side_effect = lambda agent_name: agent_map[agent_name]
            memory = PersonaMemory("test_cog", collection_id="test_facts", persona=None)

        retrieval_mock.run.return_value = {"queries": ["existing facts"]}
        narrative_mock.run.return_value = {"narrative": "Test narrative"}
        update_mock.run.return_value = {"action": "add", "new_facts": [{"fact": "Test fact"}]}

        memory.retrieval_agent = retrieval_mock
        memory.narrative_agent = narrative_mock
        memory.update_agent = update_mock
        return PersonaMemorySubject(
            memory=memory, retrieval_agent=retrieval_mock, narrative_agent=narrative_mock, update_agent=update_mock
        )

    def test_exact_duplicate_exists_true(self, persona_memory: PersonaMemorySubject) -> None:
        """Test that _exact_duplicate_exists returns True for exact matches."""
        memory = persona_memory.memory
        memory.storage.save_to_storage(
            collection_name=memory.collection_name,
            data=["User prefers Python programming", "Other fact"],
            ids=["1", "2"],
            metadata=[{}, {}],
        )

        result = memory._is_duplicate_fact("User prefers Python programming")
        assert result is True

    def test_exact_duplicate_exists_false(self, persona_memory: PersonaMemorySubject) -> None:
        """Test that _exact_duplicate_exists returns False for no matches."""
        memory = persona_memory.memory
        memory.storage.save_to_storage(
            collection_name=memory.collection_name,
            data=["User likes Java", "User enjoys coding"],
            ids=["1", "2"],
            metadata=[{}, {}],
        )

        result = memory._is_duplicate_fact("User prefers Python programming")
        assert result is False

    def test_exact_duplicate_exists_text_match(self, persona_memory: PersonaMemorySubject) -> None:
        """Test that _exact_duplicate_exists detects text matches even with whitespace."""
        memory = persona_memory.memory
        memory.storage.save_to_storage(
            collection_name=memory.collection_name,
            data=["  User prefers Python programming  ", "Other fact"],
            ids=["1", "2"],
            metadata=[{}, {}],
        )

        result = memory._is_duplicate_fact("User prefers Python programming")
        assert result is True

    def test_exact_duplicate_exists_error_handling(self, persona_memory: PersonaMemorySubject) -> None:
        """Test that _exact_duplicate_exists handles errors gracefully."""
        memory = persona_memory.memory
        with patch.object(memory.storage, "query_storage", side_effect=Exception("Storage error")):
            result = memory._is_duplicate_fact("Any fact")
            assert result is False

    def test_update_memory_skips_duplicate_add(self, persona_memory: PersonaMemorySubject) -> None:
        """Test that update_memory skips adding duplicate facts."""
        memory = persona_memory.memory
        persona_memory.retrieval_agent.run.return_value = {"queries": ["existing facts"]}
        persona_memory.update_agent.run.return_value = {
            "action": "add",
            "new_facts": [{"fact": "User enjoys classical music"}],
        }

        memory.storage.save_to_storage(
            collection_name=memory.collection_name, data=["User enjoys classical music"], metadata=[{}]
        )

        initial_count = memory.storage.count_collection(memory.collection_name)
        test_data = {"user_preference": "classical music"}

        memory.update_memory(["user_preference"], _ctx=test_data, _state={})

        final_count = memory.storage.count_collection(memory.collection_name)
        assert final_count == initial_count

    def test_update_memory_adds_non_duplicate(self, persona_memory: PersonaMemorySubject) -> None:
        """Test that update_memory adds facts that are not duplicates."""
        memory = persona_memory.memory
        persona_memory.retrieval_agent.run.return_value = {"queries": ["existing facts"]}
        persona_memory.update_agent.run.return_value = {
            "action": "add",
            "new_facts": [{"fact": "User enjoys classical music"}],
        }

        memory.storage.save_to_storage(
            collection_name=memory.collection_name,
            data=["User likes jazz", "User prefers morning meetings"],
            metadata=[{}, {}],
        )

        initial_count = memory.storage.count_collection(memory.collection_name)
        test_data = {"user_preference": "classical music"}

        memory.update_memory(["user_preference"], _ctx=test_data, _state={})

        final_count = memory.storage.count_collection(memory.collection_name)
        assert final_count == initial_count + 1

        all_facts = memory.storage.query_storage(collection_name=memory.collection_name, num_results=final_count)
        assert "User enjoys classical music" in all_facts["documents"]

    def test_update_memory_update_action_not_affected(self, persona_memory: PersonaMemorySubject) -> None:
        """Test that update action (not add) is not affected by deduplication."""
        memory = persona_memory.memory
        persona_memory.retrieval_agent.run.return_value = {"queries": ["music preferences"]}
        persona_memory.update_agent.run.return_value = {
            "action": "update",
            "new_facts": [{"fact": "User now prefers jazz music", "supersedes": ["fact123"]}],
        }

        memory.storage.save_to_storage(
            collection_name=memory.collection_name,
            data=["User likes rock music"],
            ids=["fact123"],
            metadata=[{"type": "preference"}],
        )

        initial_count = memory.storage.count_collection(memory.collection_name)
        test_data = {"user_preference": "jazz music"}

        memory.update_memory(["user_preference"], _ctx=test_data, _state={})

        final_count = memory.storage.count_collection(memory.collection_name)
        assert final_count == initial_count + 1

        all_facts = memory.storage.query_storage(collection_name=memory.collection_name, num_results=final_count)
        assert "User now prefers jazz music" in all_facts["documents"]
