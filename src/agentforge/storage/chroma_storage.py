import re
import os
import uuid
from datetime import datetime
from typing import Optional, Union
import threading

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from scipy.ndimage import value_indices

from agentforge.utils.logger import Logger
from agentforge.config import Config

logger = Logger(name="Chroma Utils", default_logger='chroma_utils')
os.environ["TOKENIZERS_PARALLELISM"] = "false"

##########################################################
# Section 1: Static Methods
##########################################################

def validate_collection_name(collection_name: str):
    # We expected a collection name that:
    # (1) contains 3-63 characters
    # (2) starts and ends with an alphanumeric character
    # (3) otherwise contains only alphanumeric characters, underscores or hyphens (-)
    # (4) contains no two consecutive periods (..) and
    # (5) is not a valid IPv4 address.

    if not collection_name:
        raise ValueError("Collection name cannot be empty.")

    # Replace any invalid characters with an underscore
    collection_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', collection_name)

    # Remove consecutive periods
    while ".." in collection_name:
        collection_name = collection_name.replace("..", ".")

    # Check if the first character is not alphanumeric and remove it
    while len(collection_name) > 0 and not collection_name[0].isalnum():
        collection_name = collection_name[1:]

    # Check if the last character is not alphanumeric and remove it
    while len(collection_name) > 0 and not collection_name[-1].isalnum():
        collection_name = collection_name[:-1]

    # Ensure we don't proceed with an empty name
    if len(collection_name) <= 0:
        collection_name = "0"

    # Ensure the name starts with an alphanumeric character
    if not collection_name[0].isalnum():
        collection_name = "0" + collection_name

    # Ensure the name ends with an alphanumeric character
    if not collection_name[-1].isalnum():
        collection_name = collection_name + "0"

    # Ensure the name is at least 3 characters long
    while len(collection_name) < 3:
        collection_name = collection_name + "0"

    # Check if the name exceeds 63 characters
    if len(collection_name) > 63:
        raise ValueError(f"Collection name exceeds 63 characters. Ensure it starts/ends with alphanumeric, "
                         f"contains only alphanumeric, underscores, hyphens, and no consecutive periods.\n"
                         f"Got: '{collection_name}'")

    return collection_name

def validate_inputs(data: Union[list, str], ids: list, metadata: list[dict]):
    """
    Validates the inputs for the save_memory method.

    Parameters:
        data (Union[list, str]): The documents to be saved.
        ids (list): The IDs for the documents.
        metadata (list[dict]): The metadata for the documents.

    Raises:
        ValueError: If any of the inputs are invalid.
    """
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

def apply_iso_timestamps(metadata: list[dict], config):
    do_time_stamp = config['settings']['storage']['options'].get('iso_timestamp', False)
    if do_time_stamp:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for m in metadata:
            m['iso_timestamp'] = timestamp

def apply_unix_timestamps(metadata: list[dict], config):
    do_time_stamp = config['settings']['storage']['options'].get('unix_timestamp', False)
    if do_time_stamp:
        timestamp = datetime.now().timestamp()
        for m in metadata:
            m['unix_timestamp'] = timestamp

def apply_timestamps(metadata: list[dict], config):
    """
    Applies timestamps to the metadata if required by the configuration.

    Parameters:
        metadata (list[dict]): The metadata for the documents.
        config (dict): The configuration dictionary.
    """
    apply_iso_timestamps(metadata, config)
    apply_unix_timestamps(metadata, config)

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

##########################################################
# Section 2: ChromaDB
##########################################################


