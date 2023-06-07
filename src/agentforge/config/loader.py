import configparser
import json
import os
import pathlib

from dotenv import load_dotenv

CONFIG_PATH = pathlib.Path(os.environ.get("AGENTFORGE_CONFIG_PATH", ".agentforge"))

dotenv_path = CONFIG_PATH / '.env'
load_dotenv(dotenv_path)


class Config:
    def __init__(self, path=CONFIG_PATH):
        self._path = path
        self._parser = configparser.ConfigParser()
        self._parser.read(CONFIG_PATH / 'config.ini')

    def persona(self):
        persona = self._parser.get('Persona', 'persona')
        persona_path = self._path / f"{persona}.json"

        with open(persona_path, 'r') as json_file:
            data = json.load(json_file)

        return data

    def storage_api(self):
        return self._parser.get('StorageAPI', 'library')

    def model_library(self, model):
        return self._parser.get('ModelLibrary', model)

    def chromadb(self):
        db_path = self._parser.get('ChromaDB', 'persist_directory', fallback=None)
        chroma_db_impl = self._parser.get('ChromaDB', 'chroma_db_impl')
        return db_path, chroma_db_impl
