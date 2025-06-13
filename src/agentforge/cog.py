"""
Cog workflow orchestration module for AgentForge.

The Cog class provides a workflow framework for executing a series of
chained agents based on configurable flow definitions and transitions.
"""

from typing import Any, List, Optional
from agentforge.config import Config
from agentforge.config_structs.trail_structs import ThoughtTrailEntry
from agentforge.core.agent_registry import AgentRegistry
from agentforge.core.agent_runner import AgentRunner
from agentforge.core.memory_manager import MemoryManager
from agentforge.core.transition_resolver import TransitionResolver
from agentforge.utils.logger import Logger
from agentforge.utils.parsing_processor import ParsingProcessor
from agentforge.core.trail_recorder import TrailRecorder


class Cog:
    """
    Orchestrates a workflow of agents based on flow configuration.
    
    Cog reads agent definitions, flow transitions, and memory configurations
    from a YAML file and executes agents in the specified order, handling
    decision-based routing and memory management.
    
    The workflow follows a template method pattern with clear separation of
    concerns across semantic sections for improved maintainability and testing.
    """

    def __init__(self, cog_file: str, enable_trail_logging: Optional[bool] = None, log_file: Optional[str] = 'cog'):
        """
        Initialize a Cog instance with necessary configurations and services.
        
        Args:
            cog_file: Name of the cog configuration file
            enable_trail_logging: Override for trail logging setting. Uses config default if None.
            log_file: Name of the log file. Defaults to 'cog'.
        """
        self.cog_file = cog_file
        self.config = Config()
        self.logger = Logger(name='Cog', default_logger=log_file)
        
        # Initialize core configurations
        self._initialize_cog_config()
        self._initialize_core_services()
        self._initialize_trail_logging(enable_trail_logging)
        
        # Initialize execution state
        self.last_executed_agent: Optional[str] = None
        self.branch_call_counts: dict = {}
        self._reset_execution_state()

    # ---------------------------------
    # Configuration & Initialization
    # ---------------------------------

    def _initialize_cog_config(self) -> None:
        """Load and build the cog configuration from the config file."""
        self.cog_config = self.config.load_cog_data(self.cog_file)

    def _initialize_core_services(self) -> None:
        """Initialize all core service components."""
        # Create agents using AgentRegistry
        self.agents = AgentRegistry.build_agents(self.cog_config)
        
        # Initialize core components
        self.mem_mgr = MemoryManager(self.cog_config, self.cog_file)
        self.agent_runner = AgentRunner()
        self.transition_resolver = TransitionResolver(self.cog_config.cog.flow)

    def _initialize_trail_logging(self, enable_trail_logging: Optional[bool]) -> None:
        """Initialize trail logging with appropriate configuration."""
        if enable_trail_logging is None:
            enable_trail_logging = self.cog_config.cog.trail_logging
        self.trail_recorder = TrailRecorder(enabled=enable_trail_logging)

    # ---------------------------------
    # Public Interface
    # ---------------------------------

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
        try:
            self.logger.info(f"Running cog '{self.cog_file}'...")
            # Load chat history with the initial user context so semantic search can use it
            self.mem_mgr.load_chat(_ctx=kwargs, _state={})
            self._execute_workflow(**kwargs)
            result = self._process_execution_result()
            self.logger.info(f"Cog '{self.cog_file}' completed successfully!")
            self.mem_mgr.record_chat(self.context, result)
            return result
        except Exception as e:
            self.logger.error(f"Cog execution failed: {e}")
            raise

    def get_track_flow_trail(self) -> List[ThoughtTrailEntry]:
        """
        Get the trail of agent executions for this cog run.
        
        Returns:
            List of ThoughtTrailEntry objects representing the execution trail
        """
        return self.trail_recorder.get_trail()

    # ---------------------------------
    # State Management
    # ---------------------------------

    def _reset_execution_state(self) -> None:
        """Reset all execution state for a fresh run."""
        self.context: dict = {}  # external context (runtime/user input)
        self.state: dict = {}    # internal state (agent-local/internal data)
        self.branch_call_counts: dict = {}
        self._reset_trail_logging()

    def _reset_trail_logging(self) -> None:
        """Reset trail logging for a new execution."""
        if hasattr(self, 'trail_recorder'):
            self.trail_recorder.reset_trail()

    def _prepare_execution_state(self, **kwargs: Any) -> None:
        """Prepare execution state with provided context."""
        self._reset_execution_state()
        self.context.update(kwargs)
        # Allow custom context loading
        self.load_additional_context(**kwargs)

    def _update_agent_state(self, agent_id: str, output: Any) -> None:
        """Update internal state with agent output."""
        self.state[agent_id] = output
        self.last_executed_agent = agent_id

    # ---------------------------------
    # Flow Execution
    # ---------------------------------

    def _execute_workflow(self, **kwargs: Any) -> None:
        """
        Execute the complete cog workflow from start to completion.
        Template method that orchestrates the entire execution flow.
        """
        self._prepare_execution_state(**kwargs)
        self._execute_agent_flow()

    def _execute_agent_flow(self) -> None:
        """
        Execute the main agent flow from start to completion.
        Orchestrates agent execution with transition resolution.
        """
        self.logger.log("Starting cog execution", "debug", "Flow")
        
        current_agent_id = self.cog_config.cog.flow.start
        self.last_executed_agent = None
        self.transition_resolver.reset_visit_counts()
        
        while current_agent_id:
                self.logger.log(f"Processing agent: {current_agent_id}", "debug", "Flow")
                
                # Execute single agent cycle
                current_agent_id = self._execute_single_agent_cycle(current_agent_id)
                
        self.logger.log("Cog execution completed", "debug", "Flow")

    def _execute_single_agent_cycle(self, agent_id: str) -> Optional[str]:
        """
        Execute a complete cycle for a single agent.
        
        Args:
            agent_id: The ID of the agent to execute
            
        Returns:
            The ID of the next agent to execute, or None if flow should end
        """
        # Handle pre-execution operations
        self._prepare_agent_execution(agent_id)
        
        # Execute the agent
        agent_output = self._execute_agent(agent_id)
        
        # Handle post-execution operations
        self._finalize_agent_execution(agent_id, agent_output)
        
        # Determine next agent in flow
        return self._determine_next_agent(agent_id)

    def _determine_next_agent(self, current_agent_id: str) -> Optional[str]:
        """
        Determine the next agent in the flow based on transition rules.
        
        Args:
            current_agent_id: The ID of the current agent
            
        Returns:
            The ID of the next agent, or None if flow should end
        """
        next_agent_id = self.transition_resolver.get_next_agent(current_agent_id, self.state)
        self.logger.log(f"Next agent: {next_agent_id}", "debug", "Flow")
        if next_agent_id != current_agent_id:
            self._reset_branch_counts()
        return next_agent_id

    # ---------------------------------
    # Agent Execution
    # ---------------------------------

    def _prepare_agent_execution(self, agent_id: str) -> None:
        """
        Prepare for agent execution by handling pre-execution operations.
        
        Args:
            agent_id: The ID of the agent to prepare for execution
        """
        # Call pre-execution hook
        self.pre_agent_execution(agent_id)
        
        # Handle memory operations before agent execution
        self._handle_pre_execution_memory(agent_id)

    def _execute_agent(self, agent_id: str) -> Any:
        """
        Execute a single agent and return its output.
        
        Args:
            agent_id: The ID of the agent to execute
            
        Returns:
            The output from the agent execution
        """
        agent = self.agents.get(agent_id)
        mem = self.mem_mgr.build_mem()
        output = self.agent_runner.run_agent(agent_id, agent, self.context, self.state, mem)
        self.branch_call_counts[agent_id] = self.branch_call_counts.get(agent_id, 0) + 1
        return output

    def _finalize_agent_execution(self, agent_id: str, output: Any) -> None:
        """
        Finalize agent execution by handling post-execution operations.
        
        Args:
            agent_id: The ID of the executed agent
            output: The output from the agent execution
        """
        # Process agent output
        processed_output = self.process_agent_output(agent_id, output)
        
        # Update agent state
        self._update_agent_state(agent_id, processed_output)
        
        # Track output for logging if enabled
        self._track_agent_output(agent_id, processed_output)
        
        # Handle memory operations after agent execution
        self._handle_post_execution_memory(agent_id)
        
        # Call post-execution hook
        self.post_agent_execution(agent_id, processed_output)

    def _track_agent_output(self, agent_id: str, output: Any) -> None:
        """Track agent output in thought flow trail if logging is enabled."""
        self.trail_recorder.record_agent_output(agent_id, output)

    def _handle_execution_error(self, agent_id: Optional[str], error: Exception) -> None:
        """
        Extension point for custom error handling.
        This method is not called automatically - subclasses can call it when needed.
        
        Args:
            agent_id: The ID of the agent that failed, if available
            error: The exception that occurred
        """
        self.logger.log(f"Error during cog execution: {error}", "error", "Flow")

    # ---------------------------------
    # Memory Management
    # ---------------------------------

    def _handle_pre_execution_memory(self, agent_id: str) -> None:
        """
        Handle memory operations before agent execution.
        
        Args:
            agent_id: The ID of the agent about to be executed
        """
        self.mem_mgr.query_before(agent_id, self.context, self.state)

    def _handle_post_execution_memory(self, agent_id: str) -> None:
        """
        Handle memory operations after agent execution.
        
        Args:
            agent_id: The ID of the agent that was executed
        """
        self.mem_mgr.update_after(agent_id, self.context, self.state)

    # ---------------------------------
    # Result Processing
    # ---------------------------------

    def _process_execution_result(self) -> Any:
        """
        Process and return the final execution result based on end conditions.
        
        Returns:
            The processed result based on end transition configuration
        """
        if not self.last_executed_agent:
            return self.state
            
        agent_transition = self.transition_resolver._get_agent_transition(self.last_executed_agent)
        
        # Handle the 'end' keyword - check for end transition
        if agent_transition.type == "end" or agent_transition.end:
            return self._extract_end_result(agent_transition)
            
        # Default behavior: return the full internal state
        return self.state

    def _extract_end_result(self, agent_transition) -> Any:
        """
        Extract the final result based on end transition configuration.
        
        Args:
            agent_transition: The transition configuration for the final agent
            
        Returns:
            The extracted result based on end configuration
        """
        # If `end: true`, return the last agent's output
        if agent_transition.end is True:
            return self.state.get(self.last_executed_agent)
        
        # If end is a string, it could be an agent_id or dot notation
        if isinstance(agent_transition.end, str):
            # Check if it's just an agent ID
            if agent_transition.end in self.state:
                return self.state[agent_transition.end]
            # Otherwise treat as dot notation in state
            return self._get_nested_result(agent_transition.end)
            
        return self.state.get(self.last_executed_agent)

    def _get_nested_result(self, path: str) -> Any:
        """
        Extract nested result using dot notation.
        
        Args:
            path: Dot notation path to extract from state
            
        Returns:
            The value at the specified path
        """
        return ParsingProcessor.get_dot_notated(self.state, path)

    # ---------------------------------
    # Extension Points
    # ---------------------------------

    def load_additional_context(self, **kwargs: Any) -> None:
        """
        Load custom additional context for the cog execution.
        Override this method in subclasses to load custom context data.
        
        Args:
            **kwargs: Context data to potentially augment
        """
        pass

    def process_agent_output(self, agent_id: str, output: Any) -> Any:
        """
        Process agent output before storing in state.
        Override this method in subclasses to implement custom output processing.
        
        Args:
            agent_id: The ID of the agent that produced the output
            output: The raw output from the agent
            
        Returns:
            The processed output to store in state
        """
        return output

    def pre_agent_execution(self, agent_id: str) -> None:
        """
        Hook called before each agent execution.
        Override this method in subclasses for custom pre-execution logic.
        
        Args:
            agent_id: The ID of the agent about to be executed
        """
        pass

    def post_agent_execution(self, agent_id: str, output: Any) -> None:
        """
        Hook called after each agent execution.
        Override this method in subclasses for custom post-execution logic.
        
        Args:
            agent_id: The ID of the agent that was executed
            output: The output from the agent execution
        """
        pass

    def _reset_branch_counts(self):
        self.branch_call_counts.clear()
