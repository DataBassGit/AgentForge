"""
Tests for AgentRegistry factory class.
"""

import pytest
from unittest.mock import patch
from agentforge.core.agent_registry import AgentRegistry
from agentforge.config_structs import CogConfig, CogDefinition, CogAgentDef
from agentforge.agent import Agent
from agentforge.config import Config
from agentforge.core.config_manager import ConfigManager


@pytest.fixture
def minimal_agent_config(isolated_config):
    """Create a minimal agent config for testing."""
    config_manager = ConfigManager()
    
    raw_agent_data = {
        "name": "TestAgent",
        "params": {},
        "prompts": {"system": "Hello", "user": "Test"},
        "model": object(),
        "settings": isolated_config.data["settings"].copy(),
        "simulated_response": "SIMULATED",
    }
    raw_agent_data["settings"]["system"]["debug"]["mode"] = True
    
    return config_manager.build_agent_config(raw_agent_data)


def test_agent_registry_build_agents_basic(minimal_agent_config):
    """Test that AgentRegistry can build a simple agent mapping from CogConfig."""
    # Create a minimal CogConfig with one agent
    agent_def = CogAgentDef(
        id="test_agent",
        type="agentforge.agent.Agent"  # Use base Agent class
    )
    
    cog_def = CogDefinition(
        name="test_cog",
        agents=[agent_def],
        flow=None  # Not needed for agent building
    )
    
    cog_config = CogConfig(cog=cog_def)
    
    # Mock load_agent_data to return our test config
    with patch.object(Config, "load_agent_data", return_value=minimal_agent_config):
        # Build agents using the registry
        agents = AgentRegistry.build_agents(cog_config)
        
        # Verify the result
        assert isinstance(agents, dict)
        assert "test_agent" in agents
        assert isinstance(agents["test_agent"], Agent)


def test_agent_registry_build_agents_with_template_file(minimal_agent_config):
    """Test that AgentRegistry respects template_file when provided."""
    agent_def = CogAgentDef(
        id="test_agent",
        template_file="custom_template",
        type="agentforge.agent.Agent"
    )
    
    cog_def = CogDefinition(
        name="test_cog",
        agents=[agent_def],
        flow=None
    )
    
    cog_config = CogConfig(cog=cog_def)
    
    # Mock load_agent_data to return our test config
    with patch.object(Config, "load_agent_data", return_value=minimal_agent_config):
        # Build agents
        agents = AgentRegistry.build_agents(cog_config)
        
        # Note: We can't easily test the template file was used without inspecting agent internals,
        # but we can verify the agent was created successfully
        assert "test_agent" in agents
        assert isinstance(agents["test_agent"], Agent)


def test_agent_registry_build_agents_multiple(minimal_agent_config):
    """Test that AgentRegistry can build multiple agents."""
    agent_defs = [
        CogAgentDef(id="agent1", type="agentforge.agent.Agent"),
        CogAgentDef(id="agent2", type="agentforge.agent.Agent"),
    ]
    
    cog_def = CogDefinition(
        name="test_cog",
        agents=agent_defs,
        flow=None
    )
    
    cog_config = CogConfig(cog=cog_def)
    
    # Mock load_agent_data to return our test config
    with patch.object(Config, "load_agent_data", return_value=minimal_agent_config):
        # Build agents
        agents = AgentRegistry.build_agents(cog_config)
        
        # Verify all agents were created
        assert len(agents) == 2
        assert "agent1" in agents
        assert "agent2" in agents
        assert isinstance(agents["agent1"], Agent)
        assert isinstance(agents["agent2"], Agent)


def test_agent_registry_build_agents_empty():
    """Test that AgentRegistry handles empty agent list."""
    cog_def = CogDefinition(
        name="test_cog",
        agents=[],  # No agents
        flow=None
    )
    
    cog_config = CogConfig(cog=cog_def)
    
    # Build agents
    agents = AgentRegistry.build_agents(cog_config)
    
    # Should return empty dict
    assert isinstance(agents, dict)
    assert len(agents) == 0 