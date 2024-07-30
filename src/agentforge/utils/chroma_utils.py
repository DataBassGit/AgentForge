import os
import uuid
# from pathlib import Path
from datetime import datetime
from typing import Optional, Union

# from scipy.spatial import distance

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from agentforge.utils.functions.Logger import Logger
from ..config import Config

logger = Logger(name="Chroma Utils")
os.environ["TOKENIZERS_PARALLELISM"] = "false"


def validate_inputs(collection_name: str, data: Union[list, str], ids: list, metadata: list[dict]):
    """
    Validates the inputs for the save_memory method.

    Parameters:
        collection_name (str): The name of the collection.
        data (Union[list, str]): The documents to be saved.
        ids (list): The IDs for the documents.
        metadata (list[dict]): The metadata for the documents.

    Raises:
        ValueError: If any of the inputs are invalid.
    """
    if not collection_name:
        raise ValueError("Collection name cannot be empty.")

    if not data:
        raise ValueError("Data cannot be empty.")

    if not (len(data) == len(ids) == len(metadata)):
        raise ValueError("The length of data, ids, and metadata lists must match.")


def generate_defaults(data: Union[list, str], ids: list = None, metadata: list[dict] = None):
    """
    Generates default values for ids and metadata if they are not provided.

    Parameters:
        data (Union[list, str]): The documents to be saved.
        ids (list, optional): The IDs for the documents.
        metadata (list[dict], optional): The metadata for the documents.

    Returns:
        tuple: A tuple containing the generated ids and metadata.
    """
    if isinstance(data, str):
        data = [data]

    ids = [str(uuid.uuid4()) for _ in data] if ids is None else ids
    metadata = [{} for _ in data] if metadata is None else metadata

    return ids, metadata


def apply_timestamps(metadata: list[dict], config):
    """
    Applies timestamps to the metadata if required by the configuration.

    Parameters:
        metadata (list[dict]): The metadata for the documents.
        config (dict): The configuration dictionary.
    """
    do_time_stamp = config['settings']['system'].get('ISOTimeStampMemory')
    if do_time_stamp:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for m in metadata:
            m['isotimestamp'] = timestamp

    do_time_stamp = config['settings']['system'].get('UnixTimeStampMemory')
    if do_time_stamp:
        timestamp = datetime.now().timestamp()
        for m in metadata:
            m['unixtimestamp'] = timestamp


