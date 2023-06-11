import configparser
import json
import os
import pathlib

from dotenv import load_dotenv

# load app configuration from file
_config_path = pathlib.Path(os.environ.get("AGENTFORGE_CONFIG_PATH", ".agentforge"))
_parser: configparser.ConfigParser | None = None
_persona: dict | None = None


def _load():
    global _parser

    _parser = configparser.ConfigParser()
    _parser.read(_config_path / 'config.ini')

    load_dotenv(_config_path / '.env')


def get(section, key, **kwargs):
    if not _parser:
        _load()

    if "default" in kwargs:
        _parser.get(section, key, fallback=kwargs["default"])

    return _parser.get(section, key)


def persona():
    global _persona

    if not _persona:
        persona_name = get('Persona', 'persona')
        persona_path = _config_path / f"{persona_name}.json"

        with open(persona_path, 'r') as json_file:
            _persona = json.load(json_file)

    return _persona


def storage_api():
    return get('StorageAPI', 'library')


def model_library(model):
    return get('ModelLibrary', model)


def chromadb():
    db_path = get('ChromaDB', 'persist_directory', fallback=None)
    chroma_db_impl = get('ChromaDB', 'chroma_db_impl')
    return db_path, chroma_db_impl
