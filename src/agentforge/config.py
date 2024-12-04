import importlib
import threading
import os
import yaml
import re
import pathlib
import sys
from typing import Dict, Any, Optional

def load_yaml_file(file_path: str) -> Dict[str, Any]:
    """
    Reads and parses a YAML file, returning its contents as a Python dictionary.

    Parameters:
        file_path (str): The path to the YAML file to be read.

    Returns:
        dict: The contents of the YAML file as a dictionary. If the file is not found
        or an error occurs during parsing, an empty dictionary is returned.
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
    _lock = threading.Lock()  # Class-level lock for thread safety
    pattern = r"^[a-zA-Z_][a-zA-Z0-9_]*$"

    # ---------------------------------
    # Initialization
    # ---------------------------------

    def __new__(cls, *args, **kwargs):
        """
        Ensures that only one instance of Config exists.
        Follows the singleton pattern to prevent multiple instances.

        Returns:
            Config: The singleton instance of the Config class.
        """
        with cls._lock:
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
            self.project_root = self.find_project_root()
            self.config_path = self.project_root / ".agentforge"

            # Placeholder for configuration data loaded from YAML files
            self.data = {}

            # Load the configuration data
            self.load_all_configurations()

    # ---------------------------------
    # Configuration Loading
    # ---------------------------------

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
            print(f"Checking {potential_dir}")

            if potential_dir.is_dir():
                print(f"Found .agentforge directory at: {current_dir}\n")
                return current_dir

            current_dir = current_dir.parent

        raise FileNotFoundError(f"Could not find the '.agentforge' directory starting from {script_dir}")

    def load_all_configurations(self):
        """
        Recursively loads all configuration data from YAML files under each subdirectory of the .agentforge folder.
        """
        with self._lock:
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

    # ---------------------------------
    # Save Configuration Method
    # ---------------------------------

    def save(self):
        """
        Saves changes to the configuration back to the system.yaml file.
        """
        with Config._lock:
            system_yaml_path = self.config_path / 'settings' / 'system.yaml'

            # Load the existing system.yaml data
            existing_data = load_yaml_file(str(system_yaml_path))

            if 'settings' in self.data and 'system' in self.data['settings']:
                # Update existing data with the current settings
                existing_data.update(self.data['settings']['system'])

                # Write back to system.yaml
                try:
                    with open(system_yaml_path, 'w') as yaml_file:
                        yaml.dump(existing_data, yaml_file, default_flow_style=False)
                except Exception as e:
                    print(f"Error saving configuration to {system_yaml_path}: {e}")
                return
            print("No system settings to save.")

    # ---------------------------------
    # Agent and Flow Configuration
    # ---------------------------------

    def load_agent_data(self, agent_name: str) -> Dict[str, Any]:
        """
        Loads configuration data for a specified agent, applying any overrides specified in the agent's configuration.

        Parameters:
            agent_name (str): The name of the agent for which to load configuration data.

        Returns:
            dict: The agent's configuration data.

        Raises:
            FileNotFoundError: If the agent configuration or persona file is not found.
            KeyError: If required keys are missing.
        """
        self.reload()

        agent = self.find_config('prompts', agent_name)
        if not agent:
            raise FileNotFoundError(f"Agent '{agent_name}' not found in configuration.")

        api, model, final_model_params = self.resolve_model_overrides(agent)
        llm = self.get_llm(api, model)
        persona_data = self.load_persona(agent)
        prompts = self.fix_prompt_placeholders(agent.get('Prompts', {}))

        return {
            'name': agent_name,
            'settings': self.data.get('settings', {}),
            'llm': llm,
            'params': final_model_params,
            'persona': persona_data,
            'prompts': prompts,
        }

    def load_flow_data(self, flow_name: str) -> Dict[str, Any]:
        """
        Loads configuration data for a specified flow.

        Parameters:
            flow_name (str): The name of the flow to load.

        Returns:
            dict: The configuration data for the flow.

        Raises:
            FileNotFoundError: If the flow configuration is not found.
        """
        self.reload()

        flow = self.find_config('flows', flow_name)
        if not flow:
            raise FileNotFoundError(f"Flow '{flow_name}' not found in configuration.")

        return flow

    def resolve_model_overrides(self, agent: dict) -> tuple:
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

    # ---------------------------------
    # LLM Handling
    # ---------------------------------

    def get_llm(self, api: str, model: str):
        """
        Loads a specified language model based on API and model settings.

        Parameters:
            api (str): The API name.
            model (str): The model name.

        Returns:
            object: An instance of the requested model class.
        """
        # Retrieve the model name, module, and class from the 'models.yaml' settings.
        model_name = self.data['settings']['models']['ModelLibrary'][api]['models'][model]['name']
        module_name = self.data['settings']['models']['ModelLibrary'][api]['module']
        class_name = self.data['settings']['models']['ModelLibrary'][api]['class']

        # Dynamically import the module corresponding to the LLM API.
        module = importlib.import_module(f".llm.{module_name}", package=__package__)

        # Retrieve the class from the imported module that handles the LLM connection.
        model_class = getattr(module, class_name)
        args = [model_name]  # Prepare the arguments for the model class instantiation.
        return model_class(*args)  # Instantiate the model class with the provided arguments.

    # ---------------------------------
    # Utility Methods
    # ---------------------------------

    def find_config(self, category: str, config_name: str) -> Optional[Dict[str, Any]]:
        """
        General method to search for a configuration by name within a specified category.

        Parameters:
            category (str): The category to search in (e.g., 'prompts', 'flows').
            config_name (str): The name of the configuration to find.

        Returns:
            dict: The configuration dictionary for the specified name, or None if not found.
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

        return search_nested_dict(self.data.get(category, {}), config_name)

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

    def fix_prompt_placeholders(self, prompts):
        """
        Recursively traverse the prompts dictionary and convert any mappings
        like {'user_input': None} into strings '{user_input}'.

        Parameters:
            prompts (dict or list or str): The prompts data structure.

        Returns:
            The fixed prompts data structure with placeholders as strings.
        """
        if isinstance(prompts, dict):
            # Check if this dict is a placeholder mapping
            if len(prompts) == 1 and list(prompts.values())[0] is None:
                key = list(prompts.keys())[0]
                # Verify that the key is a valid variable name
                if re.match(self.pattern, key):
                    # Convert to a string placeholder
                    return f"{{{key}}}"

            # If not a valid variable name, process it normally
            fixed_prompts = {}
            for key, value in prompts.items():
                fixed_key = self.fix_prompt_placeholders(key)
                fixed_value = self.fix_prompt_placeholders(value)
                fixed_prompts[fixed_key] = fixed_value
            return fixed_prompts

        if isinstance(prompts, list):
            return [self.fix_prompt_placeholders(item) for item in prompts]

        if not prompts:
            return ''

        return prompts

    def reload(self):
        """
        Reloads configurations for an agent.
        """
        if self.data['settings']['system'].get('OnTheFly', False):
            self.load_all_configurations()

    def find_file_in_directory(self, directory: str, filename: str):
        """
        Recursively searches for a file within a directory and its subdirectories.

        Parameters:
            directory (str): The directory to search in.
            filename (str): The name of the file to find.

        Returns:
            pathlib.Path or None: The full path to the file if found, None otherwise.
        """
        directory = pathlib.Path(pathlib.Path(self.config_path) / directory)

        for file_path in directory.rglob(filename):
            return file_path
        return None

    def load_persona(self, agent: dict) -> Optional[Dict[str, Any]]:
        """
        Loads the persona for the agent, if personas are enabled.

        Parameters:
            agent (dict): The agent's configuration data.

        Returns:
            dict: The loaded persona data.

        Raises:
            FileNotFoundError: If the persona file is not found.
        """
        settings = self.data['settings']
        if not settings['system'].get('PersonasEnabled', False):
            return None

        persona_file = agent.get('Persona') or settings['system'].get('Persona', 'default')
        if persona_file not in self.data.get('personas', {}):
            raise FileNotFoundError(f"Selected Persona '{persona_file}' not found. Please make sure the corresponding persona file is in the personas folder")

        return self.data['personas'][persona_file]
