import configparser
import uuid

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

    def save_tasks(self, tasks, results):
        task_orders = [task["task_order"] for task in tasks]

        metadatas = [
            {"task_status": "replace_with_task_status", "task_desc": task["task_desc"], "list_id": str(uuid.uuid4())} for
            task in tasks]

        self.collection.add(
            ids=[str(order) for order in task_orders],
            metadatas=metadatas,
            documents=results
        )

        print(self.collection.get())

        # task_order = task["task_order"]
        # self.collection.add(
        #     ids=[str(order) for order in task_order],
        #     metadatas=[
        #         {"task_status": task["task_status"], "task_desc": task["task_desc"], "task_id": task["task_id"]}],
        #     documents=result
        # )

    def save_results(self, task, result):
        pass


