# src/agentforge/storage/chroma_storage.py

import os
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from agentforge.storage.base_storage import BaseStorage

class ChromaStorage(BaseStorage):

    # ---------------------------------
    # Initialization
    # ---------------------------------

    def __init__(self):
        super().__init__()
        self.client = None
        self.embedding_function = None

    def _init_storage(self):
        # Ephemeral Storage
        if not self.storage_path:
            self.client = chromadb.EphemeralClient()
            return

        # Persistent Storage
        self.client = chromadb.PersistentClient(path=str(self.storage_path), settings=Settings(allow_reset=True))

    def _init_embeddings(self):
        # Initialize embedding based on the specified backend in the configuration
        if self.storage_embedding == 'openai_ada2':
            openai_api_key = os.getenv('OPENAI_API_KEY')
            self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
                model_name="text-embedding-ada-002",
                api_key=openai_api_key
            )
            return

        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=self.storage_embedding
        )
    # ---------------------------------
    # Internal Methods
    # ---------------------------------

    def _is_client_connected(self):
        if not self.client:
            raise ValueError("No Chroma client. Did you call connect() first?")

    def _is_storage_fresh_start(self):
        # Wipe storage on start if set to Fresh Start
        if self.config.data['settings']['storage']['options'].get('fresh_start', False):
            self.reset_storage()

    def _get_collection_params(self):
        return {
            'embedding_function': self.embedding_function,
            'metadata': self.storage_configuration['metadata'],
        }
    # ---------------------------------
    # Implementation
    # ---------------------------------

    def connect(self):
        self._init_storage()
        self._is_storage_fresh_start()

    def disconnect(self):
        # Chroma doesn’t necessarily require a formal disconnection, but let’s just set self.client to None.
        self.client = None

    def create_collection(self, collection_name):
        self._is_client_connected()
        params = self._get_collection_params()
        self.client.create_collection(collection_name, **params)

    def delete_collection(self, collection_name):
        self._is_client_connected()
        self.client.delete_collection(name=collection_name)

    def set_current_collection(self, collection_name):
        """
        Select or focus on a particular 'collection' or table within the DB.
        Returns an object or handle representing that collection, or modifies state.
        """
        self._is_client_connected()
        params = self._get_collection_params()
        self.current_collection = self.client.get_collection(collection_name, **params)

    def set_or_create_current_collection(self, collection_name):
        """
        Select a collection (or table) within the database. Will create the collection if it does not exist.
        """
        self._is_client_connected()
        params = self._get_collection_params()
        self.current_collection = self.client.get_or_create_collection(collection_name, **params)

    def reset_storage(self):
        """
        Resets the selected client storage
        """
        self._is_client_connected()
        self.client.reset()

    # ---------------------------------
    # PENDING - THERE ARE PLACEHOLDER CONCEPTS FROM GPT
    # ---------------------------------

    def insert(self, collection_name, data):
        """
        data is expected to be a list of dicts. Each dict might contain an 'id' field, plus anything else.
        We'll parse them to fit Chroma's expected arguments.
        """
        self._is_client_connected()
        collection = self.client.get_or_create_collection(name=collection_name)

        # We need at least 'ids' to pass to upsert, and optionally 'documents' or 'metadatas'.
        # This is somewhat simplified: you might have different logic for how to handle doc content vs. metadata.
        ids = []
        documents = []
        metadatas = []

        for item in data:
            ids.append(item["id"])
            # Let's assume all the other keys except 'id' go in 'metadatas'
            # Or perhaps you store a "content" field in documents.
            content = item.get("content", "")
            documents.append(content)
            # filter out "id" and "content" so the rest is metadata
            meta = {k: v for k, v in item.items() if k not in ["id", "content"]}
            metadatas.append(meta)

        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def query(self, collection_name, query):
        """
        Here we’re using a naive approach: if query is something like {"id": "2"},
        we treat that as a 'where' filter in Chroma. Or you might do more advanced logic.
        We’ll return a list of dicts that represent each record.
        """
        self._is_client_connected()
        collection = self.client.get_or_create_collection(name=collection_name)

        # For simplicity, assume we only handle one key in the query.
        # Real usage might need more sophisticated handling.
        results = collection.get(where=query, include=["metadatas", "documents", "embeddings"])

        # We’ll reconstruct them into a list of dicts:
        output = []
        for doc_id, doc_text, doc_meta in zip(results["ids"], results["documents"], results["metadatas"]):
            record = {"id": doc_id, "content": doc_text, **doc_meta}
            output.append(record)
        return output

    def update(self, collection_name, query, new_data):
        """
        We can handle updates in Chroma by retrieving the items via query,
        then upserting them again with the new data.
        """
        self._is_client_connected()
        collection = self.client.get_or_create_collection(name=collection_name)

        existing_records = self.query(collection_name, query)
        if not existing_records:
            return  # no-op if we don't find anything

        # Update each record with new_data
        for record in existing_records:
            record.update(new_data)

        # Now upsert them again
        ids = []
        documents = []
        metadatas = []

        for record in existing_records:
            ids.append(record["id"])
            documents.append(record.get("content", ""))
            meta = {k: v for k, v in record.items() if k not in ["id", "content"]}
            metadatas.append(meta)

        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def delete(self, collection_name, query):
        """
        Find the records, then remove them by ID.
        """
        self._is_client_connected()
        collection = self.client.get_or_create_collection(name=collection_name)

        records_to_delete = self.query(collection_name, query)
        if not records_to_delete:
            return

        ids_to_delete = [r["id"] for r in records_to_delete]
        collection.delete(ids=ids_to_delete)

    def count(self, collection_name):
        self._is_client_connected()
        params = self._get_collection_params()
        collection = self.client.get_collection(name=collection_name, embedding_function=params['embedding_function'] )
        return collection.count()


