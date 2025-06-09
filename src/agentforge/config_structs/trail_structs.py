"""
Trail-related dataclass definitions for AgentForge.

Contains dataclasses for thought trail tracking and related functionality.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, Union


@dataclass
class ThoughtTrailEntry:
    """A single entry in the thought flow trail."""
    agent_id: str
    output: Any
    timestamp: Optional[datetime] = None
    unix_timestamp: Optional[float] = None
    notes: Optional[str] = None
    execution_order: Optional[int] = None
    error: Optional[Union[str, Exception]] = None
    
    def __post_init__(self):
        """Auto-generate timestamps if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.unix_timestamp is None:
            self.unix_timestamp = self.timestamp.timestamp() 