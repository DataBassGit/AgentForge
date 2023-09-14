from agentforge.llm import LLM
from agentforge.logs.logger_config import Logger
from agentforge.utils.function_utils import Functions


class Agent:

    def __init__(self, log_level="info"):
        """Initializes the Agent, loads the relevant data depending on it's name and sets up the storage and logger"""
        self.agent_name = self.__class__.__name__
        self.data = None
        self.prompt = None
        self.result = None
        self.output = None

        self.functions = Functions()
        self.agent_data = self.functions.agent_utils.load_agent_data(self.agent_name)
        self.storage = self.agent_data['storage']

        self.logger = Logger(name=self.agent_name)
        self.logger.set_level(log_level)

    def run(self, bot_id=None, **kwargs):
        """This is the heart of all Agents, orchestrating the entire workflow from data loading to output generation."""
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
        """Sets the internal 'output' attribute as the internal 'result' attribute by default"""
        self.output = self.result

    def generate_prompt(self, **kwargs):
        """Takes the data previously loaded and processes it to render the prompt being fed to the LLM"""
        # Prompt Template for Rendering
        templates = []

        # Handle system prompt
        system_prompt = self.data['prompts']['System']
        templates.append((system_prompt["template"], system_prompt["vars"]))

        # Remove prompts if there's no corresponding data
        self.functions.prompt_handling.remove_prompt_if_none(self.data['prompts'], self.data)

        # Handle other types of prompts
        other_prompt_types = [prompt_type for prompt_type in self.data['prompts'].keys() if prompt_type != 'System']
        for prompt_type in other_prompt_types:
            templates.extend(self.functions.prompt_handling.handle_prompt_type(self.data['prompts'], prompt_type))

        # Render Prompts
        self.prompt = [
            self.functions.prompt_handling.render_template(template, variables, data=self.data)
            for template, variables in templates
        ]

    def load_additional_data(self):
        """Does nothing by default, it is meant to be overriden by Custom Agents if needed"""
        pass

    def load_agent_data(self, **kwargs):
        """Loads the Agent data and any additional data given to it"""
        self.agent_data = self.functions.agent_utils.load_agent_data(self.agent_name)
        self.data = {'params': self.agent_data.get('params').copy(), 'prompts': self.agent_data['prompts'].copy()}

        # Add any other data needed by the agent from kwargs
        for key in kwargs:
            self.data[key] = kwargs[key]

    def load_data(self, **kwargs):
        """This method is in charge of calling all the relevant load data methods"""
        self.load_agent_data(**kwargs)
        self.load_main_data()
        self.load_additional_data()

    def load_main_data(self):
        """Loads the main data for the Agent, by default it's the Objective and Current Task"""
        self.data['objective'] = self.agent_data.get('objective')
        # self.data['task'] = self.functions.get_current_task()['document']

    def parse_result(self):
        """This method does nothing by default, it is meant to be overridden by SubAgents if needed"""
        pass

    def process_data(self):
        """Does nothing by default, it is meant to be overriden by Custom Agents if needed"""
        pass

    def run_llm(self):
        """Sends the rendered prompt to the LLM and stores the response in the internal result attribute"""
        model: LLM = self.agent_data['llm']
        params = self.agent_data.get("params", {})
        self.result = model.generate_text(self.prompt, **params,).strip()

    def save_result(self):
        """This method saves the LLM Result to memory"""
        params = {'data': [self.result], 'collection_name': 'Results'}
        self.storage.save_memory(params)

    def status(self, msg):
        """Prints a formatted status message to the console"""
        self.functions.printing.print_message(f"\n{self.agent_name} - {msg}")
