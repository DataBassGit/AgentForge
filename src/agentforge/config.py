import importlib
import os
import yaml
import pathlib
import sys
from typing import Dict, Any

def load_yaml_file(file_path: str):
    """
    Reads and parses a YAML file, returning its contents as a Python dictionary.

    This function attempts to safely load the contents of a YAML file specified by
    the file path. If the file cannot be found or there's an error decoding the YAML,
    it handles the exceptions gracefully.

    Parameters:
        file_path (str): The path to the YAML file to be read.

    Returns:
        dict: The contents of the YAML file as a dictionary. If the file is not found
        or an error occurs during parsing, an empty dictionary is returned.

    Notes:
        - The function uses `yaml.safe_load` to prevent execution of arbitrary code
          that might be present in the YAML file.
        - Exceptions for file not found and YAML parsing errors are caught and logged,
          with an empty dictionary returned to allow the calling code to continue
          execution without interruption.
    """
    try:
        with open(file_path, 'r') as yaml_file:
            return yaml.safe_load(yaml_file)
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return {}
    except yaml.YAMLError:
        print(f"Error decoding YAML from {file_path}")
        return {}


class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensures that only one instance of Config exists.
        Follows the singleton pattern to prevent multiple instances.

        Returns:
            Config: The singleton instance of the Config class.
        """
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """
        Initializes the Config object, setting up the project root and configuration path.
        Calls method to load configuration data from YAML files.
        """
        if not hasattr(self, 'is_initialized'):  # Prevent re-initialization
            self.is_initialized = True
            try:
                self.project_root = self.find_project_root()
                self.config_path = self.project_root / ".agentforge"

                # Placeholders for the data the agent needs which is located in each respective YAML file
                self.data = {}

                # Here is where we load the information from the YAML files to their corresponding attributes
                self.load_all_configurations()
            except Exception as e:
                raise ValueError(f"Error during Config initialization: {e}")

    @staticmethod
    def find_project_root():
        """
        Finds the project root by searching for the .agentforge directory.

        Returns:
            pathlib.Path: The path to the project root directory.

        Raises:
            FileNotFoundError: If the .agentforge directory cannot be found.
        """
        print(f"\n\nCurrent working directory: {os.getcwd()}")

        script_dir = pathlib.Path(sys.argv[0]).resolve().parent
        current_dir = script_dir

        while current_dir != current_dir.parent:
            potential_dir = current_dir / ".agentforge"
            print(f"Checking {potential_dir}")  # Debugging output
            if potential_dir.is_dir():
                print(f"Found .agentforge directory at: {current_dir}")  # Debugging output
                return current_dir

            current_dir = current_dir.parent

        raise FileNotFoundError(f"Could not find the '.agentforge' directory at {script_dir}")

    @staticmethod
    def get_nested_dict(data: dict, path_parts: tuple):
        """
        Gets or creates a nested dictionary given the parts of a relative path.

        Args:
            data (dict): The top-level dictionary to start from.
            path_parts (tuple): A tuple of path components leading to the desired nested dictionary.

        Returns:
            A reference to the nested dictionary at the end of the path.
        """
        for part in path_parts:
            if part not in data:
                data[part] = {}
            data = data[part]
        return data

    def find_agent_config(self, agent_name: str):
        """
        Search for an agent's configuration by name within the nested agents' dictionary.

        Parameters:
            agent_name (str): The name of the agent to find.

        Returns:
            dict: The configuration dictionary for the specified agent, or None if not found.
        """

        def search_nested_dict(nested_dict, target):
            for key, value in nested_dict.items():
                if key == target:
                    return value
                elif isinstance(value, dict):
                    result = search_nested_dict(value, target)
                    if result is not None:
                        return result
            return None

        return search_nested_dict(self.data.get('prompts', {}), agent_name)

    def load_all_configurations(self):
        """
        Recursively loads all configuration data from YAML files under each subdirectory of the .agentforge folder.
        """
        for subdir, dirs, files in os.walk(self.config_path):
            for file in files:
                if file.endswith(('.yaml', '.yml')):
                    subdir_path = pathlib.Path(subdir)
                    relative_path = subdir_path.relative_to(self.config_path)
                    nested_dict = self.get_nested_dict(self.data, relative_path.parts)

                    file_path = str(subdir_path / file)
                    data = load_yaml_file(file_path)
                    if data:
                        filename_without_ext = os.path.splitext(file)[0]
                        nested_dict[filename_without_ext] = data

    def find_file_in_directory(self, directory: str, filename: str):
        """
        Recursively searches for a file within a directory and its subdirectories.

        Parameters:
            directory (str): The directory to search in.
            filename (str): The name of the file to find.

        Returns:
            pathlib.Path or None: The full path to the file if found, None otherwise.
        """
        directory = pathlib.Path(self.get_file_path(directory))

        for file_path in directory.rglob(filename):
            return file_path
        return None

    def get_file_path(self, file_name: str):
        """
        Constructs the full path for a given filename within the configuration path.

        Parameters:
            file_name (str): The name of the file.

        Returns:
            pathlib.Path: The full path to the file within the configuration directory.
        """
        return pathlib.Path(self.config_path) / file_name

    def get_llm(self, api: str, model: str):
        """
        Loads a specified language model based on API and model settings.

        Parameters:
            api (str): The API name.
            model (str): The model name.

        Returns:
            object: An instance of the requested model class.

        Raises:
            Exception: If there is an error loading the model.
        """
        try:
            # Retrieve the model name, module, and class from the 'models.yaml' settings.
            model_name = self.data['settings']['models']['ModelLibrary'][api]['models'][model]['name']
            module_name = self.data['settings']['models']['ModelLibrary'][api]['module']
            class_name = self.data['settings']['models']['ModelLibrary'][api]['class']

            # Dynamically import the module corresponding to the LLM API.
            module = importlib.import_module(f".llm.{module_name}", package=__package__)

            # Retrieve the class from the imported module that handles the LLM connection.
            model_class = getattr(module, class_name)
            model_class = getattr(module, class_name)
            args = [model_name]  # Prepare the arguments for the model class instantiation.
            return model_class(*args)  # Instantiate the model class with the provided arguments.

        except Exception as e:
            print(f"Error Loading Model: {e}")
            raise

    def load_agent(self, agent_name: str):
        """
        Loads an agent's configuration from a YAML file.

        Parameters:
            agent_name (str): The name of the agent to load.

        Raises:
            FileNotFoundError: If the agent's YAML file cannot be found.
            Exception: For any errors encountered while loading the agent.
        """
        try:
            path_to_file = self.find_file_in_directory("prompts", f"{agent_name}.yaml")
            if path_to_file:
                self.data['agent'] = load_yaml_file(str(path_to_file))  # Fix warning
            else:
                raise FileNotFoundError(f"Agent {agent_name}.yaml not found.")
        except Exception as e:
            print(f"Error loading agent {agent_name}: {e}")

    def load_persona(self, agent: dict) -> dict | None:
        """
        Loads the persona for the agent, if personas are enabled.

        Parameters:
            agent (dict): The agent's configuration data.

        Returns:
            dict: The loaded persona and the persona file name.
        """
        persona_data = None

        settings = self.data['settings']
        if not settings['system'].get('PersonasEnabled', False):
            return persona_data

        persona_file = agent.get('Persona') or settings['system'].get('Persona', 'default')
        if persona_file not in self.data['personas']:
            raise FileNotFoundError(f"Selected Persona '{persona_file}' not found. Please make sure the corresponding persona file is in the personas folder")

        persona_data = self.data['personas'][persona_file]
        return persona_data

    def load_agent_data(self, agent_name: str) -> Dict[str, Any]:
        """
        Loads configuration data for a specified agent, applying any overrides specified in the agent's configuration.

        Parameters:
            agent_name (str): The name of the agent for which to load configuration data.

        Returns: None

        Raises:
            FileNotFoundError: If a required configuration or persona file is not found.
            KeyError: If a required key is missing in the configuration.
            Exception: For general errors encountered during the loading process.
        """
        try:
            self.reload()

            agent = self.find_agent_config(agent_name)
            api, model, final_model_params = self.resolve_model_overrides(agent)
            llm = self.get_llm(api, model)
            persona_data = self.load_persona(agent)

            return {
                'name': agent_name,
                'settings': self.data['settings'],
                'llm': llm,
                'params': final_model_params,
                'persona': persona_data,
                'prompts': agent.get('Prompts', {}),
            }
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Configuration or persona file not found: {e}")
        except KeyError as e:
            raise KeyError(f"Missing key in configuration: {e}")
        except Exception as e:
            raise Exception(f"Error loading agent data: {e}")

    def reload(self):
        """
        Reloads configurations for an agent.
        """
        if self.data['settings']['system']['OnTheFly']:
            self.load_all_configurations()

    def resolve_model_overrides(self, agent: dict) -> tuple[str, str, dict]:
        """
        Resolves the model and API overrides for the agent, if any.

        Parameters:
            agent (dict): The agent's configuration data.

        Returns:
            tuple: The resolved API, model, and final model parameters.
        """
        settings = self.data['settings']

        model_overrides = agent.get('ModelOverrides', {})
        model_settings = settings['models']['ModelSettings']

        api = model_overrides.get('API', model_settings['API'])
        model = model_overrides.get('Model', model_settings['Model'])

        default_params = model_settings['Params']
        params = settings['models']['ModelLibrary'].get(api, {}).get('models', {}).get(model, {}).get('params', {})

        combined_params = {**default_params, **params}
        final_model_params = {**combined_params, **model_overrides.get('Params', {})}

        return api, model, final_model_params
