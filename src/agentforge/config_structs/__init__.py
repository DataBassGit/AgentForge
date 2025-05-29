"""
Configuration dataclasses for AgentForge.

This package contains pure dataclass definitions for configuration objects,
extracted from ConfigManager to improve modularity and maintainability.
"""

from .agent_config_structs import (
    PersonaSettings,
    DebugSettings,
    LoggingSettings,
    MiscSettings,
    PathSettings,
    SystemSettings,
    Settings,
    AgentConfig,
)

from .cog_config_structs import (
    CogAgentDef,
    CogMemoryDef,
    CogFlowTransition,
    CogFlow,
    CogDefinition,
    CogConfig,
)

__all__ = [
    # Agent config structs
    "PersonaSettings",
    "DebugSettings", 
    "LoggingSettings",
    "MiscSettings",
    "PathSettings",
    "SystemSettings",
    "Settings",
    "AgentConfig",
    # Cog config structs
    "CogAgentDef",
    "CogMemoryDef",
    "CogFlowTransition",
    "CogFlow",
    "CogDefinition",
    "CogConfig",
] 