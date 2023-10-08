import importlib
import yaml
import os
import pathlib


class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
            cls._instance.__init__()
        return cls._instance

    def __init__(self, config_path=None):
        self.config_path = config_path or os.environ.get("AGENTFORGE_CONFIG_PATH", ".agentforge")

        # Placeholders for the data the agent needs which is located in each respective YAML file
        self.persona = {}
        self.actions = {}
        self.agent = {}
        self.tools = {}
        self.settings = {}

        # Here is where we load the information from the YAML files to their corresponding attributes
        self.load()

    def load(self):
        self.load_settings()
        self.load_actions()
        self.load_tools()
        self.load_persona()

    def chromadb(self):
        db_path = self.settings['storage'].get('ChromaDB', {}).get('persist_directory', None)
        db_embed = self.settings['storage'].get('ChromaDB', {}).get('embedding', None)

        return db_path, db_embed


    def find_file_in_directory(self, directory, filename):
        """
        Recursively searches for a filename in a directory and its subdirectories.
        Returns the full path if found, or None otherwise.
        """
        directory = self.get_file_path(directory)

        for root, dirs, files in os.walk(directory):

            for file in files:
                path = os.path.join(root, file)
                if filename == file:
                    return path.replace(".agentforge\\", "").strip()
        return None

    def get_config_element(self, case):
        switch = {
            "Persona": self.persona,
            "Tools": self.tools,
            "Actions": self.actions
        }
        return switch.get(case, "Invalid case")

    def get_file_path(self, file_name):
        return pathlib.Path(self.config_path) / file_name

    def get_llm(self, api):
        model_name = self.agent.get('Model', self.settings['models']['ModelSettings']['Model'])
        model_name = self.settings['models']['ModelLibrary'].get(model_name)

        models = {
            "claude_api": {
                "module": "anthropic",
                "class": "Claude",
                "args": [model_name],
            },
            "oobabooga_api": {
                "module": "oobabooga",
                "class": "Oobabooga",
            },
            "oobabooga_v2_api": {
                "module": "oobabooga",
                "class": "OobaboogaV2",
            },
            "openai_api": {
                "module": "openai",
                "class": "GPT",
                "args": [model_name],
            },
        }

        model = models.get(api)
        if not model:
            raise ValueError(f"Unsupported Language Model API library: {api}")

        module_name = model["module"]
        module = importlib.import_module(f".llm.{module_name}", package=__package__)
        class_name = model["class"]
        model_class = getattr(module, class_name)
        args = model.get("args", [])
        return model_class(*args)

    # def load_agent(self, agent_name):
    #     self.agent = self.get_yaml_data(f"agents/{agent_name}.yaml")

    def load_agent(self, agent_name):
        path_to_file = self.find_file_in_directory("agents", f"{agent_name}.yaml")
        if path_to_file:
            self.agent = self.get_yaml_data(path_to_file)
        else:
            raise FileNotFoundError(f"Agent {agent_name}.yaml not found.")

    def load_settings(self):
        self.load_from_folder("settings")

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
                data = self.get_yaml_data(os.path.join(folder, file))

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

    def load_actions(self):
        self.load_from_folder("actions")

    def load_tools(self):
        self.load_from_folder("tools")

    def load_persona(self):
        persona_name = self.settings.get('directives', None).get('Persona', None)
        self.persona = self.get_yaml_data(f"personas/{persona_name}.yaml")

    def get_yaml_data(self, file_name):
        file_path = self.get_file_path(file_name)
        try:
            with open(file_path, 'r') as yaml_file:
                return yaml.safe_load(yaml_file)
        except FileNotFoundError:
            print(f"File {file_path} not found.")
            return {}
        except yaml.YAMLError:
            print(f"Error decoding YAML from {file_path}")
            return {}

    def reload(self, agent_name):
        self.load_agent(agent_name)
        self.load_actions()
        self.load_tools()
        self.load_persona()

    def get_storage_api(self):

        return self.settings['storage']['StorageAPI']
