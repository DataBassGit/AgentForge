import configparser
import json
import os
import pathlib

CONFIG_PATH = pathlib.Path(os.environ.get("AGENTFORGE_CONFIG_PATH", ".agentforge"))


def load_persona_data() -> dict:
    # Read configuration file
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH / 'config.ini')

    persona = config.get('Persona', 'persona')
    persona_path = CONFIG_PATH / f"{persona}.json"

    with open(persona_path, 'r') as json_file:
        data = json.load(json_file)
    return data
