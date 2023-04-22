import configparser
import uuid
from datetime import datetime
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

# Read configuration file
config = configparser.ConfigParser()
config.read('Config/config.ini')

db_path = config.get('ChromaDB', 'persist_directory', fallback=None)
chroma_db_impl = config.get('ChromaDB', 'chroma_db_impl')

config.read('Config/api_keys.ini')
openai_api_key = config.get('OpenAI', 'api_key')
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=openai_api_key,
                model_name="text-embedding-ada-002"
            )


class ChromaUtils:
    _instance = None
    client = None
    collection = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            print("\nCreating chroma utils")
            cls._instance = super(ChromaUtils, cls).__new__(cls, *args, **kwargs)
            cls._instance.init_storage()
        return cls._instance

    def __init__(self):
        # Add your initialization code here
        pass

    def init_storage(self):
        if self.client is None:
            settings = Settings(chroma_db_impl)
            if db_path:
                settings.persist_directory = db_path
            self.client = chromadb.Client(settings)

    def select_collection(self, collection_name):
        try:
            self.collection = self.client.get_or_create_collection(collection_name, embedding_function=openai_ef)
        except Exception as e:
            raise ValueError(f"Error getting or creating collection. Error: {e}")

    def create_collection(self, collection_name):
        try:
            self.client.create_collection(collection_name, embedding_function=openai_ef)
        except Exception as e:
            raise ValueError(f"Error creating collection. Error: {e}")

    def delete_collection(self, collection_name):
        try:
            self.client.delete_collection(collection_name)
        except Exception as e:
            print("\n\nError deleting collection: ", e)

    def clear_collection(self, collection_name):
        try:
            self.select_collection(collection_name)
            self.collection.delete()
        except Exception as e:
            print("Error clearing table:", e)

    def load_collection(self, params):
        try:
            collection_name = params.get('collection_name', 'default_collection_name')
            collection_property = params.get('collection_property', None)

            self.select_collection(collection_name)
            data = self.collection.get()[collection_property]
        except Exception as e:
            print(f"Error loading data: {e}")
            data = []

        return data

    def save_tasks(self, params):
        tasks = params.get('tasks', [])
        results = params.get('results', [])
        collection_name = params.get('collection_name', 'default_collection_name')

        try:
            task_orders = [task["task_order"] for task in tasks]
            self.select_collection(collection_name)
            metadatas = [
                {"task_status": "replace_with_task_status", "task_desc": task["task_desc"], "list_id": str(uuid.uuid4())} for task in tasks]

            self.collection.add(

                metadatas=metadatas,
                documents=results,
                ids=[str(order) for order in task_orders]
            )
        except Exception as e:
            raise ValueError(f"Error saving tasks. Error: {e}")

    def save_results(self, params):
        try:
            result = params.get('result', None)
            collection_name = params.get('collection_name', 'default_collection_name')
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            self.select_collection(collection_name)
            self.collection.add(
                documents=[result],
                metadatas=[{"timestamp": timestamp}],
                ids=[str(uuid.uuid4())],
            )
        except Exception as e:
            raise ValueError(f"Error saving results. Error: {e}")
