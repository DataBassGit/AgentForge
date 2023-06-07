import configparser
import json
import os
import pathlib

from dotenv import load_dotenv


CONFIG_PATH = pathlib.Path(os.environ.get("AGENTFORGE_CONFIG_PATH", ".agentforge"))

dotenv_path = CONFIG_PATH / '.env'
load_dotenv(dotenv_path)


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


def load_chromadb():
    config = load_config()
    db_path = config.get('ChromaDB', 'persist_directory', fallback=None)
    chroma_db_impl = config.get('ChromaDB', 'chroma_db_impl')
    return db_path, chroma_db_impl
