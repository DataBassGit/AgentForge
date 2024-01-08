import os
import uuid
from datetime import datetime

import chromadb
from chromadb.config import Settings
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction, OpenAIEmbeddingFunction
from pydantic import BaseModel
from typing import Union
from ..config import Config
from ..logs.logger_config import Logger

logger = Logger(name="Chroma Utils")
logger.set_level('info')


class ChromadbConfig(BaseModel):
    chroma_db_path: str
    chroma_db_embed: str
    client: ClientAPI
    collection: Collection
    db_path: str
    db_embed: str
    embedding: Union[SentenceTransformerEmbeddingFunction , OpenAIEmbeddingFunction]

class EmbeddingFunctions(BaseModel):
    embedding_function: Union[SentenceTransformerEmbeddingFunction , OpenAIEmbeddingFunction]
    def __init__(self, embedding_function: Union[SentenceTransformerEmbeddingFunction , OpenAIEmbeddingFunction]):
        self.embedding_function = embedding_function

    def getEmbeddingFunction(self, text: str):
        embeddings = {
            'openai_ada2': self.getOpenAIEmbeddingFunction(),
            "text-embedding-ada-002": self.getSentenceTransformerEmbeddingFunction("text-embedding-ada-002"),
            "all-MiniLM-L12-v2": self.getSentenceTransformerEmbeddingFunction("all-MiniLM-L12-v2"),
            "gte-base": self.getSentenceTransformerEmbeddingFunction("gte-base"),
            "all-distilroberta-v1": self.getSentenceTransformerEmbeddingFunction("all-distilroberta-v1"),
        }
        return embeddings[text]()

    def getSentenceTransformerEmbeddingFunction(self, name):
        return SentenceTransformerEmbeddingFunction(model_name=name)
    def getOpenAIEmbeddingFunction(self):
        return OpenAIEmbeddingFunction(api_base=os.getenv(key='OPENAI_API_BASE'), api_key=os.getenv('OPENAI_API_KEY'), model_name="text-embedding-ada-002")

    

class ChromaUtils(ChromadbConfig):
    _instance = None
    embedding_functions: EmbeddingFunctions

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            logger.log("Creating chroma utils", 'debug')
            cls.config = Config()
            cls._instance = super(ChromaUtils, cls).__new__(cls, *args, **kwargs)
            cls._instance.init_embeddings()
            cls._instance.init_storage()
        return cls._instance

    def __init__(self):
        pass# Add your initialization code here

    def init_embeddings(self):
        self.db_path, self.db_embed = str( self.config.chromadb())
        self.embedding = self.embedding_functions.getEmbeddingFunction(self.db_embed)

    def init_storage(self):
        if self.client is None:
            if self.db_path:
                self.client = chromadb.PersistentClient(path=self.db_path, settings=Settings(allow_reset=True))
            else:
                self.client = chromadb.EphemeralClient()

    def select_collection(self, collection_name):
        if not collection_name:
            collection_name = 'default_collection_name'
        try:
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_functions.getEmbeddingFunction(self.db_embed),
            metadata={"hnsw:space": "cosine"}) 
            return self.collection
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
        dist = distance.cosine(query_emb[0], num_results['embeddings'][0][0])

        if dist >= threshold:
            results = {'failed': 'No action found!'}

        return results

    def return_embedding(self, text_to_embed):
        return self.embedding([text_to_embed])

    def count_collection(self, collection_name):
        self.select_collection(collection_name=collection_name)
        return len(list(self.collection))