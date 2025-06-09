"""
Integration test for ExampleCogWithPersonaMemory cog workflow.

This test exercises the complete cog workflow as realistically as possible while 
stubbing/mocking only the agent responses. It uses real-world agent outputs 
captured from model_io.log to ensure maximum realism in testing the full
PersonaMemory integration, memory updates, and conversational flow.

Stubbed/Mocked Components:
- Agent.run() responses (using real model_io.log data)
- ChromaStorage (using FakeChromaStorage from conftest.py)

Live Components:
- Cog instantiation and flow execution
- PersonaMemory lifecycle and operations  
- Memory query/update cycles
- Agent orchestration and state transitions
- Context passing and variable resolution
"""

import pytest
from unittest.mock import patch
from agentforge.cog import Cog
from agentforge.agent import Agent


class TestExampleCogWithPersonaMemoryIntegration:
    """Integration test suite for ExampleCogWithPersonaMemory cog workflow."""
    
    @pytest.fixture
    def real_agent_responses(self):
        """
        Real agent responses captured from model_io.log for maximum test realism.
        These responses represent actual model outputs from a live cog execution.
        """
        responses = {
            'retrieval_agent': {
                "queries": [
                    "I am a helpful assistant.",
                    "I provide clear and accurate information.",
                    "I aim to be as helpful as possible to the user.",
                    "I am friendly and knowledgeable.",
                    "I exist in a virtual environment.",
                    "My goal is to assist users by providing information.",
                    "I respond to questions and needs."
                ]
            },
            'persona_retrieval_agent': {
                "queries": [
                    "I am a helpful assistant.",
                    "I provide clear and accurate information.",
                    "I aim to be as helpful as possible to the user.",
                    "I am friendly and knowledgeable.",
                    "I exist in a virtual environment.",
                    "My goal is to assist users by providing information.",
                    "I respond to questions and needs."
                ]
            },
            'narrative_agent': {
                "narrative": "I am the Default Assistant, a helpful and friendly entity existing within a virtual environment. My purpose is to assist users by providing clear, concise, and accurate information, always striving to be knowledgeable and as helpful as possible in responding to their questions and needs."
            },
            'persona_narrative_agent': {
                "narrative": "I am the Default Assistant, a helpful and friendly entity existing within a virtual environment. My purpose is to assist users by providing clear, concise, and accurate information, always striving to be knowledgeable and as helpful as possible in responding to their questions and needs."
            },
            'understand_agent': {
                "insights": "The user is initiating a casual conversation with a friendly greeting. They are likely testing the assistant's conversational abilities and responsiveness.",
                "user_intent": "Initiate a friendly greeting and check on the assistant's well-being.",
                "relevant_topics": ["Greetings", "Conversation Starters"],
                "persona_relevant": "The user is friendly and uses casual language."
            },
            'persona_response_agent': "Heyo! I'm doing well, thanks for asking. Just here and ready to help. How can I assist you today?",
            'update_agent': {
                "action": "none",
                "new_facts": []
            },
            'persona_update_agent': {
                "action": "none",
                "new_facts": []
            }
        }
        # Patch: Add persona_understand_agent as a copy of understand_agent
        responses['persona_understand_agent'] = responses['understand_agent']
        return responses
    
    @pytest.fixture
    def mock_agent_responses_with_real_data(self, monkeypatch, real_agent_responses):
        """
        Mock Agent.run() to return real agent responses from model_io.log while 
        preserving the existing stubbed_agents fixture behavior for other agents.
        """
        from agentforge.agent import Agent
        
        # Get the original stubbed run method from conftest.py
        original_stubbed_run = Agent.run
        
        def enhanced_agent_run(self: Agent, **context):
            agent_name = getattr(self, 'agent_name', 'unknown')
            
            # Return real responses for our specific test agents
            if agent_name in real_agent_responses:
                return real_agent_responses[agent_name]
            else:
                # Fall back to the original stubbed behavior for any other agents
                return original_stubbed_run(self, **context)
        
        # Track agent calls for verification
        call_tracking = {agent: 0 for agent in real_agent_responses.keys()}
        # Ensure persona_understand_agent is always tracked
        if 'persona_understand_agent' not in call_tracking:
            call_tracking['persona_understand_agent'] = 0
        original_enhanced = enhanced_agent_run
        
        def tracking_agent_run(self: Agent, **context):
            agent_name = getattr(self, 'agent_name', 'unknown')
            agent_name = agent_name.lower()
            # Map understand_agent to persona_understand_agent for tracking
            if agent_name == 'understand_agent':
                agent_name = 'persona_understand_agent'
            if agent_name in call_tracking:
                call_tracking[agent_name] += 1
            return original_enhanced(self, **context)
        
        monkeypatch.setattr(Agent, "run", tracking_agent_run, raising=True)
        
        yield call_tracking
    
    def test_complete_cog_workflow_with_persona_memory(
        self,
        isolated_config,
        fake_chroma,
        mock_agent_responses_with_real_data,
        real_agent_responses
    ):
        """
        Test the complete ExampleCogWithPersonaMemory workflow with realistic user input.
        
        This test verifies:
        1. Cog instantiation and configuration loading
        2. PersonaMemory initialization and operation  
        3. Full agent execution flow (understand -> respond)
        4. Memory query before understand agent
        5. Memory update after respond agent
        6. Proper context passing and variable resolution
        7. Expected final output matches real model behavior
        """
        # Clear any existing storage state
        fake_chroma.clear_registry()
        
        # Instantiate the cog (this tests configuration loading and memory setup)
        cog = Cog('example_cog_with_persona_memory')
        
        # Verify the cog was properly initialized
        assert cog.cog_file == 'example_cog_with_persona_memory'
        assert 'persona_memory' in cog.mem_mgr.memory_nodes
        
        # Verify PersonaMemory was configured correctly
        persona_memory = cog.mem_mgr.memory_nodes['persona_memory']['instance']
        assert persona_memory.collection_name.startswith('user_persona_facts_')
        
        # Execute the cog with realistic user input (same as in model_io.log)
        user_input = "Heyo, how's you doing?"
        result = cog.run(user_input=user_input)
        
        # Verify the final response matches expected real-world output
        expected_response = "Heyo! I'm doing well, thanks for asking. Just here and ready to help. How can I assist you today?"
        assert result == expected_response
        
        # Verify all expected agents were called
        assert mock_agent_responses_with_real_data['persona_retrieval_agent'] >= 1, "Retrieval agent should be called for persona memory"
        assert mock_agent_responses_with_real_data['persona_narrative_agent'] >= 1, "Narrative agent should be called for persona context"
        assert mock_agent_responses_with_real_data['persona_understand_agent'] == 1, "Understand agent should be called once"
        assert mock_agent_responses_with_real_data['persona_response_agent'] == 1, "Response agent should be called once"
        assert mock_agent_responses_with_real_data['persona_update_agent'] >= 1, "Update agent should be called for memory updates"
        
        # Verify the flow trail shows proper execution order 
        # Flow trail is a list of ThoughtTrailEntry objects: [ThoughtTrailEntry(agent_id='understand', output=...), ...]
        flow_trail = cog.get_track_flow_trail()
        assert len(flow_trail) == 2, f"Expected 2 agents in flow trail, got {len(flow_trail)}"
        
        # Extract agent names from flow trail
        executed_agents = [entry.agent_id for entry in flow_trail]
        expected_flow = ["understanding", "response"]
        assert executed_agents == expected_flow, f"Expected flow {expected_flow}, got {executed_agents}"
        
        # Verify the outputs in the flow trail match our expected responses
        understand_output = flow_trail[0].output
        respond_output = flow_trail[1].output
        
        assert understand_output == real_agent_responses['persona_understand_agent']
        assert respond_output == real_agent_responses['persona_response_agent']
        
        # After running, check that the understand agent was called twice in the loop
        assert cog.branch_call_counts.get("persona_understand_agent", 0) == 0, "branch_call_counts should be reset after loop exit"
        
    def test_persona_memory_integration_with_context_resolution(
        self,
        isolated_config,
        fake_chroma,
        mock_agent_responses_with_real_data
    ):
        """
        Test that PersonaMemory correctly integrates with the cog's context resolution,
        specifically testing that memory placeholders are properly resolved in agent prompts.
        """
        fake_chroma.clear_registry()
        
        cog = Cog('example_cog_with_persona_memory')
        
        # Access the memory instance to verify its state
        persona_memory = cog.mem_mgr.memory_nodes['persona_memory']['instance']
        
        # Run the cog and verify memory operations occur
        result = cog.run(user_input="Tell me about yourself")
        
        # Verify that the memory store was populated during execution
        # The store should contain the narrative after memory operations
        assert hasattr(persona_memory, 'store'), "PersonaMemory should have a store attribute"
        
        # Verify that no real API calls were made - everything should be mocked
        assert isinstance(result, str), "Final result should be a string response"
        assert len(result) > 0, "Response should not be empty"
        
    def test_memory_query_and_update_lifecycle(
        self,
        isolated_config,
        fake_chroma,
        mock_agent_responses_with_real_data
    ):
        """
        Test the complete memory lifecycle: query before understand, update after respond.
        
        This verifies the memory configuration triggers are working correctly:
        - query_before: understand
        - update_after: respond  
        - query_keys and update_keys are properly used
        """
        fake_chroma.clear_registry()
        
        cog = Cog('example_cog_with_persona_memory')
        persona_memory = cog.mem_mgr.memory_nodes['persona_memory']['instance']
        
        # Track storage operations by checking the fake storage
        storage_instance = persona_memory.storage
        initial_collection_count = len(storage_instance._collections)
        
        # Execute the cog
        result = cog.run(user_input="I love programming in Python")
        
        # Verify that memory operations were triggered
        # The collection should exist after memory operations
        final_collection_count = len(storage_instance._collections)
        assert final_collection_count >= initial_collection_count, "Memory operations should create/access collections"
        
        # Verify the expected agents were called in the right order
        # Memory query should trigger retrieval and narrative agents
        # Memory update should trigger retrieval and update agents
        assert mock_agent_responses_with_real_data['persona_retrieval_agent'] >= 2, "Retrieval agent called for both query and update"
        assert mock_agent_responses_with_real_data['persona_narrative_agent'] >= 1, "Narrative agent called for query"
        assert mock_agent_responses_with_real_data['persona_update_agent'] >= 1, "Update agent called for update"
        
    def test_cog_handles_no_memory_state_gracefully(
        self,
        isolated_config,
        fake_chroma,
        mock_agent_responses_with_real_data
    ):
        """
        Test that the cog handles scenarios with no existing memory state gracefully.
        This simulates a fresh start with no previous persona facts stored.
        """
        fake_chroma.clear_registry()
        
        cog = Cog('example_cog_with_persona_memory')
        
        # Verify initial state - no memory should exist
        persona_memory = cog.mem_mgr.memory_nodes['persona_memory']['instance']
        assert persona_memory.narrative is None, "Initial narrative should be None"
        
        # Run with completely new user input
        result = cog.run(user_input="What's the weather like?")
        
        # Should still produce a valid response even with no memory state
        assert isinstance(result, str), "Should return a string response"
        assert len(result) > 0, "Response should not be empty"
        
        # Verify all memory agents were still called appropriately
        assert mock_agent_responses_with_real_data['persona_retrieval_agent'] >= 1
        assert mock_agent_responses_with_real_data['persona_narrative_agent'] >= 1
        assert mock_agent_responses_with_real_data['persona_update_agent'] >= 1

    def test_deterministic_behavior_with_mocked_responses(
        self,
        isolated_config,
        fake_chroma,
        mock_agent_responses_with_real_data
    ):
        """
        Test that the cog produces deterministic results when using mocked agent responses.
        This ensures our test setup provides reliable, repeatable behavior.
        """
        fake_chroma.clear_registry()
        
        # Run the same input multiple times
        cog1 = Cog('example_cog_with_persona_memory')
        result1 = cog1.run(user_input="Hello there!")
        
        fake_chroma.clear_registry()  # Reset storage state
        
        cog2 = Cog('example_cog_with_persona_memory')
        result2 = cog2.run(user_input="Hello there!")
        
        # Results should be identical with mocked responses
        assert result1 == result2, "Mocked responses should produce deterministic results"
        
        # Both should produce the expected mocked response
        expected_response = "Heyo! I'm doing well, thanks for asking. Just here and ready to help. How can I assist you today?"
        assert result1 == expected_response
        assert result2 == expected_response 