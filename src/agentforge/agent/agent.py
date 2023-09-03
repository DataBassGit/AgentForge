from ..llm import LLM
from ..logs.logger_config import Logger
from ..utils.function_utils import Functions


class Agent:

    def __init__(self, log_level="info"):
        """This function Initializes the Agent, it loads the relevant data depending on it's name as well as setting
        up the storage and logger"""
        self.agent_name = self.__class__.__name__
        self.data = None
        self.prompt = None
        self.result = None
        self.output = None

        self.functions = Functions()
        self.agent_data = self.functions.load_agent_data(self.agent_name)
        self.storage = self.agent_data['storage']

        self.logger = Logger(name=self.agent_name)
        self.logger.set_level(log_level)

    def run(self, bot_id=None, **kwargs):
        """This function is the heart of all Agents, it defines how Agents receive and process data"""
        self.status("Running ...")

        self.load_data(**kwargs)
        self.process_data()
        self.generate_prompt()
        self.run_llm()
        self.parse_result()
        self.save_result()
        self.build_output()

        return self.output

    def build_output(self):
        """This function set the output as the result by default"""
        self.output = self.result

    def generate_prompt(self, **kwargs):
        """This function takes the data previously loaded and processes it to render the prompt"""
        # Prompt Template for Rendering
        templates = []

        # Handle system prompt
        system_prompt = self.data['prompts']['System']
        templates.append((system_prompt["template"], system_prompt["vars"]))

        # Remove prompts if there's no corresponding data
        self.functions.remove_prompt_if_none(self.data['prompts'], self.data)

        # Handle other types of prompts
        other_prompt_types = [prompt_type for prompt_type in self.data['prompts'].keys() if prompt_type != 'System']
        for prompt_type in other_prompt_types:
            templates.extend(self.functions.handle_prompt_type(self.data['prompts'], prompt_type))

        # Render Prompts
        self.prompt = [
            self.functions.render_template(template, variables, data=self.data)
            for template, variables in templates
        ]

    def load_additional_data(self):
        """This function does nothing by default, it is meant to be overriden by SubAgents if needed"""
        pass

    def load_agent_data(self, **kwargs):
        """This function loads the Agent data and any additional data given to it"""
        self.agent_data = self.functions.load_agent_data(self.agent_name)

        # The data dict will contain all the data that the agent requires
        self.data = {'params': self.agent_data.get('params').copy(), 'prompts': self.agent_data['prompts'].copy()}

        # Add any other data needed by the agent from kwargs
        for key in kwargs:
            self.data[key] = kwargs[key]

    def load_data(self, **kwargs):
        """This function is in charge of calling all the relevant load data methods"""
        self.load_agent_data(**kwargs)
        self.load_main_data()
        self.load_additional_data()

    def load_main_data(self):
        """This function loads the main data for the Agent, by default it's the Objective and Current Task"""
        self.data['objective'] = self.agent_data.get('objective')
        self.data['task'] = self.functions.get_current_task()['document']

    def parse_result(self):
        """This function simply returns the result by default, it is meant to be overriden by SubAgents if needed"""
        pass

    def process_data(self):
        """This function does nothing by default, it is meant to be overriden by SubAgents if needed"""
        pass

    def run_llm(self):
        """This function sends the rendered prompt to the LLM and returns the model response"""
        model: LLM = self.agent_data['llm']
        params = self.agent_data.get("params", {})
        self.result = model.generate_text(self.prompt, **params,).strip()

    def save_result(self):
        """This function saves the LLM Result to memory"""
        params = {'data': [self.result], 'collection_name': 'Results'}
        self.storage.save_memory(params)

    def status(self, msg):
        self.functions.print_message(f"\n{self.agent_name} - {msg}")
