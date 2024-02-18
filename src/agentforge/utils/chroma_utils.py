import os
import uuid
from collections.abc import Iterable
from datetime import datetime

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from ..config import Config
from agentforge.utils.functions.Logger import Logger

logger = Logger(name="Chroma Utils")


class ChromaUtils:
    """
    A utility class for managing interactions with ChromaDB, offering a range of functionalities including
    initialization, data insertion, query, and collection management.

    This class utilizes a singleton pattern to ensure a single instance manages storage interactions across
    the application.
    """

    _instance = None
    client = None
    collection = None
    db_path = None
    db_embed = None
    embedding = None

    def __new__(cls, *args, **kwargs):
        """
        Ensures a single instance of ChromaUtils is created (singleton pattern). Initializes embeddings and storage
        upon the first creation.

        Returns:
            ChromaUtils: The singleton instance of the ChromaUtils class.
        """
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
        """
        Initializes the embedding function based on the configuration, supporting multiple embedding backends.

        Raises:
            KeyError: If a required environment variable or setting is missing.
            Exception: For any errors that occur during the initialization of embeddings.
        """
        try:
            self.db_path, self.db_embed = self.chromadb_settings()

            # Initialize embedding based on the specified backend in the configuration
            if self.db_embed == 'openai_ada2':
                openai_api_key = os.getenv('OPENAI_API_KEY')
                self.embedding = embedding_functions.OpenAIEmbeddingFunction(
                    api_key=openai_api_key,
                    model_name="text-embedding-ada-002"
                )
            elif self.db_embed == 'all-distilroberta-v1':
                self.embedding = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-distilroberta-v1")
            # Additional embeddings can be initialized here similarly
            else:
                self.embedding = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L12-v2")
        except KeyError as e:
            logger.log(f"Missing environment variable or setting: {e}", 'error')
            raise
        except Exception as e:
            logger.log(f"Error initializing embeddings: {e}", 'error')
            raise

    def init_storage(self):
        """
        Initializes the storage client, either as a persistent client with a specified database path or as an
        ephemeral client based on the configuration.

        Raises:
            Exception: For any errors that occur during the initialization of storage.
        """
        try:
            if self.client is None:
                if self.db_path:
                    self.client = chromadb.PersistentClient(path=self.db_path, settings=Settings(allow_reset=True))
                else:
                    self.client = chromadb.EphemeralClient()
        except Exception as e:
            logger.log(f"Error initializing storage: {e}", 'error')
            raise

    def chromadb_settings(self):
        """
        Retrieves the ChromaDB settings from the configuration.

        Returns:
            tuple: A tuple containing the database path and embedding settings.
        """
        # Retrieve the ChromaDB settings
        db_settings = self.config.data['settings']['storage'].get('ChromaDB', {})

        # Get the database path and embedding settings
        db_path_setting = db_settings.get('persist_directory', None)
        db_embed = db_settings.get('embedding', None)

        # Construct the absolute path of the database using the project root
        if db_path_setting:
            db_path = str(self.config.project_root / db_path_setting)
        else:
            db_path = None

        return db_path, db_embed

    def select_collection(self, collection_name):
        """
        Selects (or creates if not existent) a collection within the storage by name.

        Parameters:
            collection_name (str): The name of the collection to select or create.

        Raises:
            ValueError: If there's an error in getting or creating the collection.
        """
        try:
            self.collection = self.client.get_or_create_collection(collection_name,
                                                                   embedding_function=self.embedding,
                                                                   metadata={"hnsw:space": "cosine"})
        except Exception as e:
            raise ValueError(f"\n\nError getting or creating collection. Error: {e}")

    def delete_collection(self, collection_name):
        """
        Deletes a collection from the storage by its name.

        Parameters:
            collection_name (str): The name of the collection to delete.
        """
        try:
            self.client.delete_collection(collection_name)
        except Exception as e:
            print("\n\nError deleting collection: ", e)

    def collection_list(self):
        """
        Lists all collections currently in the storage.

        Returns:
            list: A list of collection names.
        """
        return self.client.list_collections()

    def peek(self, collection_name):
        """
        Peeks into a collection to retrieve a brief overview of its contents.

        Parameters:
            collection_name (str): The name of the collection to peek into.

        Returns:
            dict or None: A dictionary containing a brief overview of the collection's contents or None if an error occurs.
        """
        try:
            self.select_collection(collection_name)

            max_result_count = self.collection.count()
            num_results = min(1, max_result_count)

            if num_results > 0:
                result = self.collection.peek()
            else:
                result = {'documents': "No Results!"}

            return result
        except Exception as e:
            logger.log(f"Error peeking collection: {e}", 'error')
            return None

    def load_collection(self, params):
        """
       Loads data from a specified collection based on provided parameters.

       Parameters:
           params (dict): Parameters specifying the collection to load from and any filters to apply.

       Returns:
           list or None: The data loaded from the collection, or None if an error occurs.
       """
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
        """
        Saves data to memory, creating or updating documents in a specified collection.

        Parameters:
            params (dict): Parameters specifying the collection to save to, documents, and any associated metadata.

        Raises:
            ValueError: If an error occurs during the save operation.
        """
        if self.config.data['settings']['system']['SaveMemory'] is False:
            return

        try:
            # Ensure collection_name is a string
            collection_name = params.pop('collection_name', None)
            if not isinstance(collection_name, str):
                raise ValueError("The 'collection_name' parameter should be a string.")

            # Ensure documents is an iterable
            documents = params.pop('data', [])
            # Check if documents is an iterable, raise ValueError if not
            if not isinstance(documents, Iterable) or documents is None:
                raise ValueError("The 'documents' parameter should be an iterable.")

            ids = params.pop('ids', [str(uuid.uuid4()) for _ in documents])

            if collection_name and documents:
                meta = params.pop('metadata', [{} for _ in documents])

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
        """
        Queries memory for documents matching a query within a specified collection.

        Parameters:
            params (dict): Parameters specifying the collection to query, the query text or embeddings, and any filters.
            num_results (int): The maximum number of results to return.

        Returns:
            dict or None: The query results, or None if an error occurs.
        """
        try:
            # Ensure collection_name is a string
            collection_name = params.pop('collection_name', None)
            if not isinstance(collection_name, str):
                raise ValueError("The 'collection_name' parameter should be a string.")

            self.select_collection(collection_name)

            max_result_count = self.collection.count()
            num_results = min(num_results, max_result_count)

            if num_results > 0:
                query = params.pop('query', None)
                filter_condition = params.pop('filter', None)
                include = params.pop('include', [])

                if include is None:
                    include = ["documents", "metadatas", "distances"]

                if query is not None:
                    result = self.collection.query(
                        query_texts=[query] if isinstance(query, str) else query,
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
                logger.log(f"No Results Found in '{collection_name}' collection!", 'warning')
                return {}

            return result
        except Exception as e:
            logger.log(f"Error querrying memory: {e}", 'error')
            return None

    def reset_memory(self):
        """
        Resets the entire storage, removing all collections and their data.

        This method should be used with caution as it will permanently delete all data within the storage.
        """
        self.client.reset()

    def search_storage_by_threshold(self, parameters):
        """
        Searches the storage for documents that meet a specified similarity threshold to a query.

        Parameters:
            parameters (dict): A dictionary containing the search parameters, including the collection name,
                                the number of results, the similarity threshold, and the query text.

        Returns:
            dict: A dictionary containing the search results if successful; otherwise, returns a dictionary
                  indicating failure if no documents meet the threshold.

        Raises:
            Exception: Logs an error message if an exception occurs during the search process.
        """
        try:
            from scipy.spatial import distance

            collection_name = parameters.pop('collection_name', None)
            num_results = parameters.pop('num_results', 1)
            threshold = parameters.pop('threshold', 0.7)
            query_text = parameters.pop('query', '')

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
        except Exception as e:
            logger.log(f"Error searching storage by threshold: {e}", 'error')
            return None

    def return_embedding(self, text_to_embed):
        """
        Generates an embedding for the given text using the configured embedding function.

        Parameters:
            text_to_embed (str): The text to generate an embedding for.

        Returns:
            list: A list containing the generated embedding vector for the given text.
        """
        return self.embedding([text_to_embed])

    def count_collection(self, collection_name):
        """
        Counts the number of documents in a specified collection.

        Parameters:
            collection_name (str): The name of the collection to count documents in.

        Returns:
            int: The number of documents in the specified collection.
        """
        self.select_collection(collection_name)
        return self.collection.count()
