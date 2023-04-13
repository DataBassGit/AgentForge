import configparser
import chromadb
from chromadb.config import Settings

# Read configuration file
config = configparser.ConfigParser()
config.read('Config/config.ini')

db_path = config.get('ChromaDB', 'persist_directory', fallback=None)
collection_name = config.get('ChromaDB', 'collection_name')
chroma_db_impl = config.get('ChromaDB', 'chroma_db_impl')


class ChromaUtils:
    _instance = None

    client = None
    collection = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ChromaUtils, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        # Add your initialization code here
        self.init_storage()

    def init_storage(self):
        settings = Settings(chroma_db_impl)
        if db_path:
            settings.persist_directory = db_path
        self.client = chromadb.Client(settings)

    def unload_storage(self):
        self.client = None

    def create_storage(self):
        if collection_name not in self.client.list_collections():
            self.client.create_collection(collection_name)
        self.collection = self.client.get_collection(collection_name)

    def delete_collection(self):
        if collection_name in self.client.list_collections():
            self.client.delete_collection()

    def get_collection(self):
        return self.collection

    def save_to_collection(self, task, result):

        meta = {
            "task_order": task["task_order"],
            "task_desc": task["task_desc"],
            "task_status": task["task_status"]
        }

        self.collection.add(
            ids=str(task['task_id']),
            metadatas=meta,
            documents=result
        )
