import importlib
import threading
import os
import yaml
import re
import pathlib
import sys
from typing import Dict, Any, Optional, Tuple
from ruamel.yaml import YAML

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
    _debug = False
    _instance = None
    _lock = threading.Lock()  # Class-level lock for thread safety
    pattern = r"^[a-zA-Z_][a-zA-Z0-9_]*$"

    # ------------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------------

    def __new__(cls, *args, **kwargs):
        """
        Ensures that only one instance of Config exists.
        Follows the singleton pattern to prevent multiple instances.

        Returns:
            Config: The singleton instance of the Config class.
        """
        with cls._lock:
            if not cls._instance:
                cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self, root_path: Optional[str] = None):
        """
        Initializes the Config object, setting up the project root and configuration path.
        Calls method to load configuration data from YAML files.
        """
        if not hasattr(self, 'is_initialized'):  # Prevent re-initialization
            self.is_initialized = True

            self.project_root = self.find_project_root(root_path)
            self.config_path = self.project_root / ".agentforge"

            # Placeholder for configuration data loaded from YAML files
            self.data = {}

            # Load the configuration data
            self.load_all_configurations()

    @classmethod
    def reset(cls, root_path=None):
        """
        Completely resets the Config singleton, allowing for re-initialization.
        """
        cls._instance = None
        return cls(root_path=root_path)

    def find_project_root(self, root_path: Optional[str] = None) -> pathlib.Path:
        # If a root path was provided, use it to checking that .agentforge exists
        if root_path:
            custom_root = pathlib.Path(root_path).resolve()
            agentforge_dir = custom_root / ".agentforge"
            if agentforge_dir.is_dir():
                if self._debug: print(f"\n\nUsing custom project root: {custom_root}")
                return custom_root
            # Early return or raise an error if .agentforge isn’t found in the custom path
            raise FileNotFoundError(f"No .agentforge found in custom root path: {custom_root}")

        # Otherwise, fall back to the original search logic
        script_dir = pathlib.Path(sys.argv[0]).resolve().parent
        current_dir = script_dir
        if self._debug: print(f"\n\nCurrent working directory: {os.getcwd()}")

        while current_dir != current_dir.parent:
            potential_dir = current_dir / ".agentforge"
            if self._debug: print(f"Checking {potential_dir}")
            if potential_dir.is_dir():
                if self._debug: print(f"Found .agentforge directory at: {current_dir}\n")
                return current_dir
            current_dir = current_dir.parent

        raise FileNotFoundError(f"Could not find the '.agentforge' directory starting from {script_dir}")

    # ------------------------------------------------------------------------
    # Configuration Loading
    # ------------------------------------------------------------------------

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

    # ------------------------------------------------------------------------
    # Save Configuration Method
    # ------------------------------------------------------------------------

    def save(self):
        """
        Saves changes to the configuration back to the system.yaml file,
        preserving structure, formatting, and comments.
        """
        with Config._lock:
            system_yaml_path = self.config_path / 'settings' / 'system.yaml'

            _yaml = YAML()
            _yaml.preserve_quotes = True  # Preserves quotes around strings if they exist

            try:
                # Load the existing system.yaml with formatting preserved
                with open(system_yaml_path, 'r') as yaml_file:
                    existing_data = _yaml.load(yaml_file)

                if 'settings' in self.data and 'system' in self.data['settings']:
                    # Update the existing data with the new settings
                    for key, value in self.data['settings']['system'].items():
                        if isinstance(value, dict) and key in existing_data:
                            # Merge dictionaries for nested structures
                            existing_data[key].update(value)
                            continue

                        # Replace or add the top-level key
                        existing_data[key] = value

                    # Save the updated configuration back to the file
                    with open(system_yaml_path, 'w') as yaml_file:
                        _yaml.dump(existing_data, yaml_file)
                    return
                print("No system settings to save.")
            except Exception as e:
                print(f"Error saving configuration to {system_yaml_path}: {e}")

    # ------------------------------------------------------------------------
    # Agent and Flow Configuration
    # ------------------------------------------------------------------------

    def load_agent_data(self, agent_name: str) -> Dict[str, Any]:
        """
        Loads configuration data for a specified agent, applying any overrides in the agent’s config.
        Returns a dict containing everything needed to run that agent.
        """

        agent = self.find_config('prompts', agent_name)

        api_name, class_name, model_name, final_params = self.resolve_model_overrides(agent)
        model = self.get_model(api_name, class_name, model_name)

        persona_data = self.load_persona(agent)
        prompts = self.fix_prompt_placeholders(agent.get('prompts', {}))
        settings = self.data.get('settings', {})

        default_debug_text = settings['system']['debug'].get('simulated_response', 'Simulated Text Goes Here!!!')
        simulated_response = agent.get('simulated_response', default_debug_text).strip()

        return {
            'name': agent_name,
            'settings': settings,
            'model': model,
            'params': final_params,
            'persona': persona_data,
            'prompts': prompts,
            'simulated_response': simulated_response,
        }

    # def load_flow_data(self, flow_name: str) -> Dict[str, Any]:
    #     """
    #     Loads configuration data for a specified flow.
    #
    #     Parameters:
    #         flow_name (str): The name of the flow to load.
    #
    #     Returns:
    #         dict: The configuration data for the flow.
    #
    #     Raises:
    #         FileNotFoundError: If the flow configuration is not found.
    #     """
    #     self.reload()
    #
    #     flow = self.find_config('flows', flow_name)
    #     if not flow:
    #         raise FileNotFoundError(f"Flow '{flow_name}' not found in configuration.")
    #
    #     return flow

    # ------------------------------------------------------------------------
    # Model Overrides
    # ------------------------------------------------------------------------

    def resolve_model_overrides(self, agent: dict) -> Tuple[str, str, str, Dict[str, Any]]:
        """
        Orchestrates finding and merging all relevant model overrides into
        a final 4-tuple: (api_name, class_name, model_identifier, final_params).
        """
        api_name, model_name, agent_params_override = self._get_agent_api_and_model(agent)
        api_section = self._get_api_section(api_name)
        class_name, model_data = self._find_class_for_model(api_section, model_name)

        model_identifier = self._get_model_identifier(api_name, model_name, model_data)
        final_params = self._merge_params(api_section, class_name, model_data, agent_params_override)

        return api_name, class_name, model_identifier, final_params

    # Step 1: Identify which API and model is needed, returning agent-level params
    def _get_agent_api_and_model(self, agent: dict) -> Tuple[str, str, Dict[str, Any]]:
        """
        Reads the 'Selected Model' defaults from the YAML and merges any agent-level
        overrides, returning (api_name, model_name, agent_params_override).
        Raises a ValueError if no valid API/Model can be determined.
        """
        selected_model = self.data['settings']['models'].get('default_model', {})
        default_api = selected_model.get('api')
        default_model = selected_model.get('model')

        model_overrides = agent.get('model_overrides', {})
        api_name = model_overrides.get('api', default_api)
        model_name = model_overrides.get('model', default_model)
        agent_params_override = model_overrides.get('params', {})

        if not api_name or not model_name:
            raise ValueError("No valid API/Model found in either Selected Model defaults or agent overrides.")
        return api_name, model_name, agent_params_override


    # Step 2: Retrieve the correct API section from the Model Library
    def _get_api_section(self, api_name: str) -> Dict[str, Any]:
        """
        Returns the relevant subsection of the Model Library for the requested API.
        Raises a ValueError if the API is not in the Model Library.
        """
        model_library = self.data['settings']['models'].get('model_library', {})
        if api_name not in model_library:
            raise ValueError(f"API '{api_name}' does not exist in the Model Library.")
        return model_library[api_name]

    # Step 3: Locate which class has the requested model and return its data
    @staticmethod
    def _find_class_for_model(api_section: Dict[str, Any], model_name: str) -> Tuple[str, Dict[str, Any]]:
        """
        Loops over the classes in the given API section to find one that has 'model_name'
        in its 'models' dict. Returns (class_name, model_data).
        Raises a ValueError if the model is not found.
        """
        for candidate_class, class_config in api_section.items():
            if candidate_class == 'params':  # skip any top-level 'params' key
                continue
            models_dict = class_config.get('models', {})
            if model_name in models_dict:
                return candidate_class, models_dict[model_name]

        raise ValueError(f"Model '{model_name}' not found in this API section.")

    # Step 4: Get the unique identifier for the model
    @staticmethod
    def _get_model_identifier(api_name: str, model_name: str, model_data: Dict[str, Any]) -> str:
        """
        Reads the 'identifier' for the selected model from the YAML.
        Raises a ValueError if it doesn't exist.
        """
        identifier = model_data.get('identifier')
        if not identifier:
            raise ValueError(f"Identifier not found for Model '{model_name}' under API '{api_name}' in Model Library.")
        return identifier

    # Step 5: Merge API-level, class-level, model-level params, and agent overrides
    @staticmethod
    def _merge_params(api_section: Dict[str, Any], class_name: str, model_data: Dict[str, Any],
                      agent_params_override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes all the relevant parameter dicts and merges them in ascending specificity:
           1. API-level params (api_section['params'])
           2. class-level params (api_section[class_name]['params'])
           3. model-level params (model_data['params'])
           4. agent overrides (agent_params_override)
        Returns the merged dict.
        """
        api_level_params = api_section.get('params', {})
        class_level_params = api_section[class_name].get('params', {})
        model_level_params = model_data.get('params', {})

        merged_params = {**api_level_params, **class_level_params, **model_level_params, **agent_params_override}
        return merged_params

    # ------------------------------------------------------------------------
    # Model Handling
    # ------------------------------------------------------------------------

    @staticmethod
    def get_model(api_name: str, class_name: str, model_identifier: str) -> Any:
        """
        Dynamically imports and instantiates the Python class for the requested API/class/identifier.
        We assume:
         - The Python module name is derived from the API’s name (e.g. openai_api).
         - The Python class name is exactly the same as the key used under that API (e.g. openai_api -> "O1Series", "GPT", etc.).
         - The model’s identifier is a valid identifier.
        """
        # Actually import:  from .apis import <python_module_name>
        module = importlib.import_module(f".apis.{api_name}", package=__package__)
        model_class = getattr(module, class_name)

        # Instantiate the model with the identifier
        return model_class(model_identifier)

    # ------------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------------

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

        config = search_nested_dict(self.data.get(category, {}), config_name)
        if not config:
            raise FileNotFoundError(f"Config '{config_name}' not found in configuration.")

        return config

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
        Reloads configurations if on-the-fly reloading is enabled.
        """
        if self.data['settings']['system']['misc'].get('on_the_fly', False):
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

    def load_persona(self, agent_config: dict) -> Optional[Dict[str, Any]]:
        """
        Loads the persona for the agent, if personas are enabled.

        Parameters:
            agent_config (dict): The agent's configuration data.

        Returns:
            dict: The loaded persona data.

        Raises:
            FileNotFoundError: If the persona file is not found.
        """
        settings = self.data['settings']
        if not settings['system']['persona'].get('enabled', False):
            return None

        persona_file = agent_config.get('persona') or settings['system']['persona'].get('name', 'default')
        if persona_file not in self.data.get('personas', {}):
            raise FileNotFoundError(
                f"Selected Persona '{persona_file}' not found. "
                "Please make sure the corresponding persona file is in the personas folder"
            )

        return self.data['personas'][persona_file]


