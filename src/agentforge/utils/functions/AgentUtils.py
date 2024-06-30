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

    def load_agent_data(self, agent_name: str) -> Dict[str, Any]:
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
            persona_data, persona_file = self.load_persona(agent, settings)
            storage = self.resolve_storage(settings, persona_file)

            return {
                'name': agent_name,
                'settings': settings,
                'llm': llm,
                'params': final_model_params,
                'persona': persona_data,
                'prompts': agent.get('Prompts', {}),
                'storage': storage,
            }

        except FileNotFoundError as e:
            self.logger.log(f"Configuration or persona file not found: {e}", 'critical')
            raise
        except KeyError as e:
            self.logger.log(f"Missing key in configuration: {e}", 'critical')
            raise
        except Exception as e:
            self.logger.log(f"Unexpected error: {e}", 'critical')
            raise

    @staticmethod
    def resolve_model_overrides(agent: dict, settings: dict) -> tuple[str, str, dict]:
        """
        Resolves the model and API overrides for the agent, if any.

        Parameters:
            agent (dict): The agent's configuration data.
            settings (dict): The application's settings.

        Returns:
            tuple: The resolved API, model, and final model parameters.
        """
        model_overrides = agent.get('ModelOverrides', {})
        model_settings = settings['models']['ModelSettings']

        api = model_overrides.get('API', model_settings['API'])
        model = model_overrides.get('Model', model_settings['Model'])

        default_params = model_settings['Params']
        params = settings['models']['ModelLibrary'].get(api, {}).get('models', {}).get(model, {}).get('params', {})

        combined_params = {**default_params, **params}
        final_model_params = {**combined_params, **model_overrides.get('Params', {})}

        return api, model, final_model_params

    def load_persona(self, agent: dict, settings: dict) -> tuple[dict | None, str]:
        """
        Loads the persona for the agent, if personas are enabled.

        Parameters:
            agent (dict): The agent's configuration data.
            settings (dict): The application's settings.

        Returns:
            tuple: The loaded persona and the persona file name.
        """
        persona_file = 'default'
        persona_data = None

        if not settings['system'].get('PersonasEnabled', False):
            return persona_data, persona_file

        persona_file = agent.get('Persona') or settings['system'].get('Persona', 'default')

        if persona_file not in self.config.data['personas']:
            self.logger.log(f"Selected Persona '{persona_file}' not found. Please make sure the "
                            f"corresponding persona file is in the personas folder", 'error')
            return None, persona_file

        persona_data = self.config.data['personas'][persona_file]
        return persona_data, persona_file

    def resolve_storage(self, settings: dict, persona_file: str):
        """
        Initializes the storage for the agent, if storage is enabled.

        Parameters:
            settings (dict): The application's settings.
            persona_file (str): The persona file name.

        Returns:
            The initialized storage utility, or None if storage is not enabled.
        """
        if not settings['system'].get('StorageEnabled'):
            return None

        return self.storage_interface.get_storage(persona_file)
