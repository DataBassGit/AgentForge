import configparser
import importlib
import json
import os
import pathlib
from typing import Dict

_parser: configparser.ConfigParser | None = None
_persona: Dict | None = None
_actions: Dict | None = None
_tools: Dict | None = None


def _load():
    global _parser
    global _persona
    global _actions
    global _tools

    _config_path = pathlib.Path(
        os.environ.get("AGENTFORGE_CONFIG_PATH", ".agentforge")
    )

    _parser = configparser.ConfigParser()
    _parser.read(_config_path / 'config.ini')

    persona_name = _parser.get('Persona', 'persona')
    persona_path = _config_path / f"{persona_name}.json"

    with open(persona_path, 'r') as json_file:
        _persona = json.load(json_file)

    actions_path = _config_path / "actions.json"  # Add the path to the actions.json

    with open(actions_path, 'r') as json_file:  # Open the actions.json file
        _actions = json.load(json_file)  # Load the data from actions.json to _actions

    tools_path = _config_path / "tools.json"  # Add the path to the tools.json

    with open(tools_path, 'r') as json_file:  # Open the tools.json file
        _tools = json.load(json_file)  # Load the data from tools.json to _tools


def get_llm(api, agent_name):
    model_name = _parser.get('ModelLibrary', _persona[agent_name]['Model'])
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


def get(section, key, **kwargs):
    if not _parser:
        _load()

    if "default" in kwargs:
        _parser.get(section, key, fallback=kwargs["default"])

    return _parser.get(section, key)


def persona():
    if not _persona:
        _load()

    return _persona


def tools():
    if not _tools:
        _load()

    return _tools


def actions():
    if not _actions:
        _load()

    return _actions


def storage_api():
    return get('StorageAPI', 'library')


def chromadb():
    db_path = get('ChromaDB', 'persist_directory', fallback=None)
    db_embed = get('ChromaDB', 'embedding', fallback=None)
    chroma_db_impl = get('ChromaDB', 'chroma_db_impl')
    return db_path, db_embed, chroma_db_impl
