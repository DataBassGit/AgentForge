"""
Trail recording utility for tracking thought flow in AgentForge.

The TrailRecorder class encapsulates all logic related to tracking agent execution
and outputs in the thought flow trail, including logging functionality.
"""

from typing import List, Optional
from agentforge.config_structs.trail_structs import ThoughtTrailEntry
from agentforge.utils.logger import Logger


class TrailRecorder:
    """Encapsulates thought trail tracking and related logging functionality."""
    
    def __init__(self, enabled: bool = True):
        """
        Initialize the trail recorder.
        
        Args:
            enabled: Whether trail recording is enabled
        """
        self.logger = Logger(name="TrailRecorder", default_logger="trail")
        self.enabled = enabled
        self.trail: List[ThoughtTrailEntry] = []
        self._execution_counter = 0
        
        # TODO: Consider adding max_entries parameter for trail size limits in the future
        # self.max_entries = max_entries
    
    def record_agent_output(self, agent_id: str, output: any, notes: Optional[str] = None, error: Optional[str] = None) -> None:
        """
        Record an agent's output in the trail.
        
        Args:
            agent_id: ID of the agent that produced the output
            output: The agent's output to record
            notes: Optional notes about this execution
            error: Optional error information if the agent failed
        """
        if not self.enabled:
            return
            
        self._execution_counter += 1
        entry = ThoughtTrailEntry(
            agent_id=agent_id,
            output=output,
            notes=notes,
            execution_order=self._execution_counter,
            error=error
        )
        self.trail.append(entry)
        self._log_trail_entry(entry)
        
        # TODO: Implement trail size management if max_entries is added
        # if self.max_entries and len(self.trail) > self.max_entries:
        #     self.trail.pop(0)  # Remove oldest entry
    
    def get_trail(self) -> List[ThoughtTrailEntry]:
        """
        Get a copy of the current trail.
        
        Returns:
            List of ThoughtTrailEntry objects representing the execution trail
        """
        return self.trail.copy()
    
    def reset_trail(self) -> None:
        """Clear the trail and reset counters."""
        self.trail.clear()
        self._execution_counter = 0
    
    def _log_trail_entry(self, entry: ThoughtTrailEntry) -> None:
        """
        Log trail entry to debug output.
        
        Args:
            entry: The trail entry to log
        """
        log_message = f"******\n{entry.agent_id}\n******\n{entry.output}\n******"
        if entry.error:
            log_message += f"\nERROR: {entry.error}"
        
        self.logger.debug(log_message) 