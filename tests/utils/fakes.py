"""In-memory stand-ins for production storage back-ends used in unit tests."""
from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional

__all__ = ["FakeChromaStorage"]


class _FakeCollection:
    """Extremely small subset of Chroma collection API sufficient for tests."""

    def __init__(self) -> None:
        self._docs: Dict[str, str] = {}
        self._metas: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()

    # Core operations -----------------------------------------------------
    def upsert(self, documents: List[str], metadatas: List[dict], ids: List[str]) -> None:  # noqa: D401
        with self._lock:
            for _id, doc, meta in zip(ids, documents, metadatas):
                self._docs[_id] = doc
                self._metas[_id] = meta or {}

    def get(self, ids: Optional[List[str]] = None):  # noqa: D401
        # Lock-free read: copy current state once to avoid partial reads.
        snapshot_docs = self._docs.copy()
        snapshot_meta = self._metas.copy()
        if ids is None:
            ids = list(snapshot_docs.keys())
        return {
            "ids": ids,
            "documents": [snapshot_docs[i] for i in ids if i in snapshot_docs],
            "metadatas": [snapshot_meta.get(i, {}) for i in ids],
        }

    def delete(self, ids: Optional[List[str]] = None) -> None:  # noqa: D401
        with self._lock:
            ids = ids or list(self._docs.keys())
            for _id in ids:
                self._docs.pop(_id, None)
                self._metas.pop(_id, None)

    def count(self) -> int:
        with self._lock:
            return len(self._docs)

    def query(self, num_results: int = 1):
        with self._lock:
            ids = list(self._docs.keys())[:num_results]
            return self.get(ids=ids)


class FakeChromaStorage:
    """Drop-in replacement for `agentforge.storage.chroma_storage.ChromaStorage`."""

    _registry: Dict[str, "FakeChromaStorage"] = {}
    _registry_lock = threading.Lock()

    def __init__(self, storage_id: str):
        self.storage_id = storage_id
        self._collections: Dict[str, _FakeCollection] = {}
        self._current: Optional[_FakeCollection] = None
        self._lock = threading.RLock()

    # Registry helpers ----------------------------------------------------
    @classmethod
    def get_or_create(cls, storage_id: str):
        with cls._registry_lock:
            if storage_id not in cls._registry:
                cls._registry[storage_id] = cls(storage_id)
            return cls._registry[storage_id]

    @classmethod
    def clear_registry(cls):
        with cls._registry_lock:
            cls._registry.clear()

    # Collection management ----------------------------------------------
    def select_collection(self, collection_name: str):
        if not collection_name or not isinstance(collection_name, str) or collection_name.strip() == "":
            raise Exception("Invalid collection name")
        self._current = self._collections.setdefault(collection_name, _FakeCollection())
        return self._current

    def delete_collection(self, collection_name: str):
        self._collections.pop(collection_name, None)
        if self._current is not None and self._current is self._collections.get(collection_name):
            self._current = None

    def count_collection(self, collection_name: str):
        return self.select_collection(collection_name).count()

    def peek(self, collection_name: str):
        col = self.select_collection(collection_name)
        ids = list(col._docs.keys())[:10]
        if not ids:
            return {"documents": "No Results!"}
        return {
            "documents": [col._docs[i] for i in ids],
            "ids": ids,
            "metadatas": [col._metas.get(i, {}) for i in ids],
        }

    # High-level API (subset) --------------------------------------------
    def save_to_storage(self, collection_name: str, data: list | str, ids: Optional[list] = None, metadata: Optional[list[dict]] = None):
        data = [data] if isinstance(data, str) else list(data)
        if ids is None:
            # Generate incremental ids based on current collection size
            existing = self.select_collection(collection_name).count()
            ids = [str(existing + i + 1) for i in range(len(data))]
        metadata = metadata or [{} for _ in data]
        if not (len(data) == len(ids) == len(metadata)):
            raise ValueError("data, ids, and metadata must have the same length")
        # Ensure each metadata dict has an integer 'id' mirroring the sequential id
        processed_metas = []
        for idx, meta in enumerate(metadata):
            meta_copy = dict(meta)  # avoid mutating caller's dict
            # ids[idx] is a string; store numeric version
            try:
                meta_copy.setdefault("id", int(ids[idx]))
            except ValueError:
                # fall back to string if non-numeric but still provide something
                meta_copy.setdefault("id", ids[idx])
            processed_metas.append(meta_copy)

        self.select_collection(collection_name).upsert(data, processed_metas, ids)

    def query_storage(self, *, collection_name: str, query: Optional[str | List[str]] = None, num_results: int = 1, **_):
        col = self.select_collection(collection_name)
        res = col.query(num_results=num_results)
        # If collection empty, return {} to mirror production behaviour
        if not res["documents"]:
            return {}
        return res

    def delete_from_storage(self, collection_name: str, ids: List[str] | str):
        if not isinstance(ids, list):
            ids = [ids]
        self.select_collection(collection_name).delete(ids)

    def reset_storage(self):
        self._collections.clear()

    def get_last_x_entries(self, collection_name: str, x: int, include: list = None):
        """
        Retrieve the last X entries from a collection, ordered by insertion (id ascending).
        Args:
            collection_name (str): The name of the collection.
            x (int): Number of most recent entries to retrieve.
            include (list, optional): Which fields to include in the result.
                Defaults to ['documents', 'metadatas', 'ids'].
        Returns:
            dict: The collection entries, sorted by id ascending, with only the requested fields.
        """
        if include is None:
            include = ['documents', 'metadatas', 'ids']
        col = self.select_collection(collection_name)
        # Sort ids as integers if possible, else as strings
        try:
            sorted_ids = sorted(col._docs.keys(), key=lambda i: int(i))
        except Exception:
            sorted_ids = sorted(col._docs.keys())
        last_ids = sorted_ids[-x:] if x > 0 else []
        # Always return in ascending order
        last_ids = sorted(last_ids, key=lambda i: int(i) if i.isdigit() else i)
        result = {
            'documents': [col._docs[i] for i in last_ids],
            'metadatas': [col._metas.get(i, {}) for i in last_ids],
            'ids': last_ids
        }
        # Only include requested fields
        return {k: result[k] for k in include if k in result} 