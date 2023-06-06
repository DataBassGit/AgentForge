import configparser
import json
import os
import pathlib

CONFIG_PATH = pathlib.Path(os.environ.get("AGENTFORGE_CONFIG_PATH", ".agentforge"))


def load_config():
    # Read configuration file
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH / 'config.ini')
    return config


def load_persona_data() -> dict:
    config = load_config()
    persona = config.get('Persona', 'persona')
    persona_path = CONFIG_PATH / f"{persona}.json"

    with open(persona_path, 'r') as json_file:
        data = json.load(json_file)
    return data


def load_storage_interface():
    config = load_config()
    return config.get('StorageAPI', 'library')

