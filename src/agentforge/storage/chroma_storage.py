# src/agentforge/storage/chroma_storage.py

import os
import uuid
from datetime import datetime
from typing import Optional, Union

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

    def _is_allowed_save_memory(self):
        save_allowed = self.config.data['settings']['storage']['options']['save_memory']
        if not save_allowed:
            self.logger.log("\nMemory Saving is Disabled. To Enable Memory Saving, set the 'save_memory' flag "
                            "to 'true' in the system.yaml file.\n", 'info')

        return save_allowed

    @staticmethod
    def _generate_defaults(data, ids, metadata):
        if isinstance(data, str):
            data = [data]

        ids = [str(uuid.uuid4()) for _ in data] if ids is None else ids
        metadata = [{} for _ in data] if metadata is None else metadata

        return ids, metadata

    @staticmethod
    def _process_data(data):
        return [data] if isinstance(data, str) else data

    def _save_to_collection(self, collection_name: str, data: list, ids: list, metadata: list[dict]):
        """
        Saves the data to the collection.

        Parameters:
            collection_name (str): The name of the collection or table.
            data (list): The documents to be saved.
            ids (list): The IDs for the documents.
            metadata (list[dict]): The metadata for the documents.
        """
        collection = self.select_collection(collection_name)
        try:
            collection.upsert(
                ids=ids,
                documents=data,
                metadatas=metadata
            )
        except Exception as e:
            raise ValueError(f"Error saving to collection '{collection_name}'. Error: {e}\n"
                             f"IDs:\n{ids}\n"
                             f"Data:\n{data}\n"
                             f"Metadata:\n{metadata}")

    @staticmethod
    def _are_inputs_valid(collection_name, data, ids, metadata):
        if not collection_name:
            raise ValueError("Collection name cannot be empty.")

        if not data:
            raise ValueError("Data cannot be empty.")

        if not (len(data) == len(ids) == len(metadata)):
            raise ValueError("The length of data, ids, and metadata lists must match.")

    def _apply_iso_timestamps(self, metadata: list[dict]):
        do_time_stamp = self.config.data['settings']['storage']['options'].get('iso_timestamp', False)
        if do_time_stamp:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for m in metadata:
                m['iso_timestamp'] = timestamp

    def _apply_unix_timestamps(self, metadata: list[dict]):
        do_time_stamp = self.config.data['settings']['storage']['options'].get('unix_timestamp', False)
        if do_time_stamp:
            timestamp = datetime.now().timestamp()
            for m in metadata:
                m['unix_timestamp'] = timestamp

    def _apply_timestamps(self, metadata: list[dict]):
        self._apply_iso_timestamps(metadata)
        self._apply_unix_timestamps(metadata)

    # ---------------------------------
    # Implementation
    # ---------------------------------

    def connect(self):
        self._init_storage()
        self._init_embeddings()
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

    def select_collection(self, collection_name):
        """
        Select a particular 'collection' or table within the DB.
        """
        self._is_client_connected()
        params = self._get_collection_params()
        return self.client.get_collection(collection_name, params['embedding_function'])

    def select_or_create_collection(self, collection_name):
        """
        Select a particular 'collection' or table within the DB.
        Automatically create the given collection or table if it does not already exist.
        """
        self._is_client_connected()
        params = self._get_collection_params()
        return self.client.get_or_create_collection(collection_name, **params)

    def reset_storage(self):
        """
        Resets the selected client storage
        """
        self._is_client_connected()
        self.client.reset()

    def insert(self, collection_name: str, data: Union[list, str], ids: list = None, metadata: list[dict] = None):
        # Check if method is allowed to run
        self._is_client_connected()
        if not self._is_allowed_save_memory():
            return

        # Actual implementation
        data = self._process_data(data)
        ids, metadata = self._generate_defaults(data, ids, metadata)
        self._are_inputs_valid(collection_name, data, ids, metadata)
        self._apply_timestamps(metadata)
        self._save_to_collection(collection_name, data, ids, metadata)

    # NEEDS WORK !!!
    def query(self, collection_name: str, ids: Optional[list[str]] = None,
              query: Optional[Union[str, list]] = None, where: Optional[dict] = None,
              include: Optional[list] = None, embeddings: Optional[list] = None, num_results: int = 1):

        self._is_client_connected()

        if not collection_name:
            raise ValueError("Collection name cannot be empty.")

        collection = self.select_collection(collection_name)

        # Set num_results to max_result_count if it is 0, indicating no limit.
        # max_result_count = collection.count()
        # if num_results == 0:
        #     num_results = max_result_count
        # else:
        #     num_results = min(num_results, max_result_count)
        #
        # if num_results <= 0:
        #     logger.log(f"No Results Found in '{collection_name}' collection!", 'warning')
        #     return {}

        # Defaulting 'include' if None
        # if include is None:
        #     include = ["documents", "metadatas", "distances"]
        include = include if include else ["documents", "metadatas", "distances"]

        if ids is not None:
            unformatted_result = collection.get(
                ids=ids,
                # where=where,
                # include=include
            )
        elif query is not None:
            unformatted_result = collection.query(
                query_texts=[query] if isinstance(query, str) else query,
                n_results=num_results,
                where=where,
                include=include
            )
        elif embeddings is not None:
            unformatted_result = collection.query(
                query_embeddings=embeddings,
                n_results=num_results,
                where=where,
                include=include
            )
        else:
            raise ValueError("Error: No query nor embeddings were provided! Try load_collection instead.")

        return unformatted_result

        # We’ll reconstruct the results
        # result = {}
        # for key, value in unformatted_result.items():
        #     if value:
        #         result[key] = value[0]
        # return result

    def update(self, collection_name: str, new_data: Union[list, str], ids: list = None, metadata: list[dict] = None):
        """
        We can handle updates in Chroma by using the insert method which automatically updates existing data
        """
        self.insert(collection_name, new_data, ids, metadata)

    def delete(self, collection_name, ids: Optional[list] = None, where: Optional[dict] = None):
        """
        Find the records, then remove them by ID.
        """
        self._is_client_connected()
        collection = self.client.get_or_create_collection(name=collection_name)

        collection.delete(
            ids=ids,
            where=where
        )

    def count(self, collection_name):
        self._is_client_connected()
        params = self._get_collection_params()
        collection = self.client.get_collection(name=collection_name, embedding_function=params['embedding_function'] )
        return collection.count()
