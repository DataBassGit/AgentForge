"""
Test to verify PersonaMemory agents receive _ctx and _state correctly.

This test confirms that the memory system standardization refactor successfully
passes _ctx and _state to specialized agents within PersonaMemory operations.
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


class TestPersonaMemoryAgentInterface:
    """Test suite to verify PersonaMemory agent interface uses _ctx and _state."""

    @pytest.fixture
    def persona_memory(self, isolated_config, fake_chroma) -> PersonaMemorySubject:
        """Create a PersonaMemory instance with mocked agent attributes."""
        fake_chroma.clear_registry()
        memory = PersonaMemory(cog_name="test_cog", persona="TestPersona")

        retrieval_mock: Any = Mock()
        narrative_mock: Any = Mock()
        update_mock: Any = Mock()
        retrieval_mock.run.return_value = {"queries": ["test query"]}
        narrative_mock.run.return_value = {"narrative": "Test narrative"}
        update_mock.run.return_value = {"action": "add", "new_facts": [{"fact": "Test fact"}]}

        memory.retrieval_agent = retrieval_mock
        memory.narrative_agent = narrative_mock
        memory.update_agent = update_mock
        return PersonaMemorySubject(
            memory=memory, retrieval_agent=retrieval_mock, narrative_agent=narrative_mock, update_agent=update_mock
        )

    def test_retrieval_agent_receives_ctx_parameter(self, persona_memory: PersonaMemorySubject) -> None:
        """Test that retrieval agent receives _ctx parameter."""
        memory = persona_memory.memory
        persona_memory.retrieval_agent.run.return_value = {"queries": ["test query"]}

        with patch.object(memory.storage, "query_storage") as mock_query:
            mock_query.return_value = {"documents": []}
            test_context = {"user_input": "Hello, how are you?"}

            memory.query_memory(query_keys=None, _ctx=test_context, _state={})

            persona_memory.retrieval_agent.run.assert_called_once()
            call_kwargs = persona_memory.retrieval_agent.run.call_args[1]
            assert "_ctx" in call_kwargs, "Retrieval agent should receive _ctx parameter"
            assert "context" not in call_kwargs, "Old 'context' parameter should not be present"
            ctx_value = call_kwargs["_ctx"]
            assert isinstance(ctx_value, dict), "_ctx should be a dict"
            assert "user_input" in ctx_value or "user_input" in str(ctx_value)

    def test_narrative_agent_receives_ctx_parameter(self, persona_memory: PersonaMemorySubject) -> None:
        """Test that narrative agent receives _ctx parameter."""
        memory = persona_memory.memory
        persona_memory.retrieval_agent.run.return_value = {"queries": ["test query"]}
        persona_memory.narrative_agent.run.return_value = {"narrative": "Test narrative"}

        with patch.object(memory.storage, "query_storage") as mock_query:
            mock_query.return_value = {"documents": ["Test fact"], "ids": ["1"], "metadatas": [{}]}
            test_context = {"user_input": "Tell me about preferences"}

            memory.query_memory(query_keys=None, _ctx=test_context, _state={})

            persona_memory.narrative_agent.run.assert_called_once()
            call_kwargs = persona_memory.narrative_agent.run.call_args[1]
            assert "_ctx" in call_kwargs, "Narrative agent should receive _ctx parameter"
            assert "context" not in call_kwargs, "Old 'context' parameter should not be present"
            ctx_value = call_kwargs["_ctx"]
            assert isinstance(ctx_value, dict), "_ctx should be a dict"
            assert "user_input" in ctx_value or "user_input" in str(ctx_value)

    def test_update_agent_receives_ctx_parameter(self, persona_memory: PersonaMemorySubject) -> None:
        """Test that update agent receives _ctx parameter."""
        memory = persona_memory.memory
        persona_memory.retrieval_agent.run.return_value = {"queries": ["test query"]}
        persona_memory.update_agent.run.return_value = {"action": "add", "new_facts": [{"fact": "User prefers Python"}]}

        with patch.object(memory.storage, "query_storage") as mock_query:
            mock_query.return_value = {"documents": []}
            with patch.object(memory.storage, "save_to_storage"):
                test_context = {
                    "external": {"user_input": "I love Python programming"},
                    "internal": {"understand": {"insights": "User expressed language preference"}},
                }

                memory.update_memory(update_keys=None, _ctx=test_context, _state={})

                persona_memory.update_agent.run.assert_called_once()
                call_kwargs = persona_memory.update_agent.run.call_args[1]
                assert "_ctx" in call_kwargs, "Update agent should receive _ctx parameter"
                assert "context" not in call_kwargs, "Old 'context' parameter should not be present"
                ctx_value = call_kwargs["_ctx"]
                assert isinstance(ctx_value, dict), "_ctx should be a dict"
                assert "user_input" in str(ctx_value), "_ctx should contain the test context data"
                assert "insights" in str(ctx_value), "_ctx should contain internal context data"

    def test_template_compatibility_verification(self, persona_memory: PersonaMemorySubject) -> None:
        """
        Verify that the agent calls work with existing prompt templates.

        This test confirms that the _ctx parameter aligns with template expectations
        like {_ctx} placeholders in persona agent prompts.
        """
        comprehensive_context = {
            "external": {"user_input": "What are my preferences?", "session_id": "test123"},
            "internal": {
                "understand": {
                    "insights": "User is asking about stored preferences",
                    "user_intent": "Information retrieval",
                    "persona_relevant": "Query relates to user's stored data",
                }
            },
        }
        agent_calls: dict[str, dict[str, Any]] = {}
        memory = persona_memory.memory

        def capture_calls(agent_name: str):
            def capture(**kwargs: Any) -> dict[str, Any]:
                agent_calls[agent_name] = kwargs
                if agent_name == "retrieval_agent":
                    return {"queries": ["test query"]}
                if agent_name == "narrative_agent":
                    return {"narrative": "Test narrative"}
                if agent_name == "update_agent":
                    return {"action": "none"}
                return {}

            return capture

        persona_memory.retrieval_agent.run.side_effect = capture_calls("retrieval_agent")
        persona_memory.narrative_agent.run.side_effect = capture_calls("narrative_agent")
        persona_memory.update_agent.run.side_effect = capture_calls("update_agent")

        with patch.object(memory.storage, "query_storage") as mock_query:
            mock_query.return_value = {"documents": ["Some fact"]}

            memory.query_memory(query_keys=None, _ctx=comprehensive_context, _state={})
            memory.update_memory(update_keys=None, _ctx=comprehensive_context, _state={})

            for agent_name, call_kwargs in agent_calls.items():
                assert "_ctx" in call_kwargs, f"{agent_name} should receive _ctx"
                assert "context" not in call_kwargs, f"{agent_name} should not receive old 'context' param"
                ctx_content = call_kwargs["_ctx"]
                assert isinstance(ctx_content, dict), f"{agent_name} _ctx should be a dict"
                assert "external" in ctx_content, f"{agent_name} _ctx should have external section"
                assert "internal" in ctx_content, f"{agent_name} _ctx should have internal section"
                assert "user_input" in str(ctx_content), f"{agent_name} _ctx should contain user input"
                assert "insights" in str(ctx_content), f"{agent_name} _ctx should contain insights"
                user_input_count = str(ctx_content).count("What are my preferences?")
                assert user_input_count == 1, f"{agent_name} _ctx should have no duplicated content"
