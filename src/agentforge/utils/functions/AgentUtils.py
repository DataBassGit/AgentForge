import yaml
import re
from typing import Dict, Any
from .Logger import Logger
from ...config import Config
from ..storage_interface import StorageInterface


class AgentUtils:
    """
    A utility class providing support for agent-specific operations, including configuration loading, YAML parsing,
    and extracting blocks from text.

    Attributes:
        logger (Logger): Logger instance for logging messages.
        config (Config): Config instance for accessing application configurations.
    """

    def __init__(self):
        """
        Initializes the AgentUtils class with a Logger and Config instance.
        """
        self.logger = Logger(name=self.__class__.__name__)
        self.config = Config()
        self.storage_interface = StorageInterface()

    def load_agent_data(self, agent_name):
        """
        Loads configuration data for a specified agent, applying any overrides specified in the agent's configuration.

        Parameters:
            agent_name (str): The name of the agent for which to load configuration data.

        Returns:
            Dict[str, Any]: A dictionary containing the loaded agent data, including settings, LLM instance,
                            parameters, prompts, storage utility, and persona.

        Raises:
            FileNotFoundError: If a required configuration or persona file is not found.
            KeyError: If a required key is missing in the configuration.
            Exception: For general errors encountered during the loading process.
        """
        try:
            self.config.reload()

            agent = self.config.find_agent_config(agent_name)
            settings = self.config.data['settings']

            api, model, final_model_params = self.resolve_model_overrides(agent, settings)
            llm = self.config.get_llm(api, model)
            persona, persona_file = self.load_persona(agent, settings)
            storage = self.resolve_storage(settings, persona_file)

            # Initialize agent data
            agent_data: Dict[str, Any] = dict(
                name=agent_name,
                settings=settings,
                llm=llm,
                params=final_model_params,
                persona=persona,
                prompts=agent['Prompts'],
                storage=storage,
            )

            return agent_data
        except FileNotFoundError as e:
            self.logger.log(f"Configuration or persona file not found: {e}", 'critical')
        except KeyError as e:
            self.logger.log(f"Missing key in configuration: {e}", 'critical')
        except Exception as e:
            self.logger.log(f"Error loading agent data: {e}", 'critical')

    @staticmethod
    def resolve_model_overrides(agent, settings):
        """
        Resolves the model and API overrides for the agent, if any.

        Parameters:
            agent (dict): The agent's configuration data.
            settings (dict): The application's settings.

        Returns:
            tuple: The resolved API, model, and final model parameters.
        """
        agent_api_override = agent.get('ModelOverrides', {}).get('API', None)
        agent_model_override = agent.get('ModelOverrides', {}).get('Model', None)

        api = agent_api_override or settings['models']['ModelSettings']['API']
        model = agent_model_override or settings['models']['ModelSettings']['Model']

        default_params = settings['models']['ModelSettings']['Params']
        model_params = settings['models']['ModelLibrary'][api]['models'].get(model, {}).get('params', {})

        combined_params = {**default_params, **model_params}
        agent_params_overrides = agent.get('ModelOverrides', {}).get('Params', {})
        final_model_params = {**combined_params, **agent_params_overrides}

        return api, model, final_model_params

    def load_persona(self, agent, settings):
        """
        Loads the persona for the agent, if personas are enabled.

        Parameters:
            agent (dict): The agent's configuration data.
            settings (dict): The application's settings.

        Returns:
            tuple: The loaded persona and the persona file name.
        """
        persona = None
        persona_file = None
        persona_enabled = settings['system'].get('EnablePersonas', None)

        if persona_enabled:
            agent_persona_override = agent.get('Persona', None)
            persona_file = agent_persona_override or settings['system'].get('Persona')

            if persona_file is not None:
                if persona_file not in self.config.data['personas']:
                    self.logger.log(f"Selected Persona '{persona_file}' not found. Please make sure the "
                                    f"corresponding persona file is in the personas folder", 'critical')

                persona = self.config.data['personas'].get(persona_file)

        return persona, persona_file

    def resolve_storage(self, settings, persona_file):
        """
        Initializes the storage for the agent, if storage is enabled.

        Parameters:
            settings (dict): The application's settings.
            persona_file (str): The persona file name.

        Returns:
            The initialized storage utility.
        """
        storage = settings['system'].get('StorageEnabled', None)
        if storage:
            storage = self.storage_interface.get_storage(persona_file)
        return storage

    def parse_yaml_string(self, yaml_string):
        """
        Parses a YAML-formatted string into a Python dictionary.

        Parameters:
            yaml_string (str): The YAML string to parse.

        Returns:
            Dict[str, Any]: The parsed YAML content as a dictionary.

        Raises:
            yaml.YAMLError: If an error occurs during YAML parsing.
        """
        try:
            cleaned_string = self.extract_yaml_block(yaml_string)
            return yaml.safe_load(cleaned_string)
        except yaml.YAMLError as e:
            self.logger.log(f"Error decoding YAML string: {e}", 'critical')

    def extract_yaml_block(self, text):
        """
        Extracts a YAML block from a string, typically used to parse YAML content from larger text blocks or files.

        Parameters:
            text (str): The text containing the YAML block.

        Returns:
            str: The extracted YAML block as a string, or None if no block is found.

        Raises:
            Exception: For unexpected errors during the extraction process.
        """
        try:
            # Regex pattern to capture content between ```yaml and ```
            pattern = r"```yaml(.*?)```"
            match = re.search(pattern, text, re.DOTALL)

            if match:
                # Return the extracted content
                return match.group(1).strip()
            else:
                # Return None or an empty string if no match is found
                return None
        except Exception as e:
            # Handle unexpected errors during regex operation
            self.logger.log(f"Error extracting YAML block: {e}", 'critical')
