"""
Cog configuration dataclasses.

Contains all dataclass definitions related to cog configuration,
including agent definitions, memory configurations, flow definitions, and the main CogConfig object.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Union


@dataclass
class CogAgentDef:
    """Definition of an agent within a cog."""

    id: str
    template_file: str | None = None
    type: str | None = None  # Full class path for custom agent types
    description: str | None = None
    # Additional agent configuration can be added here


@dataclass
class CogMemoryDef:
    """Definition of a memory node within a cog."""

    id: str
    type: str | None = None  # Full class path for memory type
    collection_id: str | None = None
    query_before: Union[str, List[str], None] = None
    query_keys: List[str] = field(default_factory=list)
    update_after: Union[str, List[str], None] = None
    update_keys: List[str] = field(default_factory=list)


@dataclass
class CogFlowTransition:
    """A single flow transition definition."""

    # Can be a string (direct transition), dict (decision), or special end marker
    type: str  # "direct", "decision", "end"
    next_agent: str | None = None  # For direct transitions
    decision_key: str | None = None  # For decision transitions
    decision_map: Dict[str, str] = field(default_factory=dict)  # For decision transitions
    fallback: str | None = None
    max_visits: int | None = None
    end: bool | str = False


@dataclass
class CogFlow:
    """Flow definition for a cog."""

    start: str
    transitions: Dict[str, CogFlowTransition]


@dataclass
class CogDefinition:
    """The core cog definition structure."""

    name: str
    description: str | None = None
    persona: str | None = None  # Persona override for the cog
    trail_logging: bool = True
    agents: List[CogAgentDef] = field(default_factory=list)
    memory: List[CogMemoryDef] = field(default_factory=list)
    flow: CogFlow | None = None
    chat_memory_enabled: bool | None = None
    chat_history_max_results: int | None = None
    chat_history_max_retrieval: int | None = None


@dataclass
class CogConfig:
    """
    Structured configuration object for cogs.

    NOTE: This object should not be mutated in place. For hot-reload support,
    replace the entire object with a new one from ConfigManager.build_cog_config().
    """

    cog: CogDefinition
    # Support for additional top-level fields
    custom_fields: Dict[str, Any] = field(default_factory=dict)
