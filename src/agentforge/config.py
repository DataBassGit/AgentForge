import importlib
import json
import os
import pathlib
from typing import Dict

_config: Dict | None = None
_persona: Dict | None = None
_actions: Dict | None = None
_tools: Dict | None = None


def _load():
    # global _parser
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


switch = {
    "Persona": persona,
    "Tasks": tasks,
    "Tools": tools,
    "Actions": actions
}


def data(case):
    return switch.get(case, lambda: "Invalid case")
