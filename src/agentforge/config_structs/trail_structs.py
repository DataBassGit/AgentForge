"""
Trail-related dataclass definitions for AgentForge.

Contains dataclasses for thought trail tracking and related functionality.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Union


@dataclass
class ThoughtTrailEntry:
    """A single entry in the thought flow trail."""

    agent_id: str
    output: Any
    timestamp: datetime | None = None
    unix_timestamp: float | None = None
    notes: str | None = None
    execution_order: int | None = None
    error: Union[str, Exception] | None = None

    def __post_init__(self):
        """Auto-generate timestamps if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.unix_timestamp is None:
            self.unix_timestamp = self.timestamp.timestamp()
