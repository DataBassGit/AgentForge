import configparser
import uuid
from datetime import datetime
import chromadb
from chromadb.config import Settings

# Read configuration file
config = configparser.ConfigParser()
config.read('Config/config.ini')

db_path = config.get('ChromaDB', 'persist_directory', fallback=None)
chroma_db_impl = config.get('ChromaDB', 'chroma_db_impl')

class ChromaUtils:
    _instance = None

    client = None
    collection = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            print("\nCreating chroma utils")
            cls._instance = super(ChromaUtils, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        # Add your initialization code here
        self.init_storage()

    def init_storage(self):
        if self.client is None:
            settings = Settings(chroma_db_impl)
            if db_path:
                settings.persist_directory = db_path
            self.client = chromadb.Client(settings)

    def unload_storage(self):
        self.client = None

    def select_collection(self, collection_name):
        try:
            self.collection = self.client.get_collection(collection_name)
        except Exception as e:
            raise ValueError(f"Collection {collection_name} not found. Error: {e}")

    def create_storage(self, collection_name):
        try:
            # print("\nCreating collection: ", collection_name)
            self.client.create_collection(collection_name)
        except Exception as e:
            print("\n\nError creating collection: ", e)

    def delete_collection(self, collection_name):
        try:
            self.client.delete_collection(collection_name)
        except Exception as e:
            print("\n\nError deleting collection: ", e)

    def get_collection(self):
        return self.collection

    def save_tasks(self, tasks, results, collection_name):
        task_orders = [task["task_order"] for task in tasks]
        self.select_collection(collection_name)
        metadatas = [
            {"task_status": "replace_with_task_status", "task_desc": task["task_desc"], "list_id": str(uuid.uuid4())} for task in tasks]

        self.collection.add(

            metadatas=metadatas,
            documents=results,
            ids = [str(order) for order in task_orders]
        )

    def save_results(self, result, collection_name):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.select_collection(collection_name)
        self.collection.add(
            documents=[result],
            metadatas=[{"timestamp": timestamp}],
            ids=[str(uuid.uuid4())],
        )

    def list_collections(self):
        return self.client.list_collections()
