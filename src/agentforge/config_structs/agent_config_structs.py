"""
Agent configuration dataclasses.

Contains all dataclass definitions related to agent configuration,
including settings structures and the main AgentConfig object.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class PersonaSettings:
    """Persona configuration from system settings."""
    enabled: bool = True
    name: str = "default_assistant"
    static_char_cap: int = 8000


@dataclass
class DebugSettings:
    """Debug configuration from system settings."""
    mode: bool = False
    save_memory: bool = False
    simulated_response: str = "Text designed to simulate an LLM response for debugging purposes without invoking the model."


@dataclass
class LoggingSettings:
    """Logging configuration from system settings."""
    enabled: bool = True
    console_level: str = "warning"
    folder: str = "./logs"
    files: Dict[str, str] = field(default_factory=dict)


@dataclass
class MiscSettings:
    """Miscellaneous system settings."""
    on_the_fly: bool = True


@dataclass
class PathSettings:
    """System file path settings."""
    files: str = "./files"


@dataclass
class SystemSettings:
    """System settings structure from settings/system.yaml."""
    persona: PersonaSettings
    debug: DebugSettings
    logging: LoggingSettings
    misc: MiscSettings
    paths: PathSettings


@dataclass
class Settings:
    """Complete settings structure containing system, models, and storage."""
    system: SystemSettings
    models: Dict[str, Any] = field(default_factory=dict)
    storage: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentConfig:
    """
    Structured configuration object for agents.
    
    NOTE: This object should not be mutated in place. For hot-reload support,
    replace the entire object with a new one from ConfigManager.build_agent_config().
    """
    name: str
    settings: Settings
    model: Any
    params: Dict[str, Any]
    prompts: Dict[str, Any]
    persona: Optional[Dict[str, Any]] = None
    simulated_response: Optional[str] = None
    parse_response_as: Optional[str] = None
    # Support for additional custom fields from YAML
    custom_fields: Dict[str, Any] = field(default_factory=dict) 