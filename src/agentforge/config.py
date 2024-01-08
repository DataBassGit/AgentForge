import importlib
import yaml
import os
import pathlib
import sys


class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
            cls._instance.__init__()
        return cls._instance

    def __init__(self, config_path=None):
        self.project_root = self.find_project_root()
        self.config_path = config_path or self.project_root / ".agentforge"
        # ... other initializations ...
        # self.config_path = config_path or os.environ.get("AGENTFORGE_CONFIG_PATH", ".agentforge")

        # Placeholders for the data the agent needs which is located in each respective YAML file
        self.persona_name = {}
        self.personas = {}
        self.actions = {}
        self.agent = {}
        self.tools = {}
        self.settings = {}

        # Here is where we load the information from the YAML files to their corresponding attributes
        self.load()

    @staticmethod
    def find_project_root():
        """
        Finds the project root by looking for the .agentforge folder.
        Starts from the directory of the executing script and moves up the tree.
        """
        # Get the path of the executing script
        script_dir = pathlib.Path(sys.argv[0]).parent
        # print(f"Starting search for .agentforge from {script_dir}")

        current_dir = script_dir
        while current_dir != current_dir.parent:
            potential_dir = current_dir / ".agentforge"
            # print(f"Checking {potential_dir}")

            if potential_dir.is_dir():
                # print(f"Found .agentforge directory at {current_dir}")
                return current_dir

            current_dir = current_dir.parent

        raise FileNotFoundError(f"Could not find the .agentforge directory at {script_dir}")

    def load(self):
        self.load_settings()
        self.load_actions()
        self.load_tools()
        self.load_persona()

    # def chromadb(self):
    #     db_path = self.settings['storage'].get('ChromaDB', {}).get('persist_directory', None)
    #     db_embed = self.settings['storage'].get('ChromaDB', {}).get('embedding', None)
    #
    #     return db_path, db_embed

    def chromadb(self):
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
        Recursively searches for a filename in a directory and its subdirectories.
        Returns the full path if found, or None otherwise.
        """
        directory = pathlib.Path(self.get_file_path(directory))

        for file_path in directory.rglob(filename):
            return file_path
        return None

    def get_config_element(self, case):
        switch = {
            "Persona": self.personas[self.persona_name],
            "Tools": self.tools,
            "Actions": self.actions
        }
        return switch.get(case, "Invalid case")

    def get_file_path(self, file_name):
        return pathlib.Path(self.config_path) / file_name

    def get_llm(self, api, model):
        try:
            model_name = self.settings['models']['ModelLibrary'][api]['models'][model]['name']
            module_name = self.settings['models']['ModelLibrary'][api]['module']
            # module_name = 'openai_api' if api == 'oobabooga_api' else self.settings['models']['ModelLibrary'][api]['module']
            class_name = self.settings['models']['ModelLibrary'][api]['class']

            # # Check if api is 'oobabooga_api' and change it to 'openai_api' if so
            # if api == 'oobabooga_api':
            #     module_name = 'openai_api'

            module = importlib.import_module(f".llm.{module_name}", package=__package__)
            model_class = getattr(module, class_name)
            args = [model_name]
            return model_class(*args)

        except Exception as e:
            print(f"Error Loading Model: {e}")
            raise

    def load_agent(self, agent_name):
        path_to_file = self.find_file_in_directory("agents", f"{agent_name}.yaml")
        if path_to_file:
            self.agent = get_yaml_data(path_to_file)
        else:
            raise FileNotFoundError(f"Agent {agent_name}.yaml not found.")

    def load_settings(self):
        self.load_from_folder("settings")

    def load_actions(self):
        self.load_from_folder("actions")

    def load_tools(self):
        self.load_from_folder("tools")

    def load_persona(self):
        self.persona_name = self.settings.get('directives', None).get('Persona', None)
        self.load_from_folder("personas")

    def reload(self, agent_name):
        # self.load_settings() // If we allow refreshing the settings, the main objective will always be rewritten
        self.load_agent(agent_name)
        self.load_actions()
        self.load_tools()
        self.load_persona()

    def load_from_folder(self, folder):
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


# -------------------------- FUNCTIONS --------------------------


def get_yaml_data(file_path):
    try:
        with open(file_path, 'r') as yaml_file:
            return yaml.safe_load(yaml_file)
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return {}
    except yaml.YAMLError:
        print(f"Error decoding YAML from {file_path}")
        return {}
