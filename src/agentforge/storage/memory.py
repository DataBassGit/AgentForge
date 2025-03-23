# src/agentforge/storage/Memory.py

from typing import Any, Dict, Optional, Union
from .chroma_storage import ChromaStorage


class Memory:
    """
    Base Memory class for managing memory operations with contextual awareness.

    The Memory class partitions memory by cog and optionally by persona.
    It delegates CRUD operations to the ChromaStorage instance, ensuring that
    update acts as create-if-not-exists.
    """

    def __init__(self, cog_name: str, persona: Optional[str] = None):
        """
        Initializes a Memory instance for a specific cog and persona.

        Args:
            cog_name (str): Name of the cog to which this memory belongs.
            persona (Optional[str]): Optional persona name for further partitioning.
        """
        self.store = {}
        self.cog_name = cog_name
        self.persona = persona
        # Build a collection name based on cog and persona.
        self.collection_name = self._build_collection_name()
        # Initialize the underlying storage using our ChromaStorage wrapper.
        self.storage = ChromaStorage(self.collection_name)

    def _build_collection_name(self) -> str:
        """
        Builds a collection name from the cog name and persona.
        """
        if self.persona:
            return f"{self.cog_name}_{self.persona}"
        return self.cog_name

    def query_memory(self, query_text: str | list[str], num_results: int = 5) -> Optional[Dict[str, Any]]:
        """
        Queries memory for items similar to query_text.

        Args:
            query_text (str): The text to search for.
            num_results (int): The number of results to return.

        Returns:
            Optional[Dict[str, Any]]: The query results or None if not found.
        """
        data = self.storage.query_storage(collection_name=self.collection_name,
                                          query = query_text, num_results= num_results)

        if data:
            self.store.update(data)

    def update_memory(self, data: Any, ids: Optional[str | list[str]] = None, metadata: Optional[list[dict]] = None) -> None:
        """
        Updates the memory entry with the specified key. Creates the entry if it doesn't exist.

        Args:
            ids (str): The unique identifier for the memory entry.
            data (Any): The data to store.
            metadata (Optional[list[dict]]): Optional metadata.
        """
        self.storage.save_to_storage(collection_name=self.collection_name, data=data, ids=ids, metadata=metadata)

    def delete(self, ids: str | list[str]) -> None:
        """
        Deletes the memory entry with the given key.

        Args:
            ids (str): The unique identifier for the memory entry to delete.
        """
        self.storage.delete_from_stroage(collection_name=self.collection_name, ids=ids)

    def wipe_memory(self):
        """
        Wipes all memory, removing all collections and their data.

        This method should be used with caution as it will permanently delete all data within the storage.
        """
        self.storage.reset_storage()