def save_to_collection(collection, data: list, ids: list, metadata: list[dict]):
    """
    Saves the data to the collection.

    Parameters:
        collection: The collection object.
        data (list): The documents to be saved.
        ids (list): The IDs for the documents.
        metadata (list[dict]): The metadata for the documents.
    """
    collection.upsert(
        documents=data,
        metadatas=metadata,
        ids=ids
    )


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

    # def __new__(cls, *args, **kwargs):
    #     """
    #     Ensures a single instance of ChromaUtils is created (singleton pattern). Initializes embeddings and storage
    #     upon the first creation.
    #
    #     Returns:
    #         ChromaUtils: The singleton instance of the ChromaUtils class.
    #     """
    #     pass
    #     if not cls._instance:
    #         logger.log("Creating chroma utils", 'debug')
    #         cls.config = Config()
    #         cls._instance = super(ChromaUtils, cls).__new__(cls, *args, **kwargs)
    #         cls._instance.init_embeddings()
    #         cls._instance.init_storage()
    #     return cls._instance

    def __init__(self, persona_name="default"):
        """
        Ensures an instance of ChromaUtils is created. Initializes embeddings and storage
        upon creation.
        """
        self.persona_name = persona_name
        self.config = Config()
        self.init_embeddings()
        self.init_storage()

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

            if self.config.data['settings']['storage']['ChromaDB'].get('DBFreshStart'):
                self.reset_memory()
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
            db_path = str(self.config.project_root / db_path_setting / self.persona_name)
            # if self.persona_name is not None:
            #     db_path = f"{db_path}/{self.persona_name}"

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
            num_results = min(10, max_result_count)

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
            print("\nMemory Saving is Disabled. To Enable Memory Saving, set the 'SaveMemory' flag to 'true' in the "
                  "system.yaml file.\n")
            return

        try:
            data = [data] if isinstance(data, str) else data

            ids, metadata = generate_defaults(data, ids, metadata)

            validate_inputs(collection_name, data, ids, metadata)

            apply_timestamps(metadata, self.config.data)

            self.select_collection(collection_name)

            save_to_collection(self.collection, data, ids, metadata)

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

            # Set num_results to max_result_count if it is 0, indicating no limit.
            if num_results == 0:
                num_results = max_result_count
            else:
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
                raise ValueError("Error: No query nor embeddings were provided! Try load_collection instead.")

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

    def search_storage_by_threshold(self, collection_name: str, query: str, threshold: float = 0.8,
                                    num_results: int = 1):
        """
        Searches the storage for documents that meet a specified similarity threshold to a query.

        Parameters:
            collection_name (str): The name of the collection to search within.
            query (str): The text of the query to compare against the documents in the collection.
            num_results (int): The maximum number of results to return. Default is 1.
            threshold (float): The similarity threshold that the documents must meet or exceed. Defaults to 0.8.

        Returns:
            dict: A dictionary containing the search results if successful; otherwise, returns an empty
             dictionary if no documents are found or meet the threshold.

        Raises:
            Exception: Logs an error message if an exception occurs during the search process.
        """
        try:
            query_emb = self.return_embedding(query)

            results = self.query_memory(collection_name=collection_name, embeddings=query_emb,
                                        include=["documents", "metadatas", "distances"],
                                        num_results=num_results)

            # We compare against the first result's embedding and `distance.cosine` returns
            # a similarity measure. May need to adjust the logic based on the actual behavior
            # of `distance.cosine`.
            # dist = distance.cosine(query_emb[0], results['embeddings'][0])
            if results:
                filtered_data = {
                    key: [value for value, dist in zip(results[key], results['distances']) if dist < threshold]
                    for key in results
                }
                if filtered_data['documents']:
                    return filtered_data
                else:
                    logger.log('Search by Threshold: No documents found that meet the threshold.', 'info')
            else:
                logger.log('Search by Threshold: No documents found.', 'info')

            return {}

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

    def search_metadata_min_max(self, collection_name, metadata_tag, min_max):
        """
        Retrieves the collection entry with the minimum or maximum value for the specified metadata tag.

        Args:
            collection_name: The ChromaDB collection object.
            metadata_tag: The name of the metadata tag to consider for finding the minimum or maximum value.
            min_max: The type of value to retrieve. Can be either "min" for minimum or "max" for maximum.
                     Default is "max".

        Returns:
            The collection entry with the minimum or maximum value for the specified metadata tag,
            or None if no entries are found or if the metadata tag contains non-numeric values.
        """
        try:
            # Retrieve only the document IDs and the specified metadata tag
            self.select_collection(collection_name)
            results = self.collection.get(include=["metadatas"])

            # Extract the metadata values and document IDs
            metadata_values = [entry[metadata_tag] for entry in results["metadatas"]]
            document_ids = results["ids"]

            # Check if all metadata values are numeric (int or float)
            if not all(isinstance(value, (int, float)) for value in metadata_values):
                logger.log(f"Error: The metadata tag '{metadata_tag}' contains non-numeric values.", 'error')
                return None

            if metadata_values:
                if min_max == "min":
                    target_index = metadata_values.index(min(metadata_values))
                else:
                    try:
                        target_index = metadata_values.index(max(metadata_values))
                    except:
                        logger.log(f"Error: The metadata tag '{metadata_tag}' is empty or does not exist. Returning 0.", 'error')
                        target_index = 0
            else:
                target_index = 0

            try:
                # Retrieve the full entry with the highest metadata value
                target_entry = self.collection.get(ids=[document_ids[target_index]], include=["documents", "metadatas"])

                max_metadata = {
                    "ids": target_entry["ids"][0],
                    "target": target_entry["metadatas"][0][metadata_tag],
                    "metadata": target_entry["metadatas"][0],
                    "document": target_entry["documents"][0],
                }

                logger.log(
                    f"Found the following record by max value of {metadata_tag} metadata tag:\n{max_metadata}",
                    'debug'
                )
                return max_metadata
            except:
                return None

        except (KeyError, ValueError, IndexError) as e:
            logger.log(f"Error finding max metadata: {e}\nCollection: {collection_name}\nTarget Metadata: {metadata_tag}", 'error')
            return None

    def delete_memory(self, collection_name, doc_id):
        self.select_collection(collection_name)
        self.collection.delete(ids=[doc_id])
