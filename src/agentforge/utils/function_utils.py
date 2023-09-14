from .storage_interface import StorageInterface
from ..logs.logger_config import Logger
from ..config import Config
from .functions.UserInferface import UserInterface
from .functions.Printing import Printing
from .functions.TaskHandling import TaskHandling

from typing import Dict, Any
from termcolor import cprint
from colorama import init

init(autoreset=True)

logger = Logger(name="Function Utils")


class Functions:

    def __init__(self):
        self.config = Config()
        self.storage = StorageInterface()
        self.user_interface = UserInterface()
        self.printing = Printing()
        self.task_handling = TaskHandling()

    @staticmethod
    def get_feedback_from_status_results(status):
        if status is not None:
            completed = status['status']

            if 'not completed' in completed:
                result = status['reason']
            else:
                result = None

            return result

    def load_agent_data(self, agent_name):
        self.config.reload(agent_name)

        defaults = self.config.data['Defaults']
        objective = self.config.data['Objective']

        agent = self.config.agent
        api = agent.get('API', defaults['API'])
        params = agent.get('Params', defaults['Params'])

        # Initialize agent data
        agent_data: Dict[str, Any] = dict(
            name=agent_name,
            llm=self.config.get_llm(api),
            objective=objective,
            prompts=agent['Prompts'],
            params=params,
            storage=StorageInterface().storage_utils,
        )

        return agent_data

    def prepare_objective(self):
        while True:
            user_input = input("\nDefine Objective (leave empty to use defaults): ")
            if user_input.lower() == '':
                return None
            else:
                self.config.data['Objective'] = user_input
                return user_input

    @staticmethod
    def calculate_next_task_order(this_task_order):
        return int(this_task_order) + 1

    @staticmethod
    def handle_prompt_type(prompts, prompt_type):
        """Handle each type of prompt and return template and vars."""
        prompt_data = prompts.get(prompt_type, {})
        if prompt_data:
            return [(prompt_data['template'], prompt_data['vars'])]
        return []

    @staticmethod
    def parse_tool_results(tool_result):
        if isinstance(tool_result, list):
            # Format each search result
            formatted_results = [f"URL: {url}\nDescription: {desc}\n---" for url, desc in tool_result]
            # Join all results into a single string
            final_output = "\n".join(formatted_results)
        else:
            final_output = tool_result

        return final_output

    @staticmethod
    def remove_prompt_if_none(prompts, kwargs):
        prompts_copy = prompts.copy()
        for prompt_type, prompt_data in prompts_copy.items():
            required_vars = prompt_data.get('vars', [])
            # If there are no required vars or all vars are empty, we keep the prompt
            if not required_vars or all(not var for var in required_vars):
                continue
            for var in required_vars:
                if kwargs.get(var) is None:
                    prompts.pop(prompt_type)
                    break  # Exit this loop, the dictionary has been changed

    @staticmethod
    def render_template(template, variables, data):
        temp = template.format(
            **{k: v for k, v in data.items() if k in variables}
        )

        return temp

    def dyna_tool(self, tool_class, payload):
        import importlib
        self.printing.print_message(f"\nRunning {tool_class} ...")

        command = payload['command']['name']
        args = payload['command']['args']
        tool_module = f"agentforge.tools.{tool_class}"

        try:
            tool = importlib.import_module(tool_module)
        except ModuleNotFoundError:
            raise ValueError(
                f"No tool module named '{tool_class}' found. Ensure the module name matches the Script name exactly.")

        # Check if the tool has a class named FileWriter (or any other tool name)
        # If it does, instantiate it, and then use the command method
        # Else, use the standalone function
        if hasattr(tool, tool_class):
            tool_instance = getattr(tool, tool_class)()
            command_func = getattr(tool_instance, command)
        else:
            command_func = getattr(tool, command)

        result = command_func(**args)

        self.printing.print_result(result, f"{tool_class} Result")
        return result

    @staticmethod
    def extract_metadata(data):
        # extract the 'metadatas' key from results
        return data['metadatas'][0][0]

    @staticmethod
    def extract_outermost_brackets(string):
        count = 0
        start_idx = None
        end_idx = None

        for idx, char in enumerate(string):
            if char == '{':
                count += 1
                if count == 1:
                    start_idx = idx
            elif char == '}':
                count -= 1
                if count == 0 and start_idx is not None:
                    end_idx = idx
                    break

        if start_idx is not None and end_idx is not None:
            return string[start_idx:end_idx + 1]
        else:
            return None

    @staticmethod
    def string_to_dictionary(string):
        from ast import literal_eval as leval
        try:
            return leval(string)
        except Exception as e:
            raise ValueError(f"\n\nError while building parsing string to dictionary: {e}")
