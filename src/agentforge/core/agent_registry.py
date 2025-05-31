"""
Agent Registry

A lightweight factory for agent class resolution and instantiation.
Extracts agent building logic from Cog to improve separation of concerns.
"""

from typing import Dict
from agentforge.config import Config
from agentforge.agent import Agent
from agentforge.config_structs import CogConfig


class AgentRegistry:
    """
    Factory for building agent instances from cog configuration.
    Handles class resolution, template assignment, and instantiation.
    """

    @staticmethod
    def build_agents(cog_config: CogConfig) -> Dict[str, Agent]:
        """
        Build a mapping of agent IDs to initialized agent instances from cog configuration.
        
        Args:
            cog_config: Structured cog configuration object
            
        Returns:
            Dict[str, Agent]: Mapping of agent IDs to agent instances
        """
        config = Config()
        agents = {}
        
        for agent_def in cog_config.cog.agents:
            agent_id = agent_def.id
            agent_class = AgentRegistry._resolve_agent_class(agent_def, config)
            agent_name = agent_def.template_file or agent_def.id
            agents[agent_id] = agent_class(agent_name=agent_name)
            
        return agents

    @staticmethod
    def _resolve_agent_class(agent_def, config: Config) -> type:
        """
        Resolve and return the agent class for a given agent definition.
        Assumes validation has already been performed by ConfigManager.
        
        Args:
            agent_def: Agent definition from cog config
            config: Config instance for class resolution
            
        Returns:
            type: The resolved agent class
        """
        return config.resolve_class(
            agent_def.type, 
            default_class=Agent,
            context=f"agent '{agent_def.id}'"
        ) 