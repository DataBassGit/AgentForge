from agentforge.config import Config
from agentforge.utils.logger import Logger
import importlib


class CogArch:
    def __init__(self, name):
        """
        Initializes a CogArch instance with the given name.
        """
        self.name = name
        self.logger = Logger(name=self.name)
        self.config = Config()
        self.agents = {}
        self.context = {}
        self.flow = {}
        self.step_dict = {}

        self.load_flow()
        self.load_agents()
        self.initialize_context()
        self.validate_flow()

    def load_flow(self):
        """
        Loads the flow configuration for the cognitive architecture.
        """
        try:
            self.flow = self.config.load_flow_data(self.name)
        except Exception as e:
            self.logger.log(f"Error loading flow '{self.name}': {e}", level='error')
            raise

    def initialize_context(self):
        """
        Placeholder for initializing the context. Can be overridden by subclasses.
        """
        pass

    def load_agents(self):
        """
        Loads and initializes agents as defined in the flow configuration.
        """
        agents_config = self.flow.get('agents', [])
        if not agents_config:
            error_msg = f"No agents defined in cognitive architecture '{self.name}'."
            self.logger.log(error_msg, level='error')
            raise ValueError(error_msg)

        for agent_info in agents_config:
            agent_name = self.get_agent_name(agent_info)
            agent_class = self.get_agent_class(agent_info, agent_name)
            agent_instance = self.instantiate_agent(agent_class, agent_name)
            self.agents[agent_name] = agent_instance

    def get_agent_name(self, agent_info):
        """
        Extracts and returns the agent name from the agent configuration.
        """
        agent_name = agent_info.get('name')
        if not agent_name:
            error_msg = f"Agent name missing in cognitive architecture '{self.name}'."
            self.logger.log(error_msg, level='error')
            raise ValueError(error_msg)
        return agent_name

    def get_agent_class(self, agent_info, agent_name):
        """
        Imports and returns the agent class based on the provided class path.
        Defaults to the base Agent class if no class path is provided.
        """
        module_path = 'agentforge.agent'
        class_name = 'Agent'

        class_path = agent_info.get('class', '')
        if class_path:
            try:
                # module_path, class_name = class_path.rsplit('.', 1)
                module_path = class_path
                _, class_name = class_path.rsplit('.', 1)
            except Exception as e:
                error_msg = f"Error parsing class path '{class_path}' for agent '{agent_name}': {e}"
                self.logger.log(error_msg, level='error')
                raise ValueError(error_msg)

        try:
            module = importlib.import_module(module_path)
            agent_class = getattr(module, class_name)
            self.logger.log(f"Loaded '{class_name}' from '{module_path}' for agent '{agent_name}'.", level='info')
            return agent_class
        except Exception as e:
            error_msg = f"Error importing agent class '{class_name}' from '{module_path}' for agent '{agent_name}': {e}"
            self.logger.log(error_msg, level='error')
            raise ImportError(error_msg)

    def instantiate_agent(self, agent_class, agent_name):
        """
        Instantiates and returns an agent instance.
        """
        try:
            agent_instance = agent_class(agent_name=agent_name)
            self.logger.log(f"Agent '{agent_name}' instantiated.", level='info')
            return agent_instance
        except Exception as e:
            error_msg = f"Error instantiating agent '{agent_name}': {e}"
            self.logger.log(error_msg, level='error')
            raise RuntimeError(error_msg)

    def validate_flow(self):
        """
        Validates the flow configuration to ensure all agents and steps are properly defined.
        """
        steps = self.flow.get('flow', [])
        if not steps:
            error_msg = f"No flow steps defined for cognitive architecture '{self.name}'."
            self.logger.log(error_msg, level='error')
            raise ValueError(error_msg)

        # Map agent names to steps for quick lookup
        self.step_dict = {}
        for step in steps:
            self.validate_step_structure(step)
            agent_name = step['step']['agent']
            self.check_duplicate_step(agent_name)
            self.step_dict[agent_name] = step
            self.validate_agent_defined(agent_name)
            self.validate_next_agents(step)
            self.validate_condition_agents(step)

        self.logger.log("Flow validation completed successfully.", level='info')

    def validate_step_structure(self, step):
        """
        Validates that each step has the required structure.
        """
        if 'step' not in step or 'agent' not in step['step']:
            error_msg = "Each flow step must contain a 'step' dictionary with an 'agent' key."
            self.logger.log(error_msg, level='error')
            raise ValueError(error_msg)

    def check_duplicate_step(self, agent_name):
        """
        Checks for duplicate steps for the same agent.
        """
        if agent_name in self.step_dict:
            error_msg = f"Duplicate step for agent '{agent_name}'."
            self.logger.log(error_msg, level='error')
            raise ValueError(error_msg)

    def validate_agent_defined(self, agent_name):
        """
        Validates that the agent is defined in the agents list.
        """
        if agent_name not in self.agents:
            error_msg = f"Agent '{agent_name}' in flow is not defined in agents list."
            self.logger.log(error_msg, level='error')
            raise ValueError(error_msg)

    def validate_next_agents(self, step):
        """
        Validates that all 'next' agents are defined.
        """
        step_info = step['step']
        next_agents = step_info.get('next', [])
        if isinstance(next_agents, str):
            next_agents = [next_agents]
        for next_agent in next_agents:
            if next_agent not in self.agents:
                error_msg = f"Next agent '{next_agent}' in step '{step_info['agent']}' is not defined."
                self.logger.log(error_msg, level='error')
                raise ValueError(error_msg)

    def validate_condition_agents(self, step):
        """
        Validates that all agents referenced in conditions are defined.
        """
        step_info = step['step']
        condition = step_info.get('condition')
        if not condition:
            return

        condition_type = condition.get('type')
        if condition_type not in ('expression', 'function', 'variable'):
            error_msg = f"Unsupported condition type '{condition_type}' in agent '{step_info['agent']}'."
            self.logger.log(error_msg, level='error')
            raise ValueError(error_msg)

        # Collect all possible next agents from conditions
        condition_agents = []
        if condition_type == 'variable':
            cases = condition.get('cases', {})
            default_agent = condition.get('default')
            condition_agents.extend(cases.values())
            if default_agent:
                condition_agents.append(default_agent)
        else:
            condition_agents.extend([
                condition.get('on_true'),
                condition.get('on_false')
            ])

        for cond_agent in condition_agents:
            if cond_agent and cond_agent not in self.agents:
                error_msg = f"Condition agent '{cond_agent}' in step '{step_info['agent']}' is not defined."
                self.logger.log(error_msg, level='error')
                raise ValueError(error_msg)

    def run(self, **kwargs):
        """
        Executes the cognitive architecture's flow starting from the first step.
        """
        self.context.update(kwargs)

        # Start execution from the first step
        steps = self.flow.get('flow', [])
        current_step = steps[0]

        while current_step:
            agent_name = current_step['step']['agent']
            self.execute_step(agent_name)

            next_step = self.get_next_step(current_step)
            if next_step:
                current_step = next_step
                continue
            self.logger.log(f"Flow completed at agent '{agent_name}'.", level='info')
            current_step = None  # End the loop

    def execute_step(self, agent_name):
        """
        Executes an agent and updates the context with its output.
        """
        agent_instance = self.agents[agent_name]
        self.logger.log(f"Running agent '{agent_name}'.", level='info')
        agent_input = self.prepare_input(agent_name)
        agent_output = self.run_agent(agent_instance, agent_input)
        self.context[agent_name] = agent_output

    def prepare_input(self, agent_name):
        """
        Prepares the input data for the agent. Can be overridden for custom behavior.
        """
        return self.context

    def run_agent(self, agent_instance, agent_input):
        """
        Runs the agent with the provided input.
        """
        try:
            agent_output = agent_instance.run(**agent_input)
            return agent_output
        except Exception as e:
            error_msg = f"Error running agent '{agent_instance.agent_name}': {e}"
            self.logger.log(error_msg, level='error')
            raise RuntimeError(error_msg)

    def get_next_step(self, current_step):
        """
        Determines the next step based on 'condition' or 'next' in current_step.
        Returns the next step to process or None if there is no next step.
        """
        step_info = current_step['step']
        if 'condition' in step_info:
            next_agent_name = self.evaluate_condition(step_info['condition'])
            next_step = self.step_dict.get(next_agent_name)
            return next_step

        if 'next' in step_info:
            next_agents = step_info.get('next', [])
            if isinstance(next_agents, str):
                next_agents = [next_agents]
            next_agent_name = next_agents[0] if next_agents else None
            if next_agent_name:
                next_step = self.step_dict.get(next_agent_name)
                return next_step

        # No 'next' or 'condition' specified
        return None

    def evaluate_condition(self, condition):
        """
        Evaluates a condition and determines the next agent based on the result.
        """
        condition_type = condition.get('type')
        if condition_type == 'expression':
            return self.evaluate_expression_condition(condition)
        if condition_type == 'function':
            return self.evaluate_function_condition(condition)
        if condition_type == 'variable':
            return self.evaluate_variable_condition(condition)

        error_msg = f"Unsupported condition type '{condition_type}'."
        self.logger.log(error_msg, level='error')
        raise ValueError(error_msg)

    def evaluate_expression_condition(self, condition):
        """
        Evaluates an expression condition.
        """
        expression = condition.get('expression')
        result = self.evaluate_expression(expression)
        return condition.get('on_true') if result else condition.get('on_false')

    def evaluate_function_condition(self, condition):
        """
        Evaluates a function-based condition.
        """
        function_name = condition.get('function')
        function = getattr(self, function_name, None)
        if not function:
            error_msg = f"Condition function '{function_name}' not found."
            self.logger.log(error_msg, level='error')
            raise ValueError(error_msg)

        result = function()
        return condition.get('on_true') if result else condition.get('on_false')

    def evaluate_variable_condition(self, condition):
        """
        Evaluates a condition based on the value of a variable in the context.
        """
        variable_name = condition.get('on')
        variable_value = self.context.get(variable_name)
        cases = condition.get('cases', {})
        default = condition.get('default')
        return cases.get(variable_value, default)

    def evaluate_expression(self, expression):
        """
        Safely evaluates an expression using the context.
        """
        try:
            allowed_names = {}
            eval_context = {}
            eval_context.update(allowed_names)
            eval_context.update(self.context)
            value = eval(expression, {"__builtins__": None}, eval_context)
            return value
        except Exception as e:
            error_msg = f"Error evaluating expression '{expression}': {e}"
            self.logger.log(error_msg, level='error')
            raise RuntimeError(error_msg)
