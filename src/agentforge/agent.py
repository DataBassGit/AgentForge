from typing import Any, Dict, List, Optional
from agentforge.llm import LLM
from agentforge.utils.Logger import Logger
from .config import Config
from agentforge.utils.PromptHandling import PromptHandling


class Agent:
    def __init__(self, agent_name: Optional[str] = None):
        """
        Initializes an Agent instance, setting up its name, logger, data attributes, and agent-specific configurations.
        It attempts to load the agent's configuration data and storage settings.

        Args:
            agent_name (Optional[str]): The name of the agent. If not provided, the class name is used.
        """
        # Set agent_name to the provided name or default to the class name
        self.agent_name: str = agent_name if agent_name is not None else self.__class__.__name__

        # Initialize logger with the agent's name
        self.logger: Logger = Logger(name=self.agent_name)

        # Initialize other configurations and handlers
        self.config = Config()
        self.prompt_handling = PromptHandling()

        # Initialize data attributes
        self.data: Dict[str, Any] = {}
        self.prompt: Optional[List[str]] = None
        self.result: Optional[str] = None
        self.output: Optional[str] = None

        # Initialize agent_data if it hasn't been set already
        if not hasattr(self, 'agent_data'):  # Prevent re-initialization
            self.agent_data: Optional[Dict[str, Any]] = None

    def run(self, **kwargs: Any) -> Optional[str]:
        """
        Orchestrates the execution of the agent's workflow: loading data, processing data, generating prompts,
        running language models, parsing results, saving results, and building the output.

        Parameters:
            **kwargs (Any): Keyword arguments that will form part of the agent's data.

        Returns:
            Optional[str]: The output generated by the agent or None if an error occurred during execution.
        """
        try:
            self.logger.log(f"\n{self.agent_name} - Running...", 'info')
            self.load_data(**kwargs)
            self.process_data()
            self.generate_prompt()
            self.run_llm()
            self.parse_result()
            self.save_to_storage()
            self.build_output()
            self.data = {}
            self.logger.log(f"\n{self.agent_name} - Done!", 'info')
        except Exception as e:
            self.logger.log(f"Agent execution failed: {e}", 'error')
            return None

        return self.output

    def load_data(self, **kwargs: Any) -> None:
        """
        Central method for data loading that orchestrates the loading of agent data, persona-specific data,
        storage data, and any additional data.

        Parameters:
            **kwargs (Any): Keyword arguments for additional data loading.
        """
        self.load_agent_data()
        self.load_persona_data()
        self.resolve_storage()
        self.load_from_storage()
        self.load_additional_data()
        self.load_kwargs(**kwargs)

    def load_agent_data(self) -> None:
        """
        Loads the agent's configuration data including parameters and prompts.
        """
        try:
            self.agent_data = self.config.load_agent_data(self.agent_name).copy()
            self.data.update({
                'params': self.agent_data.get('params').copy(),
                'prompts': self.agent_data['prompts'].copy()
            })
        except Exception as e:
            self.logger.log(f"Error loading agent data: {e}", 'error')

    def load_persona_data(self) -> None:
        """
        Loads the persona data for the agent if available. Will not load persona data if personas is disabled in system settings.
        """
        if not self.agent_data['settings']['system'].get('PersonasEnabled'):
            return None

        persona = self.agent_data.get('persona', {})
        if persona:
            for key in persona:
                self.data[key.lower()] = persona[key]

    def load_from_storage(self) -> None:
        """
        Placeholder for loading from storage. Meant to be overridden by custom agents to implement specific loading
        from storage logic.

        Notes:
            - The storage instance for an Agent is set at self.agent_data['storage'].
            - The 'StorageEnabled' setting is the system.yaml file must be set to 'True'.
        """
        pass

    def load_additional_data(self) -> None:
        """
        Placeholder for loading additional data. Meant to be overridden by custom agents as needed.
        """
        pass

    def load_kwargs(self, **kwargs: Any) -> None:
        """
        Loads the variables passed to the agent as data.

        Parameters:
            **kwargs (Any): Additional keyword arguments to be merged into the agent's data.
        """
        try:
            for key in kwargs:
                self.data[key] = kwargs[key]
        except Exception as e:
            self.logger.log(f"Error loading kwargs: {e}", 'error')

    def process_data(self) -> None:
        """
        Placeholder for data processing. Meant to be overridden by custom agents for specific data processing needs.
        """
        pass

    def generate_prompt(self) -> None:
        """
        Generates the prompts for the language model based on the template data.
        """
        try:
            prompts = self.data.get('prompts', {})

            self.prompt_handling.check_prompt_format(prompts)
            rendered_prompts = self.prompt_handling.render_prompts(prompts, self.data)
            self.prompt_handling.validate_rendered_prompts(rendered_prompts)
            self.prompt = rendered_prompts  # {'System': '...', 'User': '...'}
        except Exception as e:
            self.logger.log(f"Error generating prompt: {e}", 'error')
            self.prompt = None
            raise

    def run_llm(self) -> None:
        """
        Executes the language model generation with the generated prompt(s) and any specified parameters.
        """
        try:
            model: LLM = self.agent_data['llm']
            params: Dict[str, Any] = self.agent_data.get("params", {})
            params['agent_name'] = self.agent_name
            self.result = model.generate_text(self.prompt, **params).strip()
        except Exception as e:
            self.logger.log(f"Error running LLM: {e}", 'error')
            self.result = None

    def resolve_storage(self):
        """
        Initializes the storage for the agent, if storage is enabled.

        Returns: None
        """
        if not self.agent_data['settings']['system'].get('StorageEnabled'):
            self.agent_data['storage'] = None
            return None

        from .utils.ChromaUtils import ChromaUtils
        self.agent_data['storage'] = ChromaUtils(self.agent_data['persona']['Name'])

    def parse_result(self) -> None:
        """
        Placeholder for result parsing. Meant to be overridden by custom agents to implement specific result parsing
        logic.
        """
        pass

    def save_to_storage(self) -> None:
        """
        Placeholder for saving results to storage. Meant to be overridden by custom agents to implement specific
        saving to storage logic.

        Notes:
            - The storage instance for an Agent is set at self.agent_data['storage'].
            - The 'StorageEnabled' setting is the system.yaml file must be set to 'True'.
        """
        pass

    def build_output(self) -> None:
        """
        Constructs the output from the result. This method can be overridden by subclasses to customize the output.
        By default, it simply sets the output as the model's response.
        """
        self.output = self.result
