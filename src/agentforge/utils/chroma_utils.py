import os
import shutil
import uuid
from datetime import datetime
from typing import Optional, Union

from scipy.spatial import distance

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from agentforge.utils.functions.Logger import Logger
from ..config import Config

logger = Logger(name="Chroma Utils")


# def transform_result_format(result):
#     """
#     Transforms the format of the loaded collection result from the original format to the specified new format.
#     Accounts for optional presence of 'metadatas', 'uris', and 'data'.
#
#     Parameters:
#     - result (dict): The original result dictionary from loading a collection.
#
#     Returns:
#     - dict: Transformed result in the new specified format.
#     """
#     transformed_result = {"documents": []}
#
#     for key, value in result.items():
#         if value and key not in ["documents", "metadatas"]:
#             transformed_result[key] = value
#
#     for doc_id, metadata, document in zip(result['ids'], result['metadatas'], result['documents']):
#         if not metadata:
#             metadata = {}
#
#         transformed_document = {
#             "id": doc_id,
#             "content": document,
#             "metadata": metadata,
#         }
#         transformed_result["documents"].append(transformed_document)
#
#     return transformed_result


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

    def select_collection(self, collection_name: str):
        """
        Selects (or creates if not existent) a collection within the storage by name.

        Parameters:
            collection_name (str): The name of the collection to select or create.

        Raises:
            ValueError: If there's an error in getting or creating the collection.
        """
        try:
            self.collection = self.client.get_or_create_collection(name=collection_name,
                                                                   embedding_function=self.embedding,
                                                                   metadata={"hnsw:space": "cosine"})
        except Exception as e:
            raise ValueError(f"\n\nError getting or creating collection. Error: {e}")

    def delete_collection(self, collection_name: str):
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

    def peek(self, collection_name: str):
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

    def load_collection(self, collection_name: str, include: dict = None, where: dict = None, where_doc: dict = None):
        """
        Loads data from a specified collection based on provided filters.
        Parameters:
            collection_name (str): The name of the collection to load from.
            include(dict, optional): Specify which data to return. Will return all results if no filters are specified.
            where (dict, optional): Filter to apply in metadata. Will return documents and metadata by default.
            where_doc (dict, optional): Filter to apply in document. Not applied if not specified.
        Returns:
            list or None: The data loaded from the collection, or None if an error occurs.
        """
        params = {}

        # Defaulting 'include' if None
        if include is None:
            include = ["documents", "metadatas"]

        params.update(include=include)

        if where is not None:
            params.update(where=where)

        if where_doc is not None:
            params.update(where_document=where_doc)

        try:
            self.select_collection(collection_name)
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

    def save_memory(self, collection_name: str, data: Union[list, str], ids: list = None, metadata: list[dict] = None):
        """
        Saves data to memory, creating or updating documents in a specified collection.

        Parameters:
            collection_name (str): The name of the collection to save to. Will be created if it doesn't exist.
            data (Union[list, str]): The documents to be saved. Can be a single document as a string or a list
             of documents. If a single string is provided, it is converted into a list with one element.
            ids (list, optional): The IDs corresponding to the documents. If not provided,
                IDs will be generated automatically.
            metadata (list[dict], optional): A list of dictionaries, each representing associated metadata for
                the corresponding document in `data`. If not provided, empty dictionaries are used for each document.

        Raises:
            ValueError: If the lengths of `data`, `ids`, and `metadata` do not match, or if other errors occur
            during the save operation.
        """

        if self.config.data['settings']['system']['SaveMemory'] is False:
            print("\n\nSaving memory is OFF. Enable 'SaveMemory' in the system.yaml to turn it ON.")
            return

        if not collection_name:
            raise ValueError("Collection name cannot be empty.")

        if not data:
            raise ValueError("Data cannot be empty.")

        # Convert to list if value comes as string
        if isinstance(data, str):
            data = [data]

        # Default ids and metadata if None
        ids = [str(uuid.uuid4()) for _ in data] if ids is None else ids
        metadata = [{} for _ in data] if metadata is None else metadata

        # Validate that data, metadata, and ids have the same length
        if not (len(data) == len(ids) == len(metadata)):
            raise ValueError("The length of data, ids, and metadata lists must match.")

        try:
            do_time_stamp = self.config.data['settings']['system'].get('ISOTimeStampMemory')
            if do_time_stamp is True:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                for m in metadata:
                    m['isotimestamp'] = timestamp

            do_time_stamp = self.config.data['settings']['system'].get('UnixTimeStampMemory')
            if do_time_stamp is True:
                timestamp = datetime.now().timestamp()
                for m in metadata:
                    m['unixtimestamp'] = timestamp

            self.select_collection(collection_name)
            self.collection.upsert(
                documents=data,
                metadatas=metadata,
                ids=ids
            )

        except Exception as e:
            raise ValueError(f"Error saving results. Error: {e}\n\nData:\n{data}")

    def query_memory(self, collection_name: str, query: Optional[Union[str, list]] = None,
                     filter_condition: Optional[dict] = None, include: Optional[list] = None,
                     embeddings: Optional[list] = None, num_results: int = 1):
        """
        Queries memory for documents matching a query within a specified collection.

        Parameters:
            collection_name (str): The name of the collection to query.
            query (Optional[Union[str, list]]): The query text or a list of query texts.
                If `None`, `embeddings` must be provided.
            filter_condition (Optional[dict]): A dictionary specifying any filters to apply to the query.
            include (Optional[list]): A list specifying which elements to include in the result
                (e.g., ["documents", "metadatas", "distances"]). Defaults to all elements if `None`.
            embeddings (Optional[list]): Query embeddings used if `query` is `None`.
                Must be provided if `query` is not specified.
            num_results (int): The maximum number of results to return. Default is 1.

        Returns:
            dict or None: The query results, or None if an error occurs.
        """
        try:
            if not collection_name:
                raise ValueError("Collection name cannot be empty.")

            self.select_collection(collection_name)

            max_result_count = self.collection.count()
            num_results = min(num_results, max_result_count)

            if num_results <= 0:
                logger.log(f"No Results Found in '{collection_name}' collection!", 'warning')
                return {}

            # Defaulting 'include' if None
            if include is None:
                include = ["documents", "metadatas", "distances"]

            if query is not None:
                unformatted_result = self.collection.query(
                    query_texts=[query] if isinstance(query, str) else query,
                    n_results=num_results,
                    where=filter_condition,
                    include=include
                )

            elif embeddings is not None:
                unformatted_result = self.collection.query(
                    query_embeddings=embeddings,
                    n_results=num_results,
                    where=filter_condition,
                    include=include
                )
            else:
                raise ValueError("Error: No query nor embeddings were provided!")

            result = {}
            for key, value in unformatted_result.items():
                if value:
                    result[key] = value[0]
            return result

        except Exception as e:
            logger.log(f"Error querying memory: {e}", 'error')
            return None

    def reset_memory(self):
        """
        Resets the entire storage, removing all collections and their data.

        This method should be used with caution as it will permanently delete all data within the storage.
        """

        self.client.reset()

    def search_storage_by_threshold(self, collection_name: str, query_text: str, threshold: float = 0.7,
                                    num_results: int = 1):
        """
        Searches the storage for documents that meet a specified similarity threshold to a query.

        Parameters:
            collection_name (str): The name of the collection to search within.
            query_text (str): The text of the query to compare against the documents in the collection.
            num_results (int): The maximum number of results to return. Defaults to 1.
            threshold (float): The similarity threshold that the documents must meet or exceed. Defaults to 0.7.

        Returns:
            dict: A dictionary containing the search results if successful; otherwise, returns a dictionary
                  indicating failure if no documents meet the threshold.

        Raises:
            Exception: Logs an error message if an exception occurs during the search process.
        """
        try:
            query_emb = self.return_embedding(query_text)

            results = self.query_memory(collection_name=collection_name, embeddings=query_emb,
                                        include=["embeddings", "documents", "metadatas", "distances"],
                                        num_results=num_results)

            # We compare against the first result's embedding and `distance.cosine` returns a similarity measure.
            # May need to adjust the logic based on the actual behavior of `distance.cosine`.
            if results and 'embeddings' in results and results['embeddings']:
                dist = distance.cosine(query_emb[0], results['embeddings'][0][0])
                if dist < threshold:
                    return results
                else:
                    return {'failed': 'No documents found that meet the threshold.'}
            else:
                return {'failed': 'No documents found.'}

        except Exception as e:
            logger.log(f"Error searching storage by threshold: {e}", 'error')
            return {'failed': f"Error searching storage by threshold: {e}"}

    def return_embedding(self, text_to_embed: str):
        """
        Generates an embedding for the given text using the configured embedding function.

        Parameters:
            text_to_embed (str): The text to generate an embedding for.

        Returns:
            list: A list containing the generated embedding vector for the given text.
        """
        return self.embedding([text_to_embed])

    def count_collection(self, collection_name: str):
        """
        Counts the number of documents in a specified collection.

        Parameters:
            collection_name (str): The name of the collection to count documents in.

        Returns:
            int: The number of documents in the specified collection.
        """
        self.select_collection(collection_name)
        return self.collection.count()
