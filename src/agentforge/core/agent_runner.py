"""
AgentRunner

A helper class for executing individual agents with retry logic and error handling.
Extracts agent execution concerns from Cog to improve separation of responsibilities.
"""

from typing import Any, Optional
from agentforge.utils.logger import Logger


class AgentRunner:
    """
    Handles the execution of individual agents with retry logic and logging.
    Encapsulates agent invocation concerns separate from flow orchestration.
    """

    def __init__(self):
        """Initialize AgentRunner with its own logger instance."""
        self.logger = Logger("AgentRunner", "agent_runner")

    def run_agent(self, agent_id: str, agent, context: dict, state: dict, memory: dict, max_attempts: int = 3) -> Any:
        """
        Execute an agent with retry logic.
        
        Args:
            agent_id: The ID of the agent to execute (for logging)
            agent: The agent instance to execute
            context: External context data to pass to agent
            state: Internal state data to pass to agent
            memory: Memory data to pass to agent
            max_attempts: Maximum number of retry attempts
            
        Returns:
            Agent output on success
            
        Raises:
            Exception: If agent fails after max attempts
        """
        attempts = 0

        while attempts < max_attempts:
            attempts += 1
            self.logger.debug(f"Executing agent '{agent_id}' (attempt {attempts}/{max_attempts})")
            
            agent_output = agent.run(_ctx=context, _state=state, _mem=memory)
            
            if not agent_output:
                self.logger.warning(f"No output from agent '{agent_id}', retrying... (Attempt {attempts})")
                continue
                
            self.logger.debug(f"Agent '{agent_id}' executed successfully on attempt {attempts}")
            return agent_output

        self.logger.error(f"Max attempts reached for agent '{agent_id}' with no valid output.")
        raise Exception(f"Failed to get valid response from {agent_id}. We recommend checking the agent's input/output logs.") 