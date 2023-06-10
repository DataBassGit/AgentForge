import os
import uuid
from datetime import datetime

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from ..config import loader
from ..logs.logger_config import Logger

logger = Logger(name="Chroma Utils")
logger.set_level('info')

# Read configuration file
db_path, chroma_db_impl = loader.Config().chromadb()

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

    def collection_list(self):
        return self.client.list_collections()

    def peek(self, collection_name):
        self.select_collection(collection_name)
        return self.collection.peek()

    def load_collection(self, params):
        try:
            collection_name = params.pop('collection_name', 'default_collection_name')

            self.select_collection(collection_name)

            where = params.pop('filter', {})
            data = self.collection.get(**params, where=where)
            #data = self.collection.get(**params)

            logger.log(
                f"\nCollection: {collection_name}"
                f"\nData: {data}",
                'debug'
            )
        except Exception as e:
            print(f"\n\nError loading data: {e}")
            data = []

        return data

    def save_memory(self, params):
        try:
            collection_name = params.pop('collection_name', None)
            ids = params.pop('ids', None)
            documents = params.pop('data', None)
            meta = params.pop('metadata', [{} for _ in documents])

            if ids is None:
                ids = [str(uuid.uuid4()) for _ in documents]

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for m in meta:
                m['timestamp'] = timestamp

            self.select_collection(collection_name)
            self.collection.add(
                documents=documents,
                metadatas=meta,
                ids=ids
            )

        except Exception as e:
            raise ValueError(f"\n\nError saving results. Error: {e}")

    def update_memory(self, params):
        try:
            collection_name = params.pop('collection_name', None)
            ids = params.pop('ids', None)
            documents = params.pop('data', None)
            meta = params.pop('metadata', [{} for _ in documents])

            if ids is None:
                ids = [str(uuid.uuid4()) for _ in documents]

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for m in meta:
                m['timestamp'] = timestamp

            self.select_collection(collection_name)
            self.collection.update(
                documents=documents,
                metadatas=meta,
                ids=ids
            )

        except Exception as e:
            raise ValueError(f"\n\nError saving results. Error: {e}")

    def query_memory(self, params, num_results=1):
        collection_name = params.pop('collection_name', None)
        self.select_collection(collection_name)

        max_result_count = self.collection.count()

        num_results = min(num_results, max_result_count)

        query = params.pop('query', None)
        filter = params.pop('filter', None)
        task_desc = params.pop('task_description', None)

        logger.log(
            f"\nDB Query - Num Results: {num_results}"
            f"\n\nDB Query - Text Query: {task_desc}",
            'debug'
        )

        if num_results > 0:
            result = self.collection.query(
                query_texts=[query],
                n_results=num_results,
                where=filter
            )
        else:
            result = {'documents': "No Results!"}

        logger.log(f"DB Query - Results: {result}", 'debug')

        return result