# src/agentforge/storage/Memory.py
import json
from typing import Any, Dict, Optional, Union, List
from .chroma_storage import ChromaStorage
from agentforge.utils.parsing_processor import ParsingProcessor
from agentforge.utils.logger import Logger


class Memory:
    """
    Base Memory class for managing memory operations and storage contexts.
    Handles CRUD operations for memory storage, partitioned by persona or cog_name.
    Designed for extensibility and clarity.
    """

    def __init__(self, cog_name: str, persona: Optional[str] = None, collection_id: Optional[str] = None, logger_name: Optional[str] = None):
        """
        Initialize a Memory instance for a specific cog and persona.

        Args:
            cog_name (str): Name of the cog to which this memory belongs.
            persona (Optional[str]): Optional persona name for further partitioning.
            collection_id (Optional[str]): Optional identifier for the collection. 
            logger_name (Optional[str]): Optional name for the logger.
        """
        self._initialize_attributes(cog_name, persona, collection_id, logger_name)
        self._resolve_storage()
        self._resolve_collection_name()
        self.logger.debug(f"Initialized Memory for cog='{self.cog_name}', persona='{self.persona}', collection='{self.collection_name}'")

    # -----------------------------------------------------------------
    # Initialization Helpers
    # -----------------------------------------------------------------
    def _initialize_attributes(self, cog_name: str, persona: Optional[str], collection_id: Optional[str], logger_name: Optional[str]) -> None:
        logger_name = logger_name or f"Memory[{cog_name}]"
        self.logger = Logger(logger_name, "memory")
        self.store: Dict[str, Any] = {}
        self.cog_name = cog_name
        self.persona = persona
        self.collection_id = collection_id
        self.storage = None
        self.collection_name = None

    def _resolve_storage(self) -> None:
        """Resolve and assign the ChromaStorage instance."""
        resolved_storage_id = self._resolve_storage_id()
        self.storage = ChromaStorage.get_or_create(storage_id=resolved_storage_id)
        self.logger.debug(f"Resolved storage with id='{resolved_storage_id}'")

    def _resolve_collection_name(self) -> None:
        """Resolve and assign the collection name."""
        self._build_collection_name()
        self.logger.debug(f"Resolved collection name='{self.collection_name}'")

    # -----------------------------------------------------------------
    # Public Interface Methods
    # -----------------------------------------------------------------

    # -----------------------------------------------------------------
    # Query Methods
    # -----------------------------------------------------------------
    def query_memory(self, query_keys: Optional[List[str]], _ctx: dict, _state: dict, num_results: int = 5) -> None:
        """
        Query memory storage for relevant entries based on provided context and state.
        This is a template method that delegates to extensible steps for customization.

        Args:
            query_keys (Optional[List[str]]): Keys to construct the query from context/state.
            _ctx (dict): External context data.
            _state (dict): Internal state data.
            num_results (int): Number of results to retrieve.
        """
        self._prepare_query(query_keys, _ctx, _state, num_results)
        queries = self._build_queries(query_keys, _ctx, _state)
        if not queries:
            self.logger.debug("No queries constructed; skipping query.")
            return
        raw = self._execute_query(queries, num_results)
        self.store = self._process_query_results(raw)

    def _prepare_query(self, query_keys, _ctx, _state, num_results):
        """
        Hook for pre-query logic, validation, or setup. Override in subclasses if needed.
        """
        self.store = {}

    def _build_queries(self, query_keys, _ctx, _state):
        """
        Default implementation for building queries from keys/context/state.
        Returns a list or string.
        Override for custom query logic.
        """
        return self._build_queries_from_keys_and_context(query_keys, _ctx, _state)

    def _build_queries_from_keys_and_context(self, query_keys, _ctx, _state):
        """
        Internal helper for constructing queries from keys/context/state.
        This method can be overridden for custom query-building logic.
        """
        if query_keys:
            if isinstance(query_keys, str) or isinstance(query_keys, list):
                return query_keys
        query_values = []
        if _ctx:
            query_values.extend([str(v) for v in _ctx.values() if v is not None])
        if _state:
            query_values.extend([str(v) for v in _state.values() if v is not None])
        return query_values

    def _execute_query(self, queries, num_results):
        """
        Execute the query against storage. Override for custom storage/query logic.
        """
        return self.storage.query_storage(
            collection_name=self.collection_name,
            query=queries,
            num_results=num_results
        )

    # -----------------------------------------------------------------
    # Update Methods
    # -----------------------------------------------------------------
    
    def update_memory(self, update_keys: Optional[List[str]], _ctx: dict, _state: dict, 
                     ids: Optional[Union[str, list[str]]] = None,
                     metadata: Optional[list[dict]] = None) -> None:
        """
        Update memory with new data using update_keys to extract from context/state.
        This is a template method that delegates to extensible steps for customization.

        Args:
            update_keys (Optional[List[str]]): Keys to extract for update, or None to use all data.
            _ctx (dict): External context data.
            _state (dict): Internal state data.
            ids (Union[str, list[str]], optional): The IDs for the documents.
            metadata (list[dict], optional): Custom metadata for the documents (overrides generated metadata).
        """
        processed_data, metadata_list = self._prepare_update_data(update_keys, _ctx, _state, custom_metadata=metadata)
        if not processed_data:
            self.logger.debug("No data to update; skipping storage update.")
            return
        self._save_update(processed_data, ids, metadata_list)

    def _process_query_results(self, raw):
        """
        Process and format the raw query results. Override for custom result handling.
        """
        store = {}
        if raw:
            store.update({"raw": raw, "readable": self.format_memory_results(raw)})
            self.logger.debug(f"Query returned {len(raw.get('ids', []))} results.")
        return store

    def _save_update(self, processed_data, ids, metadata_list):
        """
        Save the processed data and metadata to storage. Override for custom storage logic.
        """
        self.storage.save_to_storage(
            collection_name=self.collection_name,
            data=processed_data,
            ids=ids,
            metadata=metadata_list
        )
        self.logger.debug(f"Updated memory with {len(processed_data)} entries.")

    # -----------------------------------------------------------------
    # Delete Methods
    # -----------------------------------------------------------------
    def delete(self, ids: Union[str, list[str]]) -> None:
        """
        Delete the memory entry or entries with the given key(s).
        This is a template method that delegates to extensible steps for customization.

        Args:
            ids (Union[str, list[str]]): The unique identifier(s) for the memory entries to delete.
        """
        self._prepare_delete(ids)
        try:
            self._execute_delete(ids)
            self._post_delete(ids)
        except Exception as e:
            self._handle_delete_error(e, ids)

    def _prepare_delete(self, ids):
        """
        Hook for pre-delete logic, validation, or setup. Override in subclasses if needed.
        """
        pass

    def _execute_delete(self, ids):
        """
        Execute the actual deletion from storage. Override for custom storage logic.
        """
        self.storage.delete_from_storage(collection_name=self.collection_name, ids=ids)

    def _post_delete(self, ids):
        """
        Hook for post-delete logic, logging, or cleanup. Override in subclasses if needed.
        """
        self.logger.debug(f"Deleted memory entries with ids={ids}.")

    def _handle_delete_error(self, error, ids):
        """
        Handle errors during deletion. Override for custom error handling.
        """
        self.logger.error(f"Memory delete failed: {error}")
        raise

    # -----------------------------------------------------------------
    # Wipe Methods
    # -----------------------------------------------------------------
    
    def wipe_memory(self) -> None:
        """
        Wipe all memory, removing all collections and their data.
        Use with caution: this will permanently delete all data within the storage.
        This is a template method that delegates to extensible steps for customization.
        """
        self._prepare_wipe()
        try:
            self._execute_wipe()
            self._post_wipe()
        except Exception as e:
            self._handle_wipe_error(e)

    def _prepare_wipe(self):
        """
        Hook for pre-wipe logic, validation, or setup. Override in subclasses if needed.
        """
        pass

    def _execute_wipe(self):
        """
        Execute the actual wipe/reset of storage. Override for custom storage logic.
        """
        self.storage.reset_storage()

    def _post_wipe(self):
        """
        Hook for post-wipe logic, logging, or cleanup. Override in subclasses if needed.
        """
        self.logger.debug("Wiped all memory from storage.")

    def _handle_wipe_error(self, error):
        """
        Handle errors during wipe. Override for custom error handling.
        """
        self.logger.error(f"Memory wipe failed: {error}")
        raise

    # -----------------------------------------------------------------
    # Extension Points (for subclassing)
    # -----------------------------------------------------------------
    def _build_collection_name(self) -> str:
        """
        Build a collection name. By default, uses the provided collection_id.
        Subclasses can override this method to provide custom collection naming.
        Returns:
            str: The collection name to use for storage.
        """
        self.collection_name = self.collection_id if self.collection_id else f"{self.cog_name}_{self.persona}"

    # TODO: Review method and consider making it optional, defaulting to PromptProcessor for automatic formatting.
    # This is a method was made to turn raw results into a readable string.
    # While this is meant for extensibility, the current format is arbitrary and may not be ideal as a default.

    @staticmethod
    def format_memory_results(raw_results: dict) -> str:
        """
        Format raw query results into a human-readable string.
        Subclasses can override this method to customize formatting.

        Args:
            raw_results (dict): The raw result from storage query.
        Returns:
            str: Human-readable formatted string of memory results.
        """
        ids = raw_results.get("ids", [])
        documents = raw_results.get("documents", [])
        metadatas = raw_results.get("metadatas", [])

        records = [
            {"id": id_, "content": d, "meta": m}
            for id_, d, m in list(zip(ids, documents, metadatas))
        ]

        def sort_key(rec):
            meta = rec["meta"]
            # Prefer iso_timestamp if present, else fallback to id
            # If both missing, fallback to 0
            ts = meta.get("iso_timestamp")
            if ts is not None:
                return ts
            return meta.get("id", 0)

        records = sorted(records, key=sort_key)

        history = []

        for rec in records:
            current_record = {}
            rec_id = rec["id"]
            
            current_record[rec_id] = [
                f"{rec['content']}\n",
                rec["meta"]
            ]

            history.append(current_record)

        return records
    

    # -----------------------------------------------------------------
    # Internal Helper Methods
    # -----------------------------------------------------------------
    def _resolve_storage_id(self) -> str:
        """
        Determine the storage_id based on persona or cog_name context.
        Returns:
            str: A normalized storage_id for ChromaStorage.
        """
        fallback_storage_id = "fallback_storage"
        if self.persona:
            storage_id = self.persona
        elif self.cog_name:
            storage_id = self.cog_name
        else:
            storage_id = fallback_storage_id
        return str(storage_id).strip() or fallback_storage_id

    def _build_merged_context(self, _ctx: dict, _state: dict) -> dict:
        """
        Build a merged context from context and state.
        Returns:
            dict: Merged context and state.
        """
        _ctx = _ctx or {}
        _state = _state or {}
        return {**_state, **_ctx}

    def _extract_keys(self, key_list: Optional[List[str]], _ctx: dict, _state: dict) -> dict:
        """
        Extract values for the given keys from context (external) first, then state (internal).
        Supports dot-notated keys for nested dict access.
        If key_list is empty or None, returns a merged dict of context and state.
        Args:
            key_list: List of keys to extract
            _ctx: External context data
            _state: Internal state data
        Returns:
            Dict of extracted key-value pairs
        Raises:
            ValueError: If a key is not found in either context or state
        """
        if not key_list:
            return self._build_merged_context(_ctx, _state)
        result = {}
        for key in key_list:
            value = ParsingProcessor.get_dot_notated(_ctx, key)
            if value is not None:
                result[key] = value
                continue
            value = ParsingProcessor.get_dot_notated(_state, key)
            if value is not None:
                result[key] = value
                continue
            self.logger.error(f"Key '{key}' not found in context or state.")
            raise ValueError(f"Key '{key}' not found in context or state.")
        return result

    def _extract_data_for_update(self, update_keys: Optional[List[str]], _ctx: dict, _state: dict) -> dict:
        """
        Extract data from context/state based on provided update_keys.
        Returns:
            dict: Data to update.
        """
        if update_keys:
            return self._extract_keys(update_keys, _ctx, _state)
        return self._build_merged_context(_ctx, _state)

    def _generate_metadata(self, flattened_data: dict, _ctx: dict, _state: dict) -> dict:
        """
        Generate metadata from flattened data and merged context/state.
        Returns:
            dict: Metadata dictionary.
        """
        metadata_dict = flattened_data.copy() if isinstance(flattened_data, dict) else {}
        merged_context = self._build_merged_context(_ctx, _state)
        if merged_context:
            context_metadata = {
                f"context_{k}": v for k, v in ParsingProcessor.flatten_dict(merged_context).items()
            }
            metadata_dict.update(context_metadata)
        return metadata_dict

    def _prepare_update_data(self, update_keys: Optional[List[str]], _ctx: dict, _state: dict, custom_metadata: Optional[list[dict]] = None) -> tuple:
        """
        Prepare data and metadata for storage from update_keys and context/state.
        If custom_metadata is provided, use it for all items.
        Args:
            update_keys: List of keys to extract for update, or None to use all data
            _ctx: External context data
            _state: Internal state data
            custom_metadata: Optional custom metadata to use for all items
        Returns:
            tuple: (processed_data, metadata_list)
        """
        data = self._extract_data_for_update(update_keys, _ctx, _state)
        if not data:
            return [], []
        flattened_data = ParsingProcessor.flatten_dict(data)
        processed_data = [str(value) for value in flattened_data.values()]
        if custom_metadata is not None:
            return processed_data, custom_metadata
        metadata_dict = self._generate_metadata(flattened_data, _ctx, _state)
        metadata_list = [metadata_dict.copy() for _ in processed_data]
        return processed_data, metadata_list
