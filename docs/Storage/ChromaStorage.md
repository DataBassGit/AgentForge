# ChromaStorage Guide

## Introduction

The **ChromaStorage** class in **AgentForge** provides a robust interface for interacting with **ChromaDB**, a high-performance vector database. With **ChromaStorage**, agents can efficiently save and retrieve data—enabling persistent memory capabilities for context retention, recall of past interactions, or any data-driven functionality you need.

This guide explains how to use **ChromaStorage** to:
- Save documents (and their metadata) to persistent storage.
- Query and retrieve stored documents based on similarity, filters, or metadata.
- Manage collections (create, list, delete, and peek into collections).
- Generate embeddings for text using your chosen embedding model.

---

## Overview

**ChromaStorage** is implemented in the `chroma_storage.py` file. Its key features include:
- **Initialization of Storage**: It sets up a persistent or ephemeral ChromaDB client, based on your configuration.
- **Embedding Initialization**: It configures an embedding function (for example, using SentenceTransformer or OpenAI’s embedding models) as specified in your settings.
- **Collection Management**: Methods to select, create, delete, and list collections.
- **Data Operations**: Methods to save, load, and query data, as well as functions for generating document IDs, applying timestamps, and more.

The ChromaStorage class uses your system’s storage settings (found in `storage.yaml`) to control aspects such as persistence, timestamping, and the selected embedding model.

---

## Using ChromaStorage in Your Agents

When storage is enabled in **AgentForge**, each agent gains access to persistent memory via an instance of **ChromaStorage** (commonly exposed as `self.storage`). For example, an agent can save conversational memory or other context by calling `self.storage.save_memory(...)`, and later query that memory with `self.storage.query_memory(...)`.

### Example Usage in an Agent

```python
from agentforge.agent import Agent

class MemoryAgent(Agent):
    def process_data(self):
        # Save a document to the 'agent_memory' collection
        self.storage.save_memory(
            collection_name='agent_memory',
            data="Remember to follow up on user feedback.",
            metadata=[{'type': 'reminder'}]
        )

    def retrieve_memory(self):
        # Query for stored documents matching a keyword
        results = self.storage.query_memory(
            collection_name='agent_memory',
            query="feedback",
            num_results=3
        )
        if results and results.get('documents'):
            for doc in results['documents']:
                print(f"Memory: {doc}")
```

---

## Key Methods

Below is a summary of the primary methods provided by the **ChromaStorage** class:

### Initialization and Setup

- **`init_storage()`**  
  Initializes the ChromaDB client. If a persistent database path is set, a persistent client is created; otherwise, an ephemeral client is used. If the configuration specifies a fresh start, it resets storage upon initialization.

- **`init_embeddings()`**  
  Configures the embedding function based on the `embedding.selected` value from your settings. Supported backends (e.g., `all-distilroberta-v1`, `openai_ada2`, etc.) are initialized here.

- **`chromadb_settings()`**  
  Retrieves storage settings such as the database path and the selected embedding from the configuration.

### Collection Management

- **`select_collection(collection_name)`**  
  Selects or creates a collection within ChromaDB by the given name.

- **`delete_collection(collection_name)`**  
  Deletes an entire collection from storage.

- **`collection_list()`**  
  Lists all collections currently available in storage.

- **`peek(collection_name)`**  
  Provides a brief overview of a collection's contents.

- **`count_collection(collection_name)`**  
  Returns the number of documents in a specified collection.

### Data Operations

- **`save_memory(collection_name, data, ids=None, metadata=None)`**  
  Saves one or more documents into the specified collection. If document IDs or metadata aren’t provided, they’re automatically generated. Timestamps (ISO or Unix) are applied based on configuration.

- **`query_memory(collection_name, query=None, filter_condition=None, include=None, embeddings=None, num_results=1)`**  
  Queries a collection to retrieve documents similar to the provided text or embedding. You can also filter results based on metadata.

- **`load_collection(collection_name, include=None, where=None, where_doc=None)`**  
  Loads data from a collection based on filtering conditions.

- **`return_embedding(text_to_embed)`**  
  Generates an embedding vector for a given piece of text using the configured embedding function.

- **`delete_memory(collection_name, doc_id)`**  
  Deletes a specific document from a collection using its unique ID.

### Advanced Data Operations

- **`search_storage_by_threshold(collection_name, query, threshold=0.8, num_results=1)`**  
  Searches a collection for documents that meet or exceed a specified similarity threshold.

- **`search_metadata_min_max(collection_name, metadata_tag, min_max)`**  
  Retrieves the document with the minimum or maximum value for a given metadata tag.

- **`rerank_results(query_results, query, temp_collection_name, num_results=None)`**  
  Re-ranks query results by temporarily storing them in a collection, re-querying, and then deleting the temporary collection.

- **`combine_query_results(*query_results)`**  
  Merges multiple query results, removes duplicates, and assigns new IDs as needed.

---

## Best Practices

- **Consistent Collection Naming**:  
  Use clear and consistent names for collections to keep your stored data organized.

- **Leverage Metadata**:  
  Attach meaningful metadata to documents to enhance query filtering and retrieval.

- **Test Query Results**:  
  Always verify that queries return the expected documents, especially when using similarity thresholds.

- **Use Timestamps**:  
  Enable ISO or Unix timestamp settings for a clear audit trail of when data was saved.

- **Be Cautious with Data Deletion**:  
  Methods like `reset_memory` or `delete_collection` permanently remove data. Use these with care.

- **Combine Query Results**:  
  When retrieving data from multiple queries, use `combine_query_results` to eliminate duplicates and create a unified view.

---

## Additional Resources


- **[Settings Overview](../Settings/Settings.md)** 
- **[Storage Guide](../Storage/ChromaStorage.md)**

---

## Conclusion

The **ChromaStorage** class in **AgentForge** empowers your agents with persistent memory using ChromaDB. With methods to save, query, and manage collections, it provides a powerful backend for building context-aware, stateful agents. By following the usage guidelines and best practices outlined above, you can effectively integrate and utilize storage as memory within your projects.

---

**Need Help?**

If you have any questions or need further assistance:
- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)
