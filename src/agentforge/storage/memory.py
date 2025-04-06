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
    Base Memory class for managing memory operations with contextual awareness.

    The Memory class partitions memory by cog and optionally by persona.
    It delegates CRUD operations to the ChromaStorage instance, ensuring that
    update acts as create-if-not-exists.
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
        # Build or use provided collection name
        self.collection_name = collection_id or self._build_collection_name()
        # Initialize the underlying storage using our ChromaStorage wrapper.
        # Pass cog and persona as context for proper namespace pathing
        self.storage = ChromaStorage(self.collection_name, cog_context=self.cog_name, persona_context=self.persona)

    def _build_collection_name(self) -> str:
        """
        Builds a collection name. By default, uses "default" as the collection name.
        This method can be overridden by subclasses to provide custom collection naming.
        
        Returns:
            str: The collection name to use for storage
        """
        return "default"

    def query_memory(self, query_text: Union[str, list[str]], num_results: int = 5) -> Optional[Dict[str, Any]]:
        """
        Queries memory for items similar to query_text.

        Args:
            query_text (Union[str, list[str]]): The text or texts to search for.
            num_results (int): The number of results to return.

        Returns:
            Optional[Dict[str, Any]]: The query results or None if not found.
        """
        data = self.storage.query_storage(
            collection_name=self.collection_name,
            query=query_text, 
            num_results=num_results
        )

        if data:
            self.store.update(data)
            return data
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
