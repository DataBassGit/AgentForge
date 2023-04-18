import json
import configparser


def load_persona_data() -> dict:
    # Read configuration file
    config = configparser.ConfigParser()
    config.read('Config/config.ini')

    persona_file_path = config.get('Persona', 'persona')

    with open(persona_file_path, 'r') as json_file:
        data = json.load(json_file)
    return data
