# src/agentforge/storage/chroma_storage.py

import chromadb
from chromadb.config import Settings
from agentforge.storage.base_storage import BaseStorage


class ChromaStorage(BaseStorage):
    def __init__(self):
        super().__init__()
        self.client = None

    def connect(self):
        if not self.storage_path:  # Ephemeral Storage
            self.client = chromadb.EphemeralClient()
            return

        self.client = chromadb.PersistentClient(path=str(self.storage_path), settings=Settings(allow_reset=True))

    def disconnect(self):
        # Chroma doesn’t necessarily require a formal disconnection,
        # but let’s just set self.client to None.
        self.client = None

    def create_collection(self, collection_name):
        if not self.client:
            raise ValueError("No Chroma client. Did you call connect() first?")
        self.client.get_or_create_collection(name=collection_name)

    def delete_collection(self, collection_name):
        if not self.client:
            raise ValueError("No Chroma client. Did you call connect() first?")
        self.client.delete_collection(name=collection_name)

    def insert(self, collection_name, data):
        """
        data is expected to be a list of dicts. Each dict might contain an 'id' field, plus anything else.
        We'll parse them to fit Chroma's expected arguments.
        """
        if not self.client:
            raise ValueError("No Chroma client. Did you call connect() first?")
        collection = self.client.get_or_create_collection(name=collection_name)

        # We need at least 'ids' to pass to upsert, and optionally 'documents' or 'metadatas'.
        # This is somewhat simplified: you might have different logic for how to handle doc content vs. metadata.
        ids = []
        documents = []
        metadatas = []

        for item in data:
            ids.append(item["id"])
            # Let's assume all the other keys except 'id' go in 'metadatas'
            # Or perhaps you store a "content" field in documents.
            content = item.get("content", "")
            documents.append(content)
            # filter out "id" and "content" so the rest is metadata
            meta = {k: v for k, v in item.items() if k not in ["id", "content"]}
            metadatas.append(meta)

        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def query(self, collection_name, query):
        """
        Here we’re using a naive approach: if query is something like {"id": "2"},
        we treat that as a 'where' filter in Chroma. Or you might do more advanced logic.
        We’ll return a list of dicts that represent each record.
        """
        if not self.client:
            raise ValueError("No Chroma client. Did you call connect() first?")
        collection = self.client.get_or_create_collection(name=collection_name)

        # For simplicity, assume we only handle one key in the query.
        # Real usage might need more sophisticated handling.
        results = collection.get(where=query, include=["metadatas", "documents", "embeddings"])

        # We’ll reconstruct them into a list of dicts:
        output = []
        for doc_id, doc_text, doc_meta in zip(results["ids"], results["documents"], results["metadatas"]):
            record = {"id": doc_id, "content": doc_text, **doc_meta}
            output.append(record)
        return output

    def update(self, collection_name, query, new_data):
        """
        We can handle updates in Chroma by retrieving the items via query,
        then upserting them again with the new data.
        """
        if not self.client:
            raise ValueError("No Chroma client. Did you call connect() first?")
        collection = self.client.get_or_create_collection(name=collection_name)

        existing_records = self.query(collection_name, query)
        if not existing_records:
            return  # no-op if we don't find anything

        # Update each record with new_data
        for record in existing_records:
            record.update(new_data)

        # Now upsert them again
        ids = []
        documents = []
        metadatas = []

        for record in existing_records:
            ids.append(record["id"])
            documents.append(record.get("content", ""))
            meta = {k: v for k, v in record.items() if k not in ["id", "content"]}
            metadatas.append(meta)

        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def delete(self, collection_name, query):
        """
        Similar approach: find the records, then remove them by ID.
        """
        if not self.client:
            raise ValueError("No Chroma client. Did you call connect() first?")
        collection = self.client.get_or_create_collection(name=collection_name)

        records_to_delete = self.query(collection_name, query)
        if not records_to_delete:
            return

        ids_to_delete = [r["id"] for r in records_to_delete]
        collection.delete(ids=ids_to_delete)

    def count(self, collection_name):
        if not self.client:
            raise ValueError("No Chroma client. Did you call connect() first?")
        collection = self.client.get_or_create_collection(name=collection_name)
        return collection.count()

    def reset_storage(self):
        """
        If we’re ephemeral, we can just reset everything.
        If we’re persistent, you might need to do something else
        (like re-initialize the PersistentClient with an empty dir).
        """
        if not self.client:
            raise ValueError("No Chroma client. Did you call connect() first?")
        self.client.reset()
