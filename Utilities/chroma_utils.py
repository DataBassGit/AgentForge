import os
import configparser
import uuid
from datetime import datetime
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from Logs.logger_config import Logger

logger = Logger(name="Chroma Utils")
logger.set_level('info')

dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'Config', '.env')
load_dotenv(dotenv_path)

# Read configuration file
config = configparser.ConfigParser()
config.read('Config/config.ini')
db_path = config.get('ChromaDB', 'persist_directory', fallback=None)
chroma_db_impl = config.get('ChromaDB', 'chroma_db_impl')

# Get API keys from environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')

# Embeddings
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
            logger.log("Creating chroma utils", 'debug')
            cls._instance = super(ChromaUtils, cls).__new__(cls, *args, **kwargs)
            cls._instance.init_storage()
        return cls._instance

    def __init__(self):
        # Add your initialization code here
        pass

    def init_storage(self):
        if self.client is None:
            settings = Settings(chroma_db_impl=chroma_db_impl, persist_directory=db_path)
            if db_path:
                settings.persist_directory = db_path
            self.client = chromadb.Client(settings)

    def select_collection(self, collection_name):
        try:
            self.collection = self.client.get_or_create_collection(collection_name, embedding_function=openai_ef)
        except Exception as e:
            raise ValueError(f"\n\nError getting or creating collection. Error: {e}")

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
            print("\n\nError clearing table:", e)

    def load_collection(self, params):
        try:
            collection_name = params.get('collection_name', 'default_collection_name')
            collection_property = params.get('collection_property', None)

            self.select_collection(collection_name)

            data = self.collection.get()[collection_property]
            logger.log(
                f"\nCollection: {collection_name}"
                f"\nProperty: {collection_property}"
                f"\nData: {data}",
                'debug'
            )
        except Exception as e:
            print(f"\n\nError loading data: {e}")
            data = []

        return data

    def load_salient(self, params):
        try:
            collection_name = params.get('collection_name', 'default_collection_name')

            self.select_collection(collection_name)
            logger.log(f"Load Salient Collection: {self.collection.get()}", 'debug')

            data = self.collection.get()
        except Exception as e:
            print(f"\n\nError loading data: {e}")
            data = []

        return data

    def save_tasks(self, params):
        tasks = params.get('tasks', [])
        results = params.get('results', [])
        collection_name = params.get('collection_name', 'default_collection_name')

        try:
            task_orders = [task["task_order"] for task in tasks]
            self.select_collection(collection_name)
            metadatas = [{
                "task_status": "not completed",
                "task_desc": task["task_desc"],
                "list_id": str(uuid.uuid4()),
                "task_order": task["task_order"]
            } for task in tasks]

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
            raise ValueError(f"\n\nError saving results. Error: {e}")

    def query_db(self, collection_name, task_desc, num_results=1):
        self.select_collection(collection_name)

        max_result_count = self.collection.count()

        num_results = min(num_results, max_result_count)

        logger.log(
            f"\nDB Query - Num Results: {num_results}"
            f"\n\nDB Query - Text Query: {task_desc}",
            'debug'
        )


        if num_results > 0:
            result = self.collection.query(
                query_texts=[task_desc],
                n_results=num_results,
            )
        else:
            result = {'documents': "No Results!"}

        logger.log(f"DB Query - Results: {result}", 'debug')

        return result

    def collection_list(self):
        return self.client.list_collections()

    def peek(self, collection_name):
        self.select_collection(collection_name)
        return self.collection.peek()

    def save_status(self, status, task_id, task_desc, task_order):
        logger.log(
            f"\nUpdating Task: {task_desc})"
            f"\nTask ID: {task_id}"
            f"\nTask Status: {status}"
            f"\nTask Order: {task_order}",
            'debug'
        )
        self.select_collection("tasks")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            self.collection.update(
                ids=[task_id],
                documents=[task_desc],
                metadatas=[{
                    "timestamp": timestamp,
                    "task_status": status,
                    "task_desc": task_desc,
                    "task_order": task_order
                }]
            )
        except Exception as e:
            raise ValueError(f"\n\nError saving status. Error: {e}")

    def save_heuristic(self, params, collection_name):
        try:
            result = params.pop('data', None)
            meta = params

            self.select_collection(collection_name)
            self.collection.add(
                documents=[str(result)],
                # metadatas=[{"timestamp": timestamp}],
                metadatas=[meta],
                ids=[str(uuid.uuid4())],
            )
            # print(f"\n\nData Saved to Collection: {self.collection.get()}")
        except Exception as e:
            raise ValueError(f"\n\nError saving results. Error: {e}")

