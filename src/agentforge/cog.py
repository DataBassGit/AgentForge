"""
Cog workflow orchestration module for AgentForge.

The Cog class provides a workflow framework for executing a series of
chained agents based on configurable flow definitions and transitions.
"""

from typing import Any, Dict, List, Optional
from agentforge.config import Config
from agentforge.config_structs.trail_structs import ThoughtTrailEntry
from agentforge.core.agent_runner import AgentRunner
from agentforge.core.config_manager import ConfigManager
from agentforge.core.memory_manager import MemoryManager
from agentforge.core.transition_resolver import TransitionResolver
from agentforge.utils.logger import Logger
from agentforge.utils.parsing_processor import ParsingProcessor
from agentforge.utils.trail_recorder import TrailRecorder


class Cog:
    """
    Orchestrates a workflow of agents based on flow configuration.
    
    Cog reads agent definitions, flow transitions, and memory configurations
    from a YAML file and executes agents in the specified order, handling
    decision-based routing and memory management.
    
    The transition logic has been extracted into a dedicated TransitionResolver
    class to improve testability and separation of concerns.
    """

    def __init__(self, cog_file: str, enable_trail_logging: Optional[bool] = None, log_file: Optional[str] = 'cog'):
        # Set instance variables
        self.cog_file = cog_file  # Store the cog file name for tests and reference
        self.config = Config()
        self.logger = Logger(name='Cog', default_logger=log_file)
        
        # Initialize the config manager and build the configuration
        config_manager = ConfigManager()
        self.cog_config = config_manager.build_cog_config(self.config.data['cogs'][cog_file])
        
        # Create agents dictionary
        self.agents = self._create_agents()
        
        # Initialize core components - pass cog_file string, not logger
        self.mem_mgr = MemoryManager(self.cog_config, cog_file)
        self.agent_runner = AgentRunner()
        self.transition_resolver = TransitionResolver(self.cog_config.cog.flow)
        
        # Initialize trail logging
        if enable_trail_logging is None:
            enable_trail_logging = self.cog_config.cog.trail_logging
        self.trail_recorder = TrailRecorder(self.logger, enabled=enable_trail_logging)
        
        # Initialize state variables
        self.last_executed_agent: Optional[str] = None
        self._reset_context_and_thoughts()

    def _reset_context_and_thoughts(self):
        self.context: dict = {}  # external context (runtime/user input)
        self.state: dict = {}    # internal state (agent-local/internal data)
        self._reset_thought_flow_trail()

    def _reset_thought_flow_trail(self):
        if hasattr(self, 'trail_recorder'):
            self.trail_recorder.reset_trail()

    ##########################################################
    # Section 2: Interface Methods
    ##########################################################

    def get_track_flow_trail(self) -> List[ThoughtTrailEntry]:
        return self.trail_recorder.get_trail()

    ##########################################################
    # Section 3: Agent Creation
    ##########################################################

    def _create_agents(self) -> Dict[str, Any]:
        """Create agent instances from the configuration."""
        agents = {}
        for agent_def in self.cog_config.cog.agents:
            # Create the agent - ConfigManager has already validated the class path
            if agent_def.type:
                agent_class = self.config.resolve_class(agent_def.type, context=f"agent '{agent_def.id}'")
                # For custom agent types, pass the template_file as agent_name if specified, otherwise use the agent id
                agent_name = agent_def.template_file or agent_def.id
                agent = agent_class(agent_name=agent_name)
            else:
                # Use default Agent class with template_file as agent_name if specified, otherwise use the agent id
                from agentforge.agent import Agent
                agent_name = agent_def.template_file or agent_def.id
                agent = Agent(agent_name=agent_name)
            
            agents[agent_def.id] = agent
        
        return agents

    ##########################################################
    # Section 4: Execution
    ##########################################################

    def _execute_flow(self) -> None:
        """
        Execute the cog flow from start to completion.
        Orchestrates agent execution with memory query/update cycles.
        """
        self.logger.log("Starting cog execution", "debug", "Flow")
        
        current_agent_id = self.cog_config.cog.flow.start
        self.last_executed_agent = None
        self.transition_resolver.reset_visit_counts()
        
        while current_agent_id:
            try:
                self.logger.log(f"Processing agent: {current_agent_id}", "debug", "Flow")
                
                # Query memory nodes before agent execution
                self.mem_mgr.query_before(current_agent_id, self.context, self.state)
                
                # Execute the current agent
                agent = self.agents.get(current_agent_id)
                mem = self.mem_mgr.build_mem()
                agent_output = self.agent_runner.run_agent(current_agent_id, agent, self.context, self.state, mem)
                
                # Store agent output in state
                self.state[current_agent_id] = agent_output
                self.last_executed_agent = current_agent_id
                
                # Track output for logging if enabled
                self._track_agent_output(current_agent_id, agent_output)
                
                # Update memory nodes after agent execution
                self.mem_mgr.update_after(current_agent_id, self.context, self.state)
                
                # Determine next agent in flow using the transition resolver
                next_agent_id = self.transition_resolver.get_next_agent(current_agent_id, self.state)
                self.logger.log(f"Next agent: {next_agent_id}", "debug", "Flow")
                
                current_agent_id = next_agent_id
                
            except Exception as e:
                self.logger.log(f"Error during cog execution: {e}", "error", "Flow")
                raise
        self.logger.log("Cog execution completed", "debug", "Flow")

    def _track_agent_output(self, agent_id: str, output: Any) -> None:
        """Track agent output in thought flow trail if logging is enabled."""
        self.trail_recorder.record_agent_output(agent_id, output)

    def run(self, **kwargs: Any) -> Any:
        """
        Execute the cog by iteratively running agents as defined in the flow.
        
        Args:
            **kwargs: Initial context values to provide to the agents
            
        Returns:
            Any: Based on the 'end' keyword in the final transition:
                - If 'end: true', returns the output of the last agent executed
                - If 'end: <agent_id>', returns the output of that specific agent
                - If 'end: <agent_id>.field.subfield', returns that nested value
                - Otherwise, returns the full internal state
        """
        self._reset_context_and_thoughts()
        self.context.update(kwargs)
        self._execute_flow()
        
        # Get the transition for the last executed agent
        if self.last_executed_agent:
            agent_transition = self.transition_resolver._get_agent_transition(self.last_executed_agent)
            
            # Handle the 'end' keyword - check for end transition
            if agent_transition.type == "end" or agent_transition.end:
                # If `end: true`, return the last agent's output
                if agent_transition.end is True:
                    return self.state.get(self.last_executed_agent)
                
                # If end is a string, it could be an agent_id or dot notation
                if isinstance(agent_transition.end, str):
                    # Check if it's just an agent ID
                    if agent_transition.end in self.state:
                        return self.state[agent_transition.end]
                    # Otherwise treat as dot notation in state
                    return ParsingProcessor.get_dot_notated(self.state, agent_transition.end)
        # Default behavior: return the full internal state
        return self.state
