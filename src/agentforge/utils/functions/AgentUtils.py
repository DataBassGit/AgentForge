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

    def get_storage(self):
        return self.config

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

            # Check for API and model_name overrides in the agent's ModelOverrides
            agent_api_override = agent.get('ModelOverrides', {}).get('API', None)
            agent_model_override = agent.get('ModelOverrides', {}).get('Model', None)

            # Use overrides if available, otherwise default to the settings
            api = agent_api_override or settings['models']['ModelSettings']['API']
            model = agent_model_override or settings['models']['ModelSettings']['Model']

            # Load default model parameter settings
            default_params = settings['models']['ModelSettings']['Params']

            # Load model-specific settings (if any)
            model_params = settings['models']['ModelLibrary'][api]['models'].get(model, {}).get('params', {})

            # Merge default settings with model-specific settings
            combined_params = {**default_params, **model_params}

            # Apply agent's parameter overrides (if any)
            agent_params_overrides = agent.get('ModelOverrides', {}).get('Params', {})
            final_model_params = {**combined_params, **agent_params_overrides}

            # Check for a Persona override in the agent's configuration
            agent_persona_override = agent.get('Persona', None)

            # Use the overridden persona if available, or default to the system's predefined persona
            persona_file = agent_persona_override or settings['system'].get('Persona')

            persona = None
            if persona_file is not None:
                # Check if the selected persona exists
                if persona_file not in self.config.data['personas']:
                    self.logger.log(f"Selected Persona '{persona_file}' not found. Please make sure the corresponding "
                                    f"persona file is in the personas folder", 'critical')

                # Load the selected persona
                persona = self.config.data['personas'][persona_file]

            # Initialize agent data
            agent_data: Dict[str, Any] = dict(
                name=agent_name,
                settings=settings,
                llm=self.config.get_llm(api, model),
                params=final_model_params,
                prompts=agent['Prompts'],
                storage=StorageInterface().storage_utils,
                persona=persona,
            )

            return agent_data
        except FileNotFoundError as e:
            # Handle file not found errors specifically
            self.logger.log(f"Configuration or persona file not found: {e}", 'critical')
        except KeyError as e:
            # Handle missing keys in configuration
            self.logger.log(f"Missing key in configuration: {e}", 'critical')
        except Exception as e:
            # Handle other general exceptions
            self.logger.log(f"Error loading agent data: {e}", 'critical')

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