class ChromaStorage:
    """
    A utility class for managing interactions with ChromaDB, offering a range of functionalities including
    initialization, data insertion, query, and collection management.

    This class provides a thread-safe, class-level registry for sharing ChromaStorage instances
    at the desired granularity (e.g., per Cog, per persona, or via a custom storage_id).

    Key/Path Resolution:
        - If storage_id is provided: key = storage_id, path = {persist_directory}/{storage_id}
        - If personas are enabled:   key = cog:persona, path = {persist_directory}/{cog}/{persona}
        - If personas are disabled:  key = cog,        path = {persist_directory}/{cog}
        - If neither cog nor storage_id is provided: raises ValueError

    Usage:
        storage = ChromaStorage.get_or_create(cog_name, persona)
        storage = ChromaStorage.get_or_create(storage_id="my_custom_id")

    To reset the registry (e.g., between tests):
        ChromaStorage.clear_registry()

    To debug instance resolution:
        storage.describe_instance()
    """
    _registry = {}
    _registry_lock = threading.Lock()

    _instance = None
    client = None
    collection = None
    db_path = None
    db_embed = None
    embedding = None

    ##########################################################
    # Section 3: Initialization
    ##########################################################

    def __init__(self, cog_context: Optional[str] = None, persona_context: Optional[str] = None, storage_id: Optional[str] = None):
        """
        Initialize a ChromaStorage instance with explicit context.
        Requires explicit context for cog/persona or storage_id.
        """
        self.config = Config()
        self.storage_id = storage_id
        self.cog_context = cog_context
        self.persona_context = persona_context
        self._resolve_context()
        self.init_embeddings()
        self.init_storage()

    def _resolve_context(self):
        """
        Internal: Ensures context is valid and sets up for path/key resolution.
        Raises ValueError if insufficient context is provided.
        """
        personas_enabled = self.config.data['settings']['system']['persona'].get('enabled', False)
        if self.storage_id:
            # storage_id mode: ignore cog/persona for path/key
            self._resolved_key = self.storage_id
            self._resolved_path_mode = 'storage_id'
        elif self.cog_context and personas_enabled and self.persona_context:
            self._resolved_key = f"{self.cog_context}:{self.persona_context}"
            self._resolved_path_mode = 'cog_persona'
        elif self.cog_context and not personas_enabled:
            self._resolved_key = self.cog_context
            self._resolved_path_mode = 'cog_only'
        else:
            raise ValueError("ChromaStorage requires either a storage_id or cog_context (with persona if personas are enabled). Provide a unique storage_id for standalone/agent mode or when context is ambiguous.")

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

            if self.config.data['settings']['storage'].get('fresh_start'):
                self.reset_storage()
        except Exception as e:
            logger.log(f"[init_storage] Error initializing storage: {e}", 'error')
            raise

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
            if not self.db_embed:
                self.embedding = embedding_functions.DefaultEmbeddingFunction()
                return
            
            if self.db_embed == 'text-embedding-ada-002':
                openai_api_key = os.getenv('OPENAI_API_KEY')
                self.embedding = embedding_functions.OpenAIEmbeddingFunction(
                    api_key=openai_api_key,
                    model_name=self.db_embed
                )
                return
            
            if self.db_embed:
                self.embedding = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=self.db_embed)
                return

            raise ValueError(f"Unsupported embedding backend: {self.db_embed}")
        except KeyError as e:
            logger.log(f"[init_embeddings] Missing environment variable or setting: {e}", 'error')
            raise
        except Exception as e:
            logger.log(f"[init_embeddings] Error initializing embeddings: {e}", 'error')
            raise

    ##########################################################
    # Section 4: Configuration
    ##########################################################

    def chromadb_settings(self):
        """
        Retrieves the ChromaDB settings from the configuration and resolves the database path.
        - If storage_id is set, path = {persist_directory}/{storage_id}
        - If personas are enabled, path = {persist_directory}/{cog}/{persona}
        - If personas are disabled, path = {persist_directory}/{cog}
        Raises ValueError if insufficient context is provided.

        Returns:
            tuple: (db_path, db_embed)
        """
        storage_settings = self.config.data['settings']['storage']
        db_path_setting = storage_settings['options'].get('persist_directory', None)
        selected_embed = storage_settings['embedding'].get('selected', None)
        db_embed = storage_settings['embedding_library'].get(selected_embed, None)
        personas_enabled = self.config.data['settings']['system']['persona'].get('enabled', False)
        if not db_path_setting:
            raise ValueError("ChromaStorage: persist_directory must be set in the settings YAML.")
        if self.storage_id:
            db_path = str(self.config.project_root / db_path_setting / self.storage_id)
        elif self.cog_context and personas_enabled and self.persona_context:
            db_path = str(self.config.project_root / db_path_setting / self.cog_context / self.persona_context)
        elif self.cog_context and not personas_enabled:
            db_path = str(self.config.project_root / db_path_setting / self.cog_context)
        else:
            raise ValueError("ChromaStorage: Cannot resolve db_path. Provide a storage_id or cog_context (with persona if personas are enabled).")
        return db_path, db_embed

    def reset_storage(self):
        """
        Resets the entire storage, removing all collections and their data.

        This method should be used with caution as it will permanently delete all data within the storage.
        """

        self.client.reset()

    def return_embedding(self, text_to_embed: str):
        """
        Generates an embedding for the given text using the configured embedding function.

        Parameters:
            text_to_embed (str): The text to generate an embedding for.

        Returns:
            list: A list containing the generated embedding vector for the given text.
        """
        return self.embedding([text_to_embed])

    ##########################################################
    # Section 5: Inner Methods
    ##########################################################

    def _calculate_num_results(self, num_results, collection_name):
        self.select_collection(collection_name)
        max_result_count = self.collection.count()
        return max_result_count if num_results == 0 else min(num_results, max_result_count)

    def _prepare_query_params(self, query, filter_condition, include, embeddings, num_results, collection_name):
        if not query and not embeddings:
            logger.log(f"Error: No query nor embeddings were provided!  ", 'error')
            return {}

        query_params = {"n_results": self._calculate_num_results(num_results, collection_name)}
        if query_params["n_results"] <= 0:
            logger.log(f"No Results Found in '{collection_name}' collection!", 'info')
            return {}

        query_params["include"] = include if include else ["documents", "metadatas", "distances"]

        if filter_condition:
            query_params["where"] = filter_condition

        if query:
            query_params["query_texts"] = [query] if isinstance(query, str) else query

        if embeddings:
            query_params["query_embeddings"] = embeddings

        return query_params

    ##########################################################
    # Section 6: DB Methods
    ##########################################################

    def collection_list(self):
        """
        Lists all collections currently in the storage.

        Returns:
            list: A list of collection names.
        """
        return self.client.list_collections()

    def select_collection(self, collection_name: str):
        """
        Selects (or creates if not existent) a collection within the storage by name.

        Parameters:
            collection_name (str): The name of the collection to select or create.

        Raises:
            ValueError: If there's an error in getting or creating the collection.
        """
        try:
            collection_name = validate_collection_name(collection_name)
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

    ##########################################################
    # Section 7: Storage for Memory
    ##########################################################

    def save_to_storage(self, collection_name: str, data: list, ids: Optional[list],
                        metadata: Optional[list[dict]]):
        """
        Saves data to memory, creating or updating documents in a specified collection.

        Parameters:
            collection_name (str): The name of the collection to save to. Will be created if it doesn't exist.
            data (list): The documents to be saved. Can be a single document as a string or a list
             of documents. If a single string is provided, it is converted into a list with one element.
            ids (list): The IDs corresponding to the documents. If not provided, IDs will be generated automatically.
            metadata (list[dict], optional): A list of dictionaries, each representing associated metadata for
                the corresponding document in `data`. If not provided, empty dictionaries are used for each document.

        Raises:
            ValueError: If the lengths of `data`, `ids`, and `metadata` do not match, or if other errors occur
            during the save operation.
        """
        try:
            data = [data] if isinstance(data, str) else data
            ids, metadata = generate_defaults(data, ids, metadata)
            validate_inputs(data, ids, metadata)
            apply_timestamps(metadata, self.config.data)

            self.select_collection(collection_name)
            self.collection.upsert(
                documents=data,
                metadatas=metadata,
                ids=ids
            )
        except Exception as e:
            raise ValueError(f"[ChromaStorage][save_to_storage] Error saving to storage. Error: {e}\n\nData:\n{data}")

    def query_storage(self, collection_name: str, query: Optional[Union[str, list]] = None,
                      filter_condition: Optional[dict] = None, include: Optional[list] = None,
                      embeddings: Optional[list] = None, num_results: int = 1):
        """
        Queries storage for documents matching a query within a specified collection.

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
            params = {
                'query': query,
                'filter_condition': filter_condition,
                'include': include,
                'embeddings': embeddings,
                'num_results': num_results,
                'collection_name': collection_name
            }
            query_params = self._prepare_query_params(**params)

            result = {}
            if query_params:
                self.select_collection(collection_name)
                unformatted_result = self.collection.query(**query_params)

                if unformatted_result:
                    for key, value in unformatted_result.items():
                        if value:
                            result[key] = value[0]

            return result

        except Exception as e:
            logger.log(f"[query_memory] Error querying storage: {e}", 'error')
            return None

    def delete_from_storage(self, collection_name, ids):
        if ids and not isinstance(ids, list):
            ids = [ids]

        self.select_collection(collection_name)
        self.collection.delete(ids=ids)

    ##########################################################
    # Section 7: Advanced
    ##########################################################

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

            results = self.query_storage(collection_name=collection_name, embeddings=query_emb,
                                        include=["documents", "metadatas", "distances"],
                                        num_results=num_results)

            # We compare against the first result's embedding and `distance.cosine` returns
            # a similarity measure. May need to adjust the logic based on the actual behavior
            # of `distance.cosine`.
            # dist = distance.cosine(query_emb[0], results['embeddings'][0])
            if results:
                results.pop('included')
                filtered_data = {
                    key: [value for value, dist in zip(results[key], results['distances']) if float(dist) < threshold]
                    for key in results
                }
                if filtered_data['documents']:
                    return filtered_data

                logger.log('[search_storage_by_threshold] No documents found that meet the threshold.', 'info')
                return {}

            logger.log('Search by Threshold: No documents found.', 'info')
            return {}

        except Exception as e:
            logger.log(f"[search_storage_by_threshold] Error searching storage by threshold: {e}", 'error')
            return {'failed': f"Error searching storage by threshold: {e}"}

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
            results = self.collection.get()

            # Extract the metadata values and document IDs
            metadata_values = [entry[metadata_tag] for entry in results["metadatas"]]
            document_ids = results["ids"]

            # Check if all metadata values are numeric (int or float)
            if not all(isinstance(value, (int, float)) for value in metadata_values):
                logger.log(f"[search_metadata_min_max] Error: The metadata tag '{metadata_tag}' contains non-numeric values.", 'error')
                return None

            if metadata_values:
                if min_max == "min":
                    target_index = metadata_values.index(min(metadata_values))
                else:
                    try:
                        target_index = metadata_values.index(max(metadata_values))
                    except:
                        logger.log(f"[search_metadata_min_max] Error: The metadata tag '{metadata_tag}' is empty or does not exist. Returning 0.", 'error')
                        target_index = 0
            else:
                target_index = 0

            try:
                # Retrieve the full entry with the highest metadata value
                target_entry = self.collection.get(ids=[document_ids[target_index]])

                max_metadata = {
                    "ids": target_entry["ids"][0],
                    "target": target_entry["metadatas"][0][metadata_tag],
                    "metadata": target_entry["metadatas"][0],
                    "document": target_entry["documents"][0],
                }

                logger.log(
                    f"[search_metadata_min_max] Found the following record by max value of {metadata_tag} metadata tag:\n{max_metadata}",
                    'debug'
                )
                return max_metadata
            except Exception as e:
                logger.log(f"[search_metadata_min_max] Error finding max metadata: {e}\nCollection: {collection_name}\nTarget Metadata: {metadata_tag}", 'error')
                return None

        except (KeyError, ValueError, IndexError) as e:
            logger.log(f"[search_metadata_min_max] Error finding max metadata: {e}\nCollection: {collection_name}\nTarget Metadata: {metadata_tag}", 'error')
            return None

    def rerank_results(self, query_results: dict, query: str, temp_collection_name: str, num_results: int = None):
        """
        Reranks the query results using a temporary collection.

        Args:
            query_results (dict): A dictionary containing the initial query results.
                Expected keys: 'documents', 'ids', 'metadatas', 'query'
            query (str): Query string to rerank against.
            temp_collection_name (str): The name of the temporary collection to use for reranking.
            num_results (int, optional): The number of results to return after reranking.
                If not provided or greater than the number of documents, all documents will be returned.

        Returns:
            dict: The reranked results, or None if an error occurs.
        """
        try:
            # Check if query_results contains the expected keys
            expected_keys = ['documents', 'ids', 'metadatas']
            if not all(key in query_results for key in expected_keys):
                raise KeyError(f"Missing expected keys in query_results. Expected: {expected_keys}")

            # Check if documents is empty
            if not query_results['documents']:
                logger.log("[rerank_results] No documents found in query_results. Skipping reranking.", 'warning')
                return query_results

            # Save the query results to a temporary collection
            self.save_to_storage(
                collection_name=temp_collection_name,
                data=query_results['documents'],
                ids=query_results['ids'],
                metadata=query_results['metadatas']
            )

            # Determine the number of results to return
            if num_results is None or num_results > len(query_results['documents']):
                num_results = len(query_results['documents'])

            # Perform reranking on the temporary collection
            reranked_results = self.query_storage(
                collection_name=temp_collection_name,
                query=query,
                num_results=num_results
            )
            count=self.count_collection(temp_collection_name)
            print(f"Count: {count}")

            # Delete the temporary collection
            self.delete_collection(temp_collection_name)

            return reranked_results
        except KeyError as e:
            logger.log(f"[rerank_results] KeyError occurred while reranking results: {e}", 'error')
            return None
        except Exception as e:
            logger.log(f"[rerank_results] Unexpected error occurred while reranking results: {e}", 'error')
            return None

    @staticmethod
    def combine_query_results(*query_results):
        """
        Combine the query results from multiple queries and remove duplicates.

        Args:
            *query_results: Variable number of query result dictionaries.

        Returns:
            dict: Combined query results with duplicates removed and new IDs assigned.
        """
        combined_results = {
            'documents': [],
            'ids': [],
            'metadatas': []
        }

        for query_result in query_results:
            combined_results['documents'].extend(query_result['documents'])
            combined_results['ids'].extend(query_result['ids'])
            combined_results['metadatas'].extend(query_result['metadatas'])

        # Remove duplicates based on the 'documents' field
        unique_results = {
            'documents': [],
            'ids': [],
            'metadatas': []
        }
        seen_documents = set()

        for i in range(len(combined_results['documents'])):
            document = combined_results['documents'][i]
            if document not in seen_documents:
                seen_documents.add(document)
                unique_results['documents'].append(document)
                unique_results['ids'].append(str(len(unique_results['ids']) + 1))  # Assign new ID
                unique_results['metadatas'].append(combined_results['metadatas'][i])

        return unique_results

    def combine_and_rerank(self, query_results: list, rerank_query, num_results=5):
        """
        Combine multiple query results, rerank them based on a new query, and return the top results.

        This function takes multiple query results, combines them, and then reranks the combined
        results based on a new query. It's useful for refining search results across multiple
        collections or queries.

        Args:
            query_results (list): A list of query result dictionaries, each containing 'ids',
                                'embeddings', 'documents', and 'metadatas'.
            rerank_query (str): The query string used for reranking the combined results.
            num_results (int, optional): The number of top results to return after reranking.
                                        Defaults to 5.

        Returns:
            dict: A dictionary containing the reranked results, including 'ids', 'embeddings',
                'documents', and 'metadatas' for the top results.

        Raises:
            ValueError: If query_results is empty or if reranking fails.

        Example:
            query_results = [results1, results2, results3]
            rerank_query = "specific query that can be the same or a new query"
            reranked = query_and_rerank(query_results, rerank_query, num_results=3)
        """

        # Combine all query results
        combined_query_results = self.combine_query_results(*query_results)

        reranked_results = self.rerank_results(
            query_results=combined_query_results,
            query=rerank_query,
            temp_collection_name="temp_reranking_collection",
            num_results=num_results
        )

        return reranked_results

    @classmethod
    def get_or_create(cls, cog_name: Optional[str] = None, persona: Optional[str] = None, storage_id: Optional[str] = None):
        """
        Retrieve a shared ChromaStorage instance for the given cog_name/persona or a custom storage_id.
        - If storage_id is provided, it is used as the registry key and for pathing.
        - If personas are enabled, uses cog:persona as key and path.
        - If personas are disabled, uses cog as key and path.
        - Raises ValueError if insufficient context is provided.

        Args:
            cog_name (Optional[str]): The cog name for context (used in default key/path).
            persona (Optional[str]): The persona for context (used in default key/path).
            storage_id (Optional[str]): Optional custom key for advanced use cases.

        Returns:
            ChromaStorage: The shared instance for the given key.
        """
        config = Config()
        personas_enabled = config.data['settings']['system']['persona'].get('enabled', False)
        if storage_id:
            key = storage_id
        elif cog_name and personas_enabled and persona:
            key = f"{cog_name}:{persona}"
        elif cog_name and not personas_enabled:
            key = cog_name
        else:
            raise ValueError("ChromaStorage.get_or_create requires either a storage_id or cog_name (with persona if personas are enabled). Provide a unique storage_id for standalone/agent mode or when context is ambiguous.")
        with cls._registry_lock:
            if key not in cls._registry:
                cls._registry[key] = cls(cog_context=cog_name, persona_context=persona, storage_id=storage_id)
            return cls._registry[key]

    @classmethod
    def clear_registry(cls):
        """
        Clear the ChromaStorage registry. Useful for test isolation or resetting state.
        """
        with cls._registry_lock:
            cls._registry.clear()

    def describe_instance(self):
        """
        Returns a dictionary describing the resolved key, path, and context for this instance.
        Useful for debugging and testing.
        """
        db_path, db_embed = self.chromadb_settings()
        return {
            'resolved_key': getattr(self, '_resolved_key', None),
            'resolved_path_mode': getattr(self, '_resolved_path_mode', None),
            'db_path': db_path,
            'cog_context': self.cog_context,
            'persona_context': self.persona_context,
            'storage_id': self.storage_id,
            'personas_enabled': self.config.data['settings']['system']['persona'].get('enabled', False),
        }

