import importlib
import json
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
        self.data = {}  # This is the attribute that will contain the configuration data in config.json file

        # the following are placeholders for each of the respective json information the agent needs
        self.persona = {}
        self.actions = {}
        self.agent = {}
        self.tools = {}

        # here is where we load the information from the JSON files to their corresponding attributes
        self.load()

    def chromadb(self):
        db_path = self.get('ChromaDB', 'persist_directory', default=None)
        db_embed = self.get('ChromaDB', 'embedding', default=None)
        return db_path, db_embed

    def get(self, section, key, default=None):
        if self.data is None:
            self.load()

        return self.data.get(section, {}).get(key, default)

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
        model_name = self.agent.get('Model', self.data['Defaults']['Model'])
        model_name = self.data['ModelLibrary'].get(model_name)

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

    def get_json_data(self, file_name):
        file_path = self.get_file_path(file_name)
        try:
            with open(file_path, 'r') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            print(f"File {file_path} not found.")
            return {}
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {file_path}")
            return {}

    def load(self):
        self.load_config()
        self.load_actions()
        self.load_tools()
        self.load_persona()

    def load_agent(self, agent_name):
        self.agent = self.get_json_data(f"agents/{agent_name}.json")

    def load_config(self):
        self.data = self.get_json_data("config.json")

    def load_from_folder(self, folder_and_attr_name):
        # Get the path for the provided folder name
        folder_path = self.get_file_path(folder_and_attr_name)

        # Initialize the attribute as an empty dictionary
        setattr(self, folder_and_attr_name, {})

        # Iterate over each file in the specified folder
        for file in os.listdir(folder_path):
            # Only process files with a .json extension
            if file.endswith(".json"):
                # Load the JSON data from the current file
                data = self.get_json_data(os.path.join(folder_and_attr_name, file))

                # Extract the name and remove it from the data
                item_name = data.pop('Name', None)

                # If the name exists, store the data under that name in the specified attribute
                if item_name:
                    getattr(self, folder_and_attr_name)[item_name] = data

    def load_actions(self):
        self.load_from_folder("actions")

    def load_tools(self):
        self.load_from_folder("tools")

    def load_persona(self):
        persona_name = self.data.get('Persona', {}).get('selected', "")
        self.persona = self.get_json_data(f"personas/{persona_name}.json")

    def reload(self, agent_name):
        self.load_agent(agent_name)
        self.load_actions()
        self.load_tools()
        self.load_persona()

    def storage_api(self):
        return self.get('StorageAPI', 'selected')
