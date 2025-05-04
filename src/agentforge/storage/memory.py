# src/agentforge/storage/Memory.py
import json
from typing import Any, Dict, Optional, Union
from .chroma_storage import ChromaStorage


def flatten_dict(d: dict, parent_key: str = '', sep: str = '.') -> dict:
    """Recursively flattens a nested dictionary using a given separator."""
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items


class Memory:
    """
    Base Memory class for managing memory operations and storage contexts.

    Memory uses a storage_id derived from persona or cog_name to partition storage.
    It delegates CRUD operations to a ChromaStorage instance identified by storage_id.
    """

    def __init__(self, cog_name: str, persona: Optional[str] = None, collection_id: Optional[str] = None):
        """
        Initializes a Memory instance for a specific cog and persona.

        Args:
            cog_name (str): Name of the cog to which this memory belongs.
            persona (Optional[str]): Optional persona name for further partitioning.
            collection_id (Optional[str]): Optional identifier for the collection. 
                                          If not provided, uses a derived name.
        """
        self.store = {}
        self.cog_name = cog_name
        self.persona = persona
        self.collection_id = collection_id

        # Resolve and normalize storage identifier
        resolved_storage_id = self._resolve_storage_id()

        # Retrieve a shared ChromaStorage instance for the resolved storage_id
        self.storage = ChromaStorage.get_or_create(storage_id=resolved_storage_id)

        # Build or use provided collection name
        self.collection_name = self._build_collection_name()

    def _build_collection_name(self) -> str:
        """
        Builds a collection name. By default, uses "general_memory" as the collection name.
        This method can be overridden by subclasses to provide custom collection naming.
        
        Returns:
            str: The collection name to use for storage
        """
        return self.collection_id

    def _resolve_storage_id(self) -> str:
        """
        Determine the storage_id based on persona or cog_name context.

        Returns:
            str: A normalized storage_id for ChromaStorage.
        """
        fallback_storage_id = "fallback_storage"

        if self.persona: # self.persona is None if personas are disabled
            storage_id = self.persona
        elif self.cog_name:
            storage_id = self.cog_name
        else:
            # Fallback storage identifier when no context is available
            storage_id = fallback_storage_id
        # Normalize and return
        return str(storage_id).strip() or fallback_storage_id

    def format_memory_results(self, raw_results: dict) -> str:
        """
        Formats raw Chroma query results into a human-readable string.

        Each memory entry is presented as a block headed by '--- Memory <n>: <id>',
        followed by the document content and an indented YAML-style metadata dump.
        Only metadata keys present for each record are included. Subclasses can override
        this method to customize formatting.

        Args:
            raw_results (dict): The raw result from Chroma query_storage.

        Returns:
            str: Human-readable formatted string of memory results.
        """
        ids = raw_results.get("ids", [])
        documents = raw_results.get("documents", [])
        metadatas = raw_results.get("metadatas", [])
        # Attempt to order by unix_timestamp or iso_timestamp if present
        entries = []
        for idx, (id_, doc, meta) in enumerate(zip(ids, documents, metadatas)):
            # Try to get a sortable timestamp
            ts = None
            if isinstance(meta, dict):
                ts = meta.get("unix_timestamp")
                if ts is None and "iso_timestamp" in meta:
                    ts = meta["iso_timestamp"]
            entries.append((idx, id_, doc, meta, ts))
        # Sort by timestamp if available, else by original order
        def sort_key(entry):
            ts = entry[4]
            if ts is None:
                return float('inf')
            try:
                return float(ts)
            except Exception:
                return float('inf')
        entries.sort(key=sort_key)
        blocks = []
        for new_idx, (idx, id_, doc, meta, ts) in enumerate(entries):
            block = f"--- Memory {new_idx}: {id_}\n"
            block += f"content: {doc}\n"
            block += "metadata:\n"
            for k, v in meta.items():
                block += f"  {k}: {v}\n"
            blocks.append(block.rstrip())
        return "\n\n".join(blocks)

    def query_memory(self, query_text: Union[str, list[str]], num_results: int = 5) -> Optional[dict]:
        """
        Queries memory for items similar to query_text and returns both raw and formatted results.

        Args:
            query_text (Union[str, list[str]]): The text or texts to search for.
            num_results (int): The number of results to return.

        Returns:
            Optional[dict]: Dict with 'raw' (original chroma result) and 'readable' (formatted string), or None if not found.
        """
        raw = self.storage.query_storage(
            collection_name=self.collection_name,
            query=query_text, 
            num_results=num_results
        )

        if raw:
            self.store.update({"raw": raw, "readable": self.format_memory_results(raw)})
            return {"raw": raw, "readable": self.format_memory_results(raw)}
        return None

    @staticmethod
    def _prepare_memory_data(data: dict, context: Optional[dict] = None) -> tuple:
        """
        Prepares data for storage by processing and creating appropriate metadata.
        
        Args:
            data (dict): The primary data to store
            context (dict, optional): Additional context to include in metadata
            
        Returns:
            tuple: (processed_data, metadata_list)
        """
        # If the data is a dictionary, flatten it for storage
        flattened_data = flatten_dict(data) if isinstance(data, dict) else data
        
        # Convert values to strings for storage
        processed_data = [str(value) for value in flattened_data.values()]
        
        # Create metadata from the flattened data and additional context
        metadata_dict = flattened_data.copy()
        if context:
            # Add context as additional metadata with a prefix to avoid collisions
            context_metadata = {"context_" + k: v for k, v in flatten_dict(context).items()}
            metadata_dict.update(context_metadata)
        
        # Create a list of the same metadata for each data item
        metadata_list = [metadata_dict.copy() for _ in processed_data]
        
        return processed_data, metadata_list

    def update_memory(self, data: dict, 
                     context: Optional[dict] = None,
                     ids: Optional[Union[str, list[str]]] = None,
                     metadata: Optional[list[dict]] = None) -> None:
        """
        Updates memory with new data, using contexts for metadata if provided.

        Args:
            data (dict): Dictionary containing the data to be stored.
            context (dict, optional): Dictionary containing the cog's external and internal context.
            ids (Union[str, list[str]], optional): The IDs for the documents.
            metadata (list[dict], optional): Custom metadata for the documents (overrides generated metadata).
        """
        # If custom metadata is not provided, generate it from data and context
        if metadata is None:
            processed_data, generated_metadata = self._prepare_memory_data(data, context)
            metadata = generated_metadata
        else:
            # If metadata is provided but data is a dictionary, flatten it
            processed_data = [str(value) for value in flatten_dict(data).values()] if isinstance(data, dict) else data
            
        # Save to storage with the prepared data
        self.storage.save_to_storage(
            collection_name=self.collection_name, 
            data=processed_data, 
            ids=ids, 
            metadata=metadata
        )

    def delete(self, ids: Union[str, list[str]]) -> None:
        """
        Deletes the memory entry with the given key(s).

        Args:
            ids (Union[str, list[str]]): The unique identifier(s) for the memory entries to delete.
        """
        self.storage.delete_from_storage(collection_name=self.collection_name, ids=ids)

    def wipe_memory(self):
        """
        Wipes all memory, removing all collections and their data.

        This method should be used with caution as it will permanently delete all data within the storage.
        """
        self.storage.reset_storage()
