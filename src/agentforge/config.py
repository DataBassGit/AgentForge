import importlib
import json
import os
import pathlib
from typing import Dict

_config: Dict | None = None
_persona: Dict | None = None
_actions: Dict | None = None
_tools: Dict | None = None


class Config:
    _switch = None

    def __init__(self, config_path=None):
        self.config_path = config_path or os.environ.get("AGENTFORGE_CONFIG_PATH", ".agentforge")
        self.config = {}
        self.persona = {}
        self.actions = {}
        self.tools = {}
        self.load()

    def load_json(self, file_path):
        try:
            with open(file_path, 'r') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            print(f"File {file_path} not found.")
            return {}
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {file_path}")
            return {}

    def _get_file_path(self, file_name):
        return pathlib.Path(self.config_path) / file_name

    def load(self):
        self.load_config()
        self.load_persona()
        self.load_actions()
        self.load_tools()

    def load_config(self):
        self.config = self.load_json(self._get_file_path("config.json"))

    def load_persona(self):
        persona_name = self.config.get('Persona', {}).get('default', "")
        self.persona = self.load_json(self._get_file_path(f"{persona_name}.json"))

    def load_actions(self):
        self.actions = self.load_json(self._get_file_path("actions.json"))
        pass

    def load_tools(self):
        self.tools = self.load_json(self._get_file_path("tools.json"))

    def get_persona(self):
        if not self.persona:
            self.load_persona()

        return self.persona

    def get_tasks(self):
        if not _persona:
            self.load_persona()

        return self.persona['Tasks']

    def get_tools(self):
        if not self.tools:
            self.load_tools()

        return self.tools

    def get_actions(self):
        if not self.actions:
            self.load_actions()

        return self.actions

    def storage_api(self):
        return get('StorageAPI', 'selected')

    def get(self, section, key, default=None):
        if self.config is None:
            self.load()

        return self.config.get(section, {}).get(key, default)

    def chromadb(self):
        db_path = get('ChromaDB', 'persist_directory', default=None)
        db_embed = get('ChromaDB', 'embedding', default=None)
        return db_path, db_embed

    def get_config_element(self, case):
        switch = {
            "Persona": self.persona,
            "Tasks": self.persona.get('Tasks', {}),
            "Tools": self.tools,
            "Actions": self.actions
        }
        return switch.get(case, "Invalid case")


# -----------------------------------


def _load():
    global _config
    global _persona
    global _actions
    global _tools

    _path = pathlib.Path(
        os.environ.get("AGENTFORGE_CONFIG_PATH", ".agentforge")
    )

    _config_path = _path / "config.json"  # Add the path to the Config JSON file

    with open(_config_path, 'r') as json_file:  # Open the Config JSON file
        _config = json.load(json_file)  # Load the data from the Config JSON file

    persona_name = _config['Persona']['default']
    persona_path = _path / f"{persona_name}.json"  # Add the path to the Persona JSON file

    with open(persona_path, 'r') as json_file:  # Open the Persona JSON file
        _persona = json.load(json_file)  # Load the data from the Persona JSON file

    actions_path = _path / "actions.json"  # Add the path to the Actions JSON file

    with open(actions_path, 'r') as json_file:  # Open the Actions JSON file
        _actions = json.load(json_file)  # Load the data from the Actions JSON file

    tools_path = _path / "tools.json"  # Add the path to the Tools JSON file

    with open(tools_path, 'r') as json_file:  # Open the Tools JSON file
        _tools = json.load(json_file)  # Load the data from the Tools JSON file


def get_llm(api, agent_name):
    model_name = _persona[agent_name].get('Model', _persona['Defaults']['Model'])
    model_name = _config['ModelLibrary'].get(model_name)

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


def get(section, key, default=None):
    if _config is None:
        _load()

    return _config.get(section, {}).get(key, default)


def storage_api():
    return get('StorageAPI', 'selected')


def chromadb():
    db_path = get('ChromaDB', 'persist_directory', default=None)
    db_embed = get('ChromaDB', 'embedding', default=None)
    return db_path, db_embed


def persona():
    if not _persona:
        _load()

    return _persona


def tasks():
    if not _persona:
        _load()

    return _persona['Tasks']


def tools():
    if not _tools:
        _load()

    return _tools


def actions():
    if not _actions:
        _load()

    return _actions


_switch = {
    "Persona": persona,
    "Tasks": tasks,
    "Tools": tools,
    "Actions": actions
}


def data(case):
    return _switch.get(case, lambda: "Invalid case")
