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

    def run(self, **kwargs):
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

    def generate_prompt(self):
        """Takes the data previously loaded and processes it to render the prompt being fed to the LLM."""
        rendered_prompts = []

        for prompt_template in self.data['prompts'].values():
            template = self.functions.prompt_handling.handle_prompt_template(prompt_template, self.data)
            if template:  # If the template is valid (i.e., not None)
                rendered_prompt = self.functions.prompt_handling.render_prompt_template(template, self.data)
                rendered_prompts.append(rendered_prompt)

        self.prompt = rendered_prompts

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
        self.load_agent_type_data()
        self.load_main_data()
        self.load_additional_data()

    def load_main_data(self):
        """Loads the main data for the Agent; by default, it's the Objective"""
        self.data['objective'] = self.agent_data['settings']['directives'].get('Objective', None)

    def load_agent_type_data(self):
        """Does nothing by default, it is meant to be overriden by Custom Agent Types if needed"""
        pass

    def parse_result(self):
        """This method does nothing by default, it is meant to be overridden by Custom Agents if needed"""
        pass

    def process_data(self):
        """Does nothing by default, it is meant to be overriden by Custom Agents if needed"""
        pass

    def run_llm(self):
        """Sends the rendered prompt to the LLM and stores the response in the internal result attribute"""
        model: LLM = self.agent_data['llm']
        params = self.agent_data.get("params", {})
        self.result = model.generate_text(self.prompt, **params).strip()

    def save_result(self):
        """This method saves the LLM Result to memory"""
        params = {'data': [self.result], 'collection_name': 'Results'}
        self.storage.save_memory(params)

    def status(self, msg):
        """Prints a formatted status message to the console"""
        self.functions.printing.print_message(f"\n{self.agent_name} - {msg}")
