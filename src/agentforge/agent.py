from .config import Config
from agentforge.apis.base_api import BaseModel
from agentforge.utils.logger import Logger
from agentforge.utils.prompt_processor import PromptProcessor
from typing import Any, Dict, Optional


class Agent:
    def __init__(self, agent_name: Optional[str] = None, log_file: Optional[str] = 'AgentForge'):
        """
        Initializes an Agent instance, setting up its name, logger, data attributes, and agent-specific configurations.
        It attempts to load the agent's configuration data and storage settings.

        Args:
            agent_name (Optional[str]): The name of the agent. If not provided, the class name is used.
            log_file (Optional[str]): The name of the log file for the agent. If not provided, AgentForge.log is used.
        """
        # Set agent_name to the provided name or default to the class name
        self.agent_name: str = agent_name if agent_name is not None else self.__class__.__name__

        # Initialize logger with the agent's name
        self.logger: Logger = Logger(self.agent_name, log_file)

        # Initialize configurations and handlers
        self.config = Config()
        self.prompt_processor = PromptProcessor()

        # Initialize data attributes
        self.agent_data: Optional[Dict[str, Any]] = None
        self.persona: Optional[Dict[str, Any]] = None
        self.model: Optional[BaseModel] = None
        self.prompt_template: Optional[Dict[str, Any]] = None
        self.template_data: Dict[str, Any] = {}
        self.prompt: Optional[Dict[str]] = None
        self.result: Optional[str] = None
        self.output: Optional[str] = None

        # Load and validate agent data during initialization
        self.initialize_agent_config()

    # ---------------------------------
    # Execution
    # ---------------------------------

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
            self.logger.info(f"{self.agent_name} - Running...")
            self.load_data(**kwargs)
            self.process_data()
            self.render_prompt()
            self.run_llm()
            self.parse_result()
            self.save_to_storage()
            self.build_output()
            self.logger.info(f"{self.agent_name} - Done!")
        except Exception as e:
            self.logger.error(f"Agent execution failed: {e}")
            return None
        return self.output

    # ---------------------------------
    # Configuration Loading
    # ---------------------------------

    def initialize_agent_config(self) -> None:
        """
        Loads the agent's configuration data and resolves it's storage.
        """
        self.load_agent_data()
        self.load_prompt_template()
        self.load_persona_data()
        self.load_model()
        self.resolve_storage()

    def load_agent_data(self) -> None:
        """
        Loads the agent's configuration data.
        """
        self.agent_data = self.config.load_agent_data(self.agent_name).copy()
        self.validate_agent_data()

    def load_prompt_template(self) -> None:
        """
        Validates that prompts are properly formatted and available.
        """
        self.prompt_template = self.agent_data.get('prompts', {})
        if not self.prompt_template:
            error_msg = f"No prompts defined for agent '{self.agent_name}'."
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        self.prompt_processor.check_prompt_format(self.prompt_template)
        self.logger.debug(f"Prompts for '{self.agent_name}' validated.")

    def load_persona_data(self) -> None:
        """
        Loads and validates the persona data for the agent if available. Will not load persona data if personas is disabled in system settings.
        """
        personas_enabled = self.agent_data['settings']['system'].get('PersonasEnabled', False)
        if personas_enabled:
            self.persona = self.agent_data.get('persona', {})
            self.validate_persona_data()
            self.logger.debug(f"Persona Data Loaded for '{self.agent_name}'.")

            if self.persona:
                for key in self.persona:
                    self.template_data[key.lower()] = self.persona[key]

    def load_model(self):
        self.model = self.agent_data.get('model')
        if not self.model:
            error_msg = f"Model not specified for agent '{self.agent_name}'."
            self.logger.error(error_msg)
            raise ValueError(error_msg)

    def resolve_storage(self):
        """
        Initializes the storage for the agent, if storage is enabled.
        """
        storage_enabled = self.agent_data['settings']['system'].get('StorageEnabled', False)
        if not storage_enabled:
            self.agent_data['storage'] = None
            return

        from .utils.ChromaUtils import ChromaUtils
        persona_name = self.persona.get('Name', 'DefaultPersona') if self.persona else 'DefaultPersona'
        self.agent_data['storage'] = ChromaUtils(persona_name)

    # ---------------------------------
    # Validation
    # ---------------------------------

    def validate_agent_data(self) -> None:
        """
        Validates that agent_data has the necessary structure and keys.
        """
        if not self.agent_data:
            error_msg = f"Agent data for '{self.agent_name}' is not loaded."
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        required_keys = ['params', 'prompts', 'settings']
        for key in required_keys:
            if key not in self.agent_data:
                error_msg = f"Agent data missing required key '{key}' for agent '{self.agent_name}'."
                self.logger.error(error_msg)
                raise ValueError(error_msg)

        if 'system' not in self.agent_data['settings']:
            error_msg = f"Agent data settings missing 'system' key for agent '{self.agent_name}'."
            self.logger.error(error_msg)
            raise ValueError(error_msg)

    def validate_persona_data(self) -> None:
        """
        Validates persona data.
        """
        if not self.persona:
            self.logger.warning(f"Personas are enabled but no persona data found for agent '{self.agent_name}'.")

        self.logger.debug(f"Persona for '{self.agent_name}' validated!.")
        # Note: We may want to implement additional persona data validation later on.

    # ---------------------------------
    # Data Loading
    # ---------------------------------

    def load_data(self, **kwargs: Any) -> None:
        """
        Central method for data loading that orchestrates the loading of agent data, persona-specific data,
        storage data, and any additional data.

        Parameters:
            **kwargs (Any): Keyword arguments for additional data loading.
        """
        if self.agent_data['settings']['system'].get('OnTheFly', True):
            self.initialize_agent_config()

        self.load_from_storage()
        self.load_additional_data()
        self.template_data.update(kwargs)

    def load_from_storage(self) -> None:
        """
        Placeholder for loading from storage. Meant to be overridden by custom agents to implement specific loading
        from storage logic.

        Notes:
            - The storage instance for an Agent is set at self.agent_data['storage'].
            - The 'StorageEnabled' setting in the system.yaml file must be set to 'True'.
        """
        pass

    def load_additional_data(self) -> None:
        """
        Placeholder for loading additional data to the prompt template data. Meant to be overridden by custom agents
         as needed.
        """
        pass

    # ---------------------------------
    # Processing
    # ---------------------------------

    def process_data(self) -> None:
        """
        Placeholder for data processing. Meant to be overridden by custom agents for specific data processing needs.
        """
        pass

    def render_prompt(self) -> None:
        """
        Generates the prompts for the language model based on the template data.
        """
        self.prompt = self.prompt_processor.render_prompts(self.prompt_template, self.template_data)
        self.prompt_processor.validate_rendered_prompts(self.prompt) # {'System': '...', 'User': '...'}

    # ---------------------------------
    # LLM Execution
    # ---------------------------------

    def run_llm(self) -> None:
        """
        Executes the language model generation with the generated prompt(s) and any specified parameters.
        """
        if self.agent_data['settings']['system'].get('DebugMode', False):
            self.result = self.agent_data['debugging_text']
            return

        params: Dict[str, Any] = self.agent_data.get("params", {})
        params['agent_name'] = self.agent_name
        self.result = self.model.generate(self.prompt, **params).strip()

    # ---------------------------------
    # Result Handling
    # ---------------------------------

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
            - The 'StorageEnabled' setting in the system.yaml file must be set to 'True'.
        """
        pass

    def build_output(self) -> None:
        """
        Constructs the output from the result. This method can be overridden by subclasses to customize the output.
        By default, it simply sets the output as the model's response.
        """
        self.output = self.result
