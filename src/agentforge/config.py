import configparser
import importlib
import json
import os
import pathlib
from typing import Dict, Any

from dotenv import load_dotenv

from .utils.storage_interface import StorageInterface

_parser: configparser.ConfigParser | None = None
_persona: Dict | None = None


def _load():
    global _parser
    global _persona

    _config_path = pathlib.Path(
        os.environ.get("AGENTFORGE_CONFIG_PATH", ".agentforge")
    )

    load_dotenv(_config_path / '.env')

    _parser = configparser.ConfigParser()
    _parser.read(_config_path / 'config.ini')

    persona_name = _parser.get('Persona', 'persona')
    persona_path = _config_path / f"{persona_name}.json"

    with open(persona_path, 'r') as json_file:
        _persona = json.load(json_file)


def _get_llm(api, agent_name):
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


def get_agent_data(agent_name):
    # Load persona data
    persona_data = persona()

    # Initialize agent data
    agent_data: Dict[str, Any] = dict(
        name=agent_name,
        llm=_get_llm(persona_data[agent_name]['API'], agent_name),
        objective=persona_data['Objective'],
        prompts=persona_data[agent_name]['Prompts'],
        params=persona_data[agent_name]['Params'],
        storage=StorageInterface().storage_utils,
    )

    if "HeuristicImperatives" in persona_data:
        imperatives = persona_data["HeuristicImperatives"]
        agent_data.update(heuristic_imperatives=imperatives)

    return agent_data


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


def storage_api():
    return get('StorageAPI', 'library')


def chromadb():
    db_path = get('ChromaDB', 'persist_directory', fallback=None)
    chroma_db_impl = get('ChromaDB', 'chroma_db_impl')
    return db_path, chroma_db_impl
