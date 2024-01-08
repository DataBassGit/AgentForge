import os
import uuid
from datetime import datetime

from weaviate import Client
from weaviate.batch import Batch

class WeaviateUtils:

    _instance = None
    client = None
    collection = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(WeaviateUtils, cls).__new__(cls, *args, **kwargs)
            cls._instance.init_client()
        return cls._instance

    def init_client(self):
        self.client = Client(url="http://localhost:8080")

    def create_schema(self, schema):
        self.client.schema.create(schema)

    def select_collection(self, collection_name):
        self.collection = self.client.collections[collection_name]

    def delete_collection(self, collection_name):
        self.client.collections.delete(collection_name)

    def collection_list(self):
        return self.client.collections.list()

    def peek(self, collection_name):
        self.select_collection(collection_name)
        result = self.collection.get()
        return result

    def load_collection(self, params):
        collection_name = params.pop('collection_name')
        self.select_collection(collection_name)
        result = self.collection.get(params)
        return result

    def save_batch(self, params):
        collection_name = params.pop('collection_name')
        objects = params.pop('objects')

        self.select_collection(collection_name)
        batch = Batch(self.collection)

        for obj in objects:
            batch.add_data_object(obj)

        batch.execute()

    def query(self, params):
        collection_name = params.pop('collection_name')
        self.select_collection(collection_name)

        result = self.collection.query(params)
        return result

    # other methods
    # Reset weaviate data
    def reset(self):
        self.client.data_object.delete_all()

    # Text embedding
    def embed_text(self, text):
        result = self.client.text2vec.embed({
            "text": text
        })
        return result["vector"]

    # Search by vector similarity
    def vector_search(self, vector, params):
        result = self.client.query.vector(
            vector=vector,
            params=params
        )
        return result

    # Delete objects
    def delete_objects(self, className, ids):
        self.client.data_object.delete(className, ids)

        # Pagination

    def get_objects_paginated(self, className, params):
        return self.client.data_object.get_paginate(className, params)