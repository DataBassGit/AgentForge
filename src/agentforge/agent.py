from agentforge.llm import LLM
from agentforge.utils.functions.Logger import Logger
from agentforge.utils.function_utils import Functions


class Agent:
    def __init__(self):
        """
        Initializes an Agent instance, setting up its name, logger, data attributes, and agent-specific configurations.
        It attempts to load the agent's configuration data and storage settings.
        """
        self.agent_name = self.__class__.__name__
        self.logger = Logger(name=self.agent_name)

        self.data: dict = {}
        self.prompt = None
        self.result = None
        self.output = None
        # self.storage = None

        if not hasattr(self, 'agent_data'):  # Prevent re-initialization
            self.agent_data = None

        try:
            self.functions = Functions()
            # self.storage = self.functions.agent_utils.get_storage()

        except Exception as e:
            self.logger.log(f"Error during initialization of {self.agent_name}: {e}", 'error')

    def run(self, **kwargs):
        """
        Orchestrates the execution of the agent's workflow: loading data, processing data, generating prompts,
        running language models, parsing results, saving results, and building the output.

        Parameters:
            **kwargs: Keyword arguments that can be used for loading data.

        Returns:
            The output generated by the agent or None if an error occurred during execution.
        """
        try:
            self.logger.log(f"\n{self.agent_name} - Running...", 'info')
            self.load_data(**kwargs)
            self.process_data()
            self.generate_prompt()
            self.run_llm()
            self.parse_result()
            self.save_result()
            self.build_output()
            self.data = {}
            self.logger.log(f"\n{self.agent_name} - Done!", 'info')
        except Exception as e:
            self.logger.log(f"Error running agent: {e}", 'error')
            return None

        return self.output

    def load_data(self, **kwargs):
        """
        Central method for data loading that orchestrates the loading of agent data, type-specific data, main data,
        and any additional data.

        Parameters:
            **kwargs: Keyword arguments for additional data loading.
        """
        self.load_kwargs(**kwargs)
        self.load_agent_data()
        self.load_persona_data()
        self.load_additional_data()

    def load_kwargs(self, **kwargs):
        """
        Loads the variables passed to the agent as data.

        Parameters:
            **kwargs: Additional keyword arguments to be merged into the agent's data.
        """
        try:
            for key in kwargs:
                self.data[key] = kwargs[key]
        except Exception as e:
            self.logger.log(f"Error loading kwargs: {e}", 'error')

    def load_agent_data(self, **kwargs):
        """
        Loads the agent's configuration data including parameters and prompts.
        """
        try:
            self.agent_data = self.functions.agent_utils.load_agent_data(self.agent_name).copy()
            self.data.update({
                'params': self.agent_data.get('params').copy(),
                'prompts': self.agent_data['prompts'].copy()
            })

        except Exception as e:
            self.logger.log(f"Error loading agent data: {e}", 'error')

    def load_additional_data(self, **kwargs):
        """
        Placeholder for loading additional data. Meant to be overridden by custom agents as needed.
        """
        pass

    def load_persona_data(self):
        """
        Loads the persona data for the agent if available.
        """
        persona = self.agent_data.get('persona', None)
        if persona:
            for key in persona:
                self.data[key.lower()] = persona[key]

    def process_data(self, **kwargs):
        """
        Placeholder for data processing. Meant to be overridden by custom agents for specific data processing needs.
        """
        pass

    def generate_prompt(self, **kwargs):
        """
        Generates the prompt(s) for the language model based on template data. It handles the rendering of prompt
        templates and aggregates them into a list.
        """
        try:
            rendered_prompts = []
            for prompt_template in self.data['prompts'].values():
                template = self.functions.prompt_handling.handle_prompt_template(prompt_template, self.data)
                if template:
                    rendered_prompt = self.functions.prompt_handling.render_prompt_template(template, self.data)
                    rendered_prompts.append(rendered_prompt)

            self.prompt = rendered_prompts
        except Exception as e:
            self.logger.log(f"Error generating prompt: {e}", 'error')
            self.prompt = None

    def run_llm(self, **kwargs):
        """
        Executes the language model generation with the generated prompt(s) and any specified parameters.
        """
        try:
            model: LLM = self.agent_data['llm']
            params = self.agent_data.get("params", {})
            params['agent_name'] = self.agent_name
            self.result = model.generate_text(self.prompt, **params).strip()
        except Exception as e:
            self.logger.log(f"Error running LLM: {e}", 'error')
            self.result = None

    def parse_result(self, **kwargs):
        """
        Placeholder for result parsing. Meant to be overridden by custom agents to implement specific result parsing
        logic.
        """
        pass

    def save_result(self, **kwargs):
        """
        Placeholder for result saving. Meant to be overridden by custom agents to implement specific result saving
        logic.
        """
        pass

    def build_output(self, **kwargs):
        """
        Constructs the output from the result. This method can be overridden by subclasses to customize the output.
        """
        self.output = self.result
