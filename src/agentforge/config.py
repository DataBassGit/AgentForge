import importlib
import importlib.util
import threading
import os
import yaml
import re
import pathlib
from pathlib import Path
import sys
from typing import Dict, Any, Optional, Tuple
from ruamel.yaml import YAML
from types import ModuleType

# Import ConfigManager for structured config objects
from .core.config_manager import ConfigManager
from .config_structs import AgentConfig, CogConfig


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
    """
    Singleton class for loading, managing, and providing access to AgentForge configuration data.
    """
    _instance = None
    _lock = threading.Lock()
    _debug = False
    pattern = r"^[a-zA-Z_][a-zA-Z0-9_]*$"

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self, root_path: Optional[str] = None):
        if not hasattr(self, 'is_initialized'):
            self._initialize_attributes(root_path)
            self.is_initialized = True

    @classmethod
    def reset(cls, root_path=None):
        """
        Completely resets the Config singleton, allowing for re-initialization.
        """
        cls._instance = None
        instance = cls(root_path=root_path)
        return instance

    def _initialize_attributes(self, root_path: Optional[str]):
        """
        Initializes all instance attributes for the Config class.
        """
        self.project_root = self.find_project_root(root_path)
        self.config_path = self.project_root / ".agentforge"
        self.data = {}
        self.config_manager = ConfigManager()
        self.load_all_configurations()

    def find_project_root(self, root_path: Optional[str] = None) -> pathlib.Path:
        # If a root path was provided, use it to checking that .agentforge exists
        if root_path:
            custom_root = pathlib.Path(root_path).resolve()
            agentforge_dir = custom_root / ".agentforge"
            if agentforge_dir.is_dir():
                if self._debug: print(f"\n\nUsing custom project root: {custom_root}")
                return custom_root
            # Early return or raise an error if .agentforge isn't found in the custom path
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

    # -----------------------------------
    # Configuration Loading & Saving
    # -----------------------------------

    @staticmethod
    def load_yaml_file(file_path: str) -> Dict[str, Any]:
        """
        Reads and parses a YAML file, returning its contents as a Python dictionary.
        Returns an empty dictionary if the file is not found or an error occurs.
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
                        data = self.load_yaml_file(file_path)
                        if data:
                            filename_without_ext = os.path.splitext(file)[0]
                            nested_dict[filename_without_ext] = data

    def save(self):
        """
        Saves changes to the configuration back to the system.yaml file,
        preserving structure, formatting, and comments.
        """
        with Config._lock:
            system_yaml_path = self.config_path / 'settings' / 'system.yaml'
            _yaml = YAML()
            _yaml.preserve_quotes = True
            try:
                with open(system_yaml_path, 'r') as yaml_file:
                    existing_data = _yaml.load(yaml_file)
                if 'settings' in self.data and 'system' in self.data['settings']:
                    for key, value in self.data['settings']['system'].items():
                        if isinstance(value, dict) and key in existing_data:
                            existing_data[key].update(value)
                            continue
                        existing_data[key] = value
                    with open(system_yaml_path, 'w') as yaml_file:
                        _yaml.dump(existing_data, yaml_file)
                    return
                print("No system settings to save.")
            except Exception as e:
                print(f"Error saving configuration to {system_yaml_path}: {e}")

    def reload(self):
        """
        Reloads configurations if on-the-fly reloading is enabled in settings.
        """
        if self.settings.system.misc.on_the_fly:
            self.load_all_configurations()

    # -----------------------------------
    # Agent & Cog Configuration
    # -----------------------------------

    def load_agent_data(self, agent_name: str) -> AgentConfig:
        """
        Loads configuration data for a specified agent, applying any overrides in the agent's config.
        Returns a structured AgentConfig object containing everything needed to run that agent.
        """
        agent = self.find_config('prompts', agent_name)
        api_name, class_name, model_name, final_params = self.resolve_model_overrides(agent)
        model = self.get_model(api_name, class_name, model_name)
        persona_data = self.load_persona(agent)
        prompts = self.fix_prompt_placeholders(agent.get('prompts', {}))
        settings = self.data.get('settings', {})
        default_debug_text = settings['system']['debug'].get('simulated_response', 'Simulated Text Goes Here!!!')
        simulated_response = agent.get('simulated_response', default_debug_text).strip()
        raw_agent_data = {
            'name': agent_name,
            'settings': settings,
            'model': model,
            'params': final_params,
            'persona': persona_data,
            'prompts': prompts,
            'simulated_response': simulated_response,
        }
        reserved_fields = {
            'name', 'settings', 'model', 'params', 'persona', 'prompts', 'simulated_response',
            'model_overrides'
        }
        for key, value in agent.items():
            if key not in raw_agent_data and key not in reserved_fields:
                raw_agent_data[key] = value
        return self.config_manager.build_agent_config(raw_agent_data)

    def load_cog_data(self, cog_name: str) -> CogConfig:
        """
        Loads configuration data for a specified cog, returning a validated structured CogConfig object.
        """
        raw_cog_data = self.find_config('cogs', cog_name)
        return self.config_manager.build_cog_config(raw_cog_data)

    # -----------------------------------
    # Model API & Overrides
    # -----------------------------------

    def resolve_model_overrides(self, agent: dict) -> Tuple[str, str, str, Dict[str, Any]]:
        """
        Finds and merges all relevant model overrides into a final 4-tuple:
        (api_name, class_name, model_identifier, final_params).
        """
        api_name, model_name, agent_params_override = self._get_agent_api_and_model(agent)
        api_section = self._get_api_section(api_name)
        class_name, model_data = self._find_class_for_model(api_section, model_name)
        model_identifier = self._get_model_identifier(api_name, model_name, model_data)
        final_params = self._merge_params(api_section, class_name, model_data, agent_params_override)
        return api_name, class_name, model_identifier, final_params

    def _get_agent_api_and_model(self, agent: dict) -> Tuple[str, str, Dict[str, Any]]:
        """
        Reads the 'Selected Model' defaults from the YAML and merges any agent-level overrides.
        Returns (api_name, model_name, agent_params_override).
        Raises ValueError if no valid API/Model can be determined.
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

    def _get_api_section(self, api_name: str) -> Dict[str, Any]:
        """
        Returns the relevant subsection of the Model Library for the requested API.
        Raises ValueError if the API is not in the Model Library.
        """
        model_library = self.data['settings']['models'].get('model_library', {})
        if api_name not in model_library:
            raise ValueError(f"API '{api_name}' does not exist in the Model Library.")
        return model_library[api_name]

    @staticmethod
    def _find_class_for_model(api_section: Dict[str, Any], model_name: str) -> Tuple[str, Dict[str, Any]]:
        """
        Finds which class in the API section has the requested model in its 'models' dict.
        Returns (class_name, model_data). Raises ValueError if not found.
        """
        for candidate_class, class_config in api_section.items():
            if candidate_class == 'params':
                continue
            models_dict = class_config.get('models', {})
            if model_name in models_dict:
                return candidate_class, models_dict[model_name]
        raise ValueError(f"Model '{model_name}' not found in this API section.")

    @staticmethod
    def _get_model_identifier(api_name: str, model_name: str, model_data: Dict[str, Any]) -> str:
        """
        Reads the 'identifier' for the selected model from the YAML.
        Raises ValueError if it doesn't exist.
        """
        identifier = model_data.get('identifier')
        if not identifier:
            raise ValueError(f"Identifier not found for Model '{model_name}' under API '{api_name}' in Model Library.")
        return identifier

    @staticmethod
    def _merge_params(api_section: Dict[str, Any], class_name: str, model_data: Dict[str, Any], agent_params_override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merges API-level, class-level, model-level params, and agent overrides in ascending specificity.
        Returns the merged dict.
        """
        api_level_params = api_section.get('params', {})
        class_level_params = api_section[class_name].get('params', {})
        model_level_params = model_data.get('params', {})
        merged_params = {**api_level_params, **class_level_params, **model_level_params, **agent_params_override}
        return merged_params

    # -----------------------------------
    # Model Handling
    # -----------------------------------

    @staticmethod
    def resolve_class(full_class_path: str, default_class: Optional[type] = None, context: str = "") -> type:
        """
        Dynamically resolve and return a class from a fully qualified path.
        Raises ValueError or ImportError if the class cannot be found.
        """
        if not full_class_path:
            if default_class is not None:
                return default_class
            raise ValueError(f"No class path provided for {context}")
        parts = full_class_path.split(".")
        if len(parts) < 2:
            raise ValueError(f"Invalid type format for {context}: '{full_class_path}'. Must be fully qualified (e.g., 'mymodule.MyClass').")
        module_path = ".".join(parts[:-1])
        class_name = parts[-1]
        try:
            spec = importlib.util.find_spec(module_path)
            if spec is None:
                raise ImportError(f"Module '{module_path}' not found for {context}.")
        except (ModuleNotFoundError, ImportError):
            raise ImportError(f"Module '{module_path}' not found for {context}.")
        module = importlib.import_module(module_path)
        if not hasattr(module, class_name):
            raise ImportError(f"Class '{class_name}' not found in module '{module_path}' for {context}.")
        return getattr(module, class_name)

    @staticmethod
    def get_model(api_name: str, class_name: str, model_identifier: str) -> Any:
        """
        Dynamically imports and instantiates the Python class for the requested API/class/identifier.
        """
        module = Config._get_module(api_name)
        model_class = getattr(module, class_name)
        return model_class(model_identifier)

    @staticmethod
    def _get_module(api_name: str) -> ModuleType:
        """
        Retrieves the module for the given API. Tries the built-in apis folder first; if not found, loads from the custom_apis folder.
        """
        module = Config._try_load_built_in_api(api_name)
        if module is not None:
            return module
        return Config._load_custom_api(api_name)

    @staticmethod
    def _try_load_built_in_api(api_name: str) -> Optional[ModuleType]:
        """
        Attempts to load a built-in API module from the package's apis folder. Returns the module if found; otherwise returns None.
        """
        built_in_api_path = Path(__file__).parent / "apis" / f"{api_name}.py"
        if built_in_api_path.exists():
            return importlib.import_module(f".apis.{api_name}", package=__package__)
        return None

    @staticmethod
    def _load_custom_api(api_name: str) -> ModuleType:
        """
        Loads a custom API module from the project's custom_apis folder. Sets up a dummy package environment so that relative imports work correctly.
        """
        project_root = Config().project_root
        custom_api_dir = project_root / ".agentforge" / "custom_apis"
        custom_api_path = custom_api_dir / f"{api_name}.py"
        if not custom_api_path.exists():
            raise ImportError(
                f"Cannot find API module '{api_name}' in the built-in folder or at {custom_api_path}."
            )
        spec = importlib.util.spec_from_file_location(f"custom_apis.{api_name}", custom_api_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load spec for custom API module '{api_name}'.")
        module = importlib.util.module_from_spec(spec)
        module.__package__ = "custom_apis"
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module

    # -----------------------------------
    # Utility Methods
    # -----------------------------------

    def find_config(self, category: str, config_name: str) -> Optional[Dict[str, Any]]:
        """
        Search for a configuration by name within a specified category.
        Returns the configuration dictionary for the specified name, or raises FileNotFoundError if not found.
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

    def find_file_in_directory(self, directory: str, filename: str):
        """
        Recursively search for a file within a directory and its subdirectories.
        Returns the full path to the file if found, None otherwise.
        """
        directory = pathlib.Path(pathlib.Path(self.config_path) / directory)
        for file_path in directory.rglob(filename):
            return file_path
        return None

    def fix_prompt_placeholders(self, prompts):
        """
        Recursively traverse the prompts dictionary and convert any mappings like {'user_input': None} into strings '{user_input}'.
        Returns the fixed prompts data structure with placeholders as strings.
        """
        if isinstance(prompts, dict):
            if len(prompts) == 1 and list(prompts.values())[0] is None:
                key = list(prompts.keys())[0]
                if re.match(self.pattern, key):
                    return f"{{{key}}}"
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

    @staticmethod
    def get_nested_dict(data: dict, path_parts: tuple):
        """
        Gets or creates a nested dictionary given the parts of a relative path.
        Returns a reference to the nested dictionary at the end of the path.
        """
        for part in path_parts:
            if part not in data:
                data[part] = {}
            data = data[part]
        return data

    @property
    def settings(self):
        """
        Returns the loaded settings as a Settings dataclass for dot notation access.
        """
        settings_dict = self.data.get('settings', {})
        return self.config_manager._build_settings(settings_dict)

    # -----------------------------------
    # Persona Handling
    # -----------------------------------

    def resolve_persona(self, cog_config: Optional[Dict[str, Any]] = None, agent_config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Resolves the persona to use based on the deterministic hierarchy:
        1. Cog-defined persona (highest priority)
        2. Agent-defined persona
        3. System default persona (lowest priority)
        Returns the resolved persona data or None if personas are disabled.
        """
        settings = self.data['settings']
        if not settings['system']['persona'].get('enabled', False):
            return None
        persona_name = None
        if cog_config and 'persona' in cog_config:
            persona_name = cog_config['persona']
        elif agent_config and 'persona' in agent_config:
            persona_candidate = agent_config['persona']
            if isinstance(persona_candidate, str):
                persona_name = persona_candidate
        else:
            persona_name = settings['system']['persona'].get('name', 'default_assistant')
        if persona_name and persona_name not in self.data.get('personas', {}):
            raise FileNotFoundError(
                f"Selected Persona '{persona_name}' not found. "
                "Please make sure the corresponding persona file is in the personas folder"
            )
        return self.data['personas'][persona_name] if persona_name else None

    def load_persona(self, agent_config: dict) -> Optional[Dict[str, Any]]:
        """
        Loads the persona for the agent, if personas are enabled.
        Returns the loaded persona data.
        Raises FileNotFoundError if the persona file is not found.
        """
        persona_data = self.resolve_persona(agent_config=agent_config)
        return persona_data


