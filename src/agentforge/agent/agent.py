from ..llm import LLM
from ..logs.logger_config import Logger
from ..utils.function_utils import Functions

from termcolor import cprint
from colorama import init
init(autoreset=True)


class Agent:

    _agent_name = None

    def __init__(self, agent_name=None, log_level="info"):
        """This function Initializes the Agent, it loads the relevant data depending on it's name as well as setting
        up the storage and logger"""
        if agent_name is None:
            self._agent_name = self.__class__.__name__

        self.functions = Functions()
        self.agent_data = self.functions.load_agent_data(self._agent_name)
        self.storage = self.agent_data['storage']

        self.logger = Logger(name=self._agent_name)
        self.logger.set_level(log_level)

    def run(self, bot_id=None, **kwargs):
        """This function is the heart of all Agents, it defines how Agents receive and process data"""
        agent_name = self.__class__.__name__

        cprint(f"\n{agent_name} - Running Agent...", 'red', attrs=['bold'])

        data = self.load_data(**kwargs)
        self.process_data(data)
        prompt = self.generate_prompt(**data)
        result = self.run_llm(prompt)
        parsed_data = self.parse_result(result=result, data=data)
        self.save_parsed_result(parsed_data)
        output = self.build_output(parsed_data)

        cprint(f"\n{agent_name} - Agent Done...\n", 'red', attrs=['bold'])

        return output

    def build_output(self, parsed_data):
        """This function returns the parsed_data by default, it is meant to be overriden by SubAgents if needed"""
        return parsed_data

    def generate_prompt(self, **kwargs):
        """This function takes the data previously loaded and process it to render the prompt"""
        # Load Prompts from Persona Data
        prompts = kwargs['prompts']
        templates = []

        # Handle system prompt
        system_prompt = prompts['System']
        templates.append((system_prompt["template"], system_prompt["vars"]))

        # Remove prompts if there's no corresponding data in kwargs
        self.functions.remove_prompt_if_none(prompts, kwargs)

        # Handle other types of prompts
        other_prompt_types = [prompt_type for prompt_type in prompts.keys() if prompt_type != 'System']
        for prompt_type in other_prompt_types:
            templates.extend(self.functions.handle_prompt_type(prompts, prompt_type))

        # Render Prompts
        prompts = [
            self.functions.render_template(template, variables, data=kwargs)
            for template, variables in templates
        ]

        self.logger.log(f"Prompt:\n{prompts}", 'debug')

        return prompts

    def load_additional_data(self, data):
        """This function does nothing by default, it is meant to be overriden by SubAgents if needed"""
        pass

    def load_agent_data(self, **kwargs):
        """This function loads the Agent data and any additional data given to it"""
        self.agent_data = self.functions.load_agent_data(self._agent_name)  # Is this needed if it's called in INIT?

        # The data dict will contain all the data that the agent requires
        data = {'params': self.agent_data.get('params').copy(), 'prompts': self.agent_data['prompts'].copy()}

        # Add any other data needed by the agent from kwargs
        for key in kwargs:
            data[key] = kwargs[key]

        return data

    def load_data(self, **kwargs):
        """This function is in charge of calling all the relevant load data methods"""
        data = self.load_agent_data(**kwargs)

        self.load_main_data(data)
        self.load_additional_data(data)

        return data

    def load_main_data(self, data):
        """This function loads the main data for the Agent, by default it's the Objective and Current Task"""
        data['objective'] = self.agent_data.get('objective')
        data['task'] = self.functions.get_current_task()['document']

    def parse_result(self, result, **kwargs):
        """This function simply returns the result by default, it is meant to be overriden by SubAgents if needed"""
        return result

    def process_data(self, data):
        """This function is for processing the data before being rendering the prompt"""
        self.functions.set_task_order(data)
        self.functions.show_task(data)

    def run_llm(self, prompt):
        """This function sends the rendered prompt to the LLM and returns the model response"""
        model: LLM = self.agent_data['llm']
        params = self.agent_data.get("params", {})
        return model.generate_text(prompt, **params,).strip()

    def save_parsed_result(self, result):
        """This function saves the LLM Result to memory"""
        params = {'data': [result], 'collection_name': 'Results'}
        self.storage.save_memory(params)
