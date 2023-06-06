import json
import configparser
import pathlib


def load_persona_data() -> dict:
    # Read configuration file
    config = configparser.ConfigParser()
    config.read('config/config.ini')

    parent_path = pathlib.Path(__file__).parent
    persona = config.get('Persona', 'persona')
    persona_path = parent_path / f"{persona}.json"

    with open(persona_path, 'r') as json_file:
        data = json.load(json_file)
    return data
