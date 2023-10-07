import os
import uuid
from datetime import datetime

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from ..config import Config
from ..logs.logger_config import Logger

logger = Logger(name="Chroma Utils")
logger.set_level('info')


class ChromaUtils:
    _instance = None
    client = None
    collection = None
    db_path = None
    db_embed = None
    embedding = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            logger.log("Creating chroma utils", 'debug')
            cls.config = Config()
            cls._instance = super(ChromaUtils, cls).__new__(cls, *args, **kwargs)
            cls._instance.init_embeddings()
            cls._instance.init_storage()
        return cls._instance

    def __init__(self):
        # Add your initialization code here
        pass

    def init_embeddings(self):
        self.db_path, self.db_embed = self.config.chromadb()

        if self.db_embed == 'openai_ada2':
            # Get API keys from environment variables
            openai_api_key = os.getenv('OPENAI_API_KEY')

            # Embeddings - need to handle embedding errors gracefully
            self.embedding = embedding_functions.OpenAIEmbeddingFunction(
                api_key=openai_api_key,
                model_name="text-embedding-ada-002"
            )
        elif self.db_embed == 'all-distilroberta-v1':
            self.embedding = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-distilroberta-v1")
        elif self.db_embed == 'gte-base':
            self.embedding = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="gte-base")
        else:
            self.embedding = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L12-v2")

    def init_storage(self):
        if self.client is None:
            if self.db_path:
                self.client = chromadb.PersistentClient(path=self.db_path, settings=Settings(allow_reset=True))
            else:
                self.client = chromadb.EphemeralClient()

    def select_collection(self, collection_name):
        try:
            self.collection = self.client.get_or_create_collection(collection_name,
                                                                   embedding_function=self.embedding,
                                                                   metadata={"hnsw:space": "cosine"})
        except Exception as e:
            raise ValueError(f"\n\nError getting or creating collection. Error: {e}")


    def delete_collection(self, collection_name):
        try:
            self.client.delete_collection(collection_name)
        except Exception as e:
            print("\n\nError deleting collection: ", e)

    def collection_list(self):
        return self.client.list_collections()

    def peek(self, collection_name):
        self.select_collection(collection_name)

        max_result_count = self.collection.count()
        num_results = min(1, max_result_count)

        if num_results > 0:
            result = self.collection.peek()
        else:
            result = {'documents': "No Results!"}

        return result

    def load_collection(self, params):
        try:
            collection_name = params.pop('collection_name', 'default_collection_name')

            self.select_collection(collection_name)

            where = params.pop('filter', {})
            if where:
                params.update(where=where)
            data = self.collection.get(**params)

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
            self.collection.upsert(
                documents=documents,
                metadatas=meta,
                ids=ids
            )

        except Exception as e:
            raise ValueError(f"\n\nError saving results. Error: {e}")

    def query_memory(self, params, num_results=1):
        collection_name = params.get('collection_name', None)
        self.select_collection(collection_name)

        max_result_count = self.collection.count()
        num_results = min(num_results, max_result_count)

        if num_results > 0:
            query = params.pop('query', None)
            filter_condition = params.pop('filter', None)
            include = params.pop('include', ["documents", "metadatas", "distances"])

            if query is not None:
                result = self.collection.query(
                    query_texts=[query],
                    n_results=num_results,
                    where=filter_condition,
                    include=include
                )
            else:
                embeddings = params.pop('embeddings', None)

                if embeddings is not None:
                    result = self.collection.query(
                        query_embeddings=embeddings,
                        n_results=num_results,
                        where=filter_condition,
                        include=include
                    )
                else:
                    raise ValueError(f"\n\nError: No query nor embeddings were provided!")
        else:
            result = {'documents': "No Results!"}

        return result

    def reset_memory(self):
        self.client.reset()

    def search_storage_by_threshold(self, parameters):
        from scipy.spatial import distance

        collection_name = parameters.pop('collection_name', None)
        num_results = parameters.pop('num_results', 1)
        threshold = parameters.pop('threshold', 0.7)
        query_text = parameters.pop('query', None)

        query_emb = self.return_embedding(query_text)

        parameters = {
            "collection_name": collection_name,
            "embeddings": query_emb,
            "include": ["embeddings", "documents", "metadatas", "distances"]
        }

        results = self.query_memory(parameters, num_results)
        dist = distance.cosine(query_emb[0], results['embeddings'][0][0])

        if dist >= threshold:
            results = {'failed': 'No action found!'}

        return results

    def return_embedding(self, text_to_embed):
        return self.embedding([text_to_embed])

    def count_collection(self, collection_name):
        self.select_collection(collection_name)
        return self.collection.count()
