import importlib
import yaml
import os
import pathlib
import sys


class Config:
    _instance = None
    _level = 'debug'

    def __new__(cls, *args, **kwargs):
        """
        Ensures that only one instance of Config exists.
        Follows the singleton pattern to prevent multiple instances.

        Returns:
            Config: The singleton instance of the Config class.
        """
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
            cls._instance.__init__()
        return cls._instance

    def __init__(self, config_path=None):
        """
        Initializes the Config object, setting up the project root and configuration path.
        Calls method to load configuration data from YAML files.

        Parameters:
            config_path (str, optional): The path to the configuration directory. Defaults to None,
                                         which will use the project root's .agentforge directory.
        """
        try:
            self.project_root = self.find_project_root()
            self.config_path = config_path or self.project_root / ".agentforge"

            # Placeholders for the data the agent needs which is located in each respective YAML file
            self.persona_name = {}
            self.personas = {}
            self.actions = {}
            self.agent = {}
            self.tools = {}
            self.settings = {}

            # Here is where we load the information from the YAML files to their corresponding attributes
            self.load()
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
        # Get the path of the executing script
        script_dir = pathlib.Path(sys.argv[0]).parent
        current_dir = script_dir

        while current_dir != current_dir.parent:
            potential_dir = current_dir / ".agentforge"

            if potential_dir.is_dir():
                return current_dir

            current_dir = current_dir.parent

        raise FileNotFoundError(f"Could not find the .agentforge directory at {script_dir}")

    def load(self):
        """
        Loads configuration data from YAML files into respective attributes.
        """
        try:
            self.load_settings()
            self.load_actions()
            self.load_tools()
            self.load_persona()
        except Exception as e:
            print(f"Error loading configuration data: {e}")

    # Does not belong here, need to be reworked to be in chroma_utils
    def chromadb(self):
        """
        Retrieves the ChromaDB settings from the configuration.

        Returns:
            tuple: A tuple containing the database path and embedding settings.
        """
        # Retrieve the ChromaDB settings
        db_settings = self.settings['storage'].get('ChromaDB', {})

        # Get the database path and embedding settings
        db_path_setting = db_settings.get('persist_directory', None)
        db_embed = db_settings.get('embedding', None)

        # Construct the absolute path of the database using the project root
        if db_path_setting:
            db_path = str(self.project_root / db_path_setting)
        else:
            db_path = None

        return db_path, db_embed

    def find_file_in_directory(self, directory, filename):
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

    # Not happy with this
    def get_config_element(self, case):
        """
        Retrieves a specific configuration element based on a given case.

        Parameters:
            case (str): The case to retrieve, such as "Persona", "Tools", or "Actions".

        Returns:
            The configuration element if found; otherwise, returns "Invalid case".
        """
        switch = {
            "Persona": self.personas[self.persona_name],
            "Tools": self.tools,
            "Actions": self.actions
        }
        return switch.get(case, "Invalid case")

    def get_file_path(self, file_name):
        """
        Constructs the full path for a given filename within the configuration path.

        Parameters:
            file_name (str): The name of the file.

        Returns:
            pathlib.Path: The full path to the file within the configuration directory.
        """
        return pathlib.Path(self.config_path) / file_name

    def get_llm(self, api, model):
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
            model_name = self.settings['models']['ModelLibrary'][api]['models'][model]['name']
            module_name = self.settings['models']['ModelLibrary'][api]['module']
            class_name = self.settings['models']['ModelLibrary'][api]['class']

            module = importlib.import_module(f".llm.{module_name}", package=__package__)
            model_class = getattr(module, class_name)
            args = [model_name]
            return model_class(*args)

        except Exception as e:
            print(f"Error Loading Model: {e}")
            raise

    def load_agent(self, agent_name):
        """
        Loads an agent's configuration from a YAML file.

        Parameters:
            agent_name (str): The name of the agent to load.

        Raises:
            FileNotFoundError: If the agent's YAML file cannot be found.
            Exception: For any errors encountered while loading the agent.
        """
        try:
            path_to_file = self.find_file_in_directory("agents", f"{agent_name}.yaml")
            if path_to_file:
                self.agent = get_yaml_data(path_to_file)  # Fix warning
            else:
                raise FileNotFoundError(f"Agent {agent_name}.yaml not found.")
        except Exception as e:
            print(f"Error loading agent {agent_name}: {e}")

    def load_settings(self):
        """
        Loads settings configuration from the settings folder.
        """
        self.load_from_folder("settings")

    def load_actions(self):
        """
        Loads actions configuration from the actions folder.
        """
        self.load_from_folder("actions")

    def load_tools(self):
        """
        Loads tools configuration from the tools folder.
        """
        self.load_from_folder("tools")

    def load_persona(self):
        """
        Loads persona configuration based on the directives setting from the settings folder.
        """
        self.persona_name = self.settings.get('directives', None).get('Persona', None)
        self.load_from_folder("personas")

    def reload(self, agent_name):
        """
        Reloads configurations for an agent, including actions, tools, and persona, without refreshing settings.

        Parameters:
            agent_name (str): The name of the agent to reload configurations for.
        """
        # Rework how we do main objective
        # self.load_settings() // If we allow refreshing the settings, the main objective will always be rewritten
        self.load_agent(agent_name)
        self.load_actions()
        self.load_tools()
        self.load_persona()

    def load_from_folder(self, folder):
        """
        Loads configuration data from a specified folder.

        Parameters:
            folder (str): The folder from which to load configuration data.

        Raises:
            Exception: For any errors encountered while loading data from the folder.
        """
        try:
            # Get the path for the provided folder name
            folder_path = self.get_file_path(folder)

            # If the folder attribute doesn't exist, initialize it as an empty dictionary
            if not hasattr(self, folder):
                setattr(self, folder, {})

            # Reference to the folder's dictionary
            folder_dict = getattr(self, folder)

            # Iterate over each file in the specified folder
            for file in os.listdir(folder_path):
                # Only process files with a .yaml or .yml extension
                if file.endswith(".yaml") or file.endswith(".yml"):
                    # Load the YAML data from the current file
                    pathy = os.path.join(folder_path, file)
                    data = get_yaml_data(pathy)

                    # Get the filename without the extension
                    filename = os.path.splitext(file)[0]

                    # Check if filename exists under the folder's dictionary, if not, initialize it as a dict
                    if filename not in folder_dict:
                        folder_dict[filename] = {}

                    # Reference to the file name's dictionary
                    file_dict = folder_dict[filename]

                    for item_name, data_item in data.items():
                        # Extract the name and store the data under that name in the file name's dictionary
                        if item_name:
                            file_dict[item_name] = data_item
        except Exception as e:
            print(f"Error loading data from {folder}: {e}")

# -------------------------- FUNCTIONS --------------------------


def get_yaml_data(file_path):
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
