# src/agentforge/storage/Memory.py

from typing import Any, Dict, Optional
from chroma_storage import ChromaStorage


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

    def query(self, query_text: str, num_results: int = 1) -> Optional[Dict[str, Any]]:
        """
        Queries memory for items similar to query_text.

        Args:
            query_text (str): The text to search for.
            num_results (int): The number of results to return.

        Returns:
            Optional[Dict[str, Any]]: The query results or None if not found.
        """
        return self.storage.query_memory(collection_name=self.collection_name,
                                         query=query_text,
                                         num_results=num_results)

    def update(self, key: str, data: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Updates the memory entry with the specified key. Creates the entry if it doesn't exist.

        Args:
            key (str): The unique identifier for the memory entry.
            data (Any): The data to store.
            metadata (Optional[Dict[str, Any]]): Optional metadata.
        """
        # The underlying ChromaStorage's update method should act as create-if-not-exists.
        self.storage.save_memory(collection_name=self.collection_name,
                                 data=data,
                                 ids=[key],
                                 metadata=metadata)

    def delete(self, key: str) -> None:
        """
        Deletes the memory entry with the given key.

        Args:
            key (str): The unique identifier for the memory entry to delete.
        """
        self.storage.delete_memory(collection_name=self.collection_name,
                                   doc_id=key)