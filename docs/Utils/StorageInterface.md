# Storage Interface Documentation

## Introduction to StorageInterface

The `StorageInterface` serves as a critical component in the AgentForge framework, providing a consistent interface for data storage and retrieval operations. It allows the system to interact with various databases, ensuring that data management is seamless regardless of the underlying storage solution.

## Key Features

- **Flexibility**: `StorageInterface` allows for easy swapping between different databases by updating the `Storage.yaml` configuration file.
- **Modularity**: The interface is designed to work with various database utilities that follow a consistent method naming convention, ensuring interoperability and ease of maintenance.

## How to Use StorageInterface

The `StorageInterface` class can be instantiated and used to interact with the storage utility of your choice, as demonstrated in the following example:

```python
from agentforge.utils.storage_interface import StorageInterface

# Initialize the Storage Interface
storage = StorageInterface().storage_utils
```

---

### Common Methods and Interoperability

In `storage_utils`, method names and the formats of the information they return must be consistent across different database utilities. This uniformity is crucial for ensuring that data can be handled predictably within the system, regardless of the database technology in use.

Below is a rundown of the common methods provided by the `ChromaUtils` class, which other database utility classes should emulate:

- `collection_list()`: Returns a list of all collections in the database. The format is a list of strings, each representing a collection name.

- `load_collection(params)`: Loads data from a collection based on the specified parameters. It returns a list of documents meeting the query criteria.

- `save_memory(params)`: Saves data to the specified collection. It does not return any value but will raise an exception if the operation fails.

- `query_memory(params, num_results=1)`: Retrieves data from the collection based on the provided query parameters. It returns a dictionary containing the query results, which includes the documents, metadatas, and distances if specified.

- `count_collection(collection_name)`: Provides the number of items in the specified collection. The return format is an integer representing the count.

For example, to get a list of all collections:

```python
collections = storage.collection_list()
```

### More Storage Methods

Here are descriptions of the rest of the methods within the `ChromaUtils` class:

- `init_embeddings()`: Initializes the embedding function based on the specified embedding model. It is crucial for enabling semantic search within ChromaDB.

- `init_storage()`: Establishes a connection to the ChromaDB client. If a persistent database path is provided, it connects to that; otherwise, it uses an ephemeral client.

- `select_collection(collection_name)`: Selects the specified collection from the database, readying it for operations. If the collection does not exist, it attempts to create it.

- `delete_collection(collection_name)`: Deletes the specified collection from the database.

- `peek(collection_name)`: Retrieves a snapshot of the latest document in the specified collection.

- `reset_memory()`: Clears all data within the database. It does not return any value but will raise an exception if the operation fails.

- `search_storage_by_threshold(parameters)`: Searches the storage by a semantic threshold, returning documents that are semantically close to the query text.

- `return_embedding(text_to_embed)`: Generates an embedding for the provided text, which can be used for semantic searches.

For the actual code implementation on these methods,
please refer to the [ChromaUtils](../../src/agentforge/utils/chroma_utils.py) class.

### Ensuring Data Format Consistency

When creating or adapting database utilities, developers must ensure that each method not only matches the method signature but also produces and handles return values in a consistent format. This consistency is critical for the seamless operation of the `StorageInterface`, as it relies on predictable data structures to perform system-wide operations.

Inconsistent return formats could lead to unexpected behavior, errors in data handling, or system failures. Therefore, maintaining uniformity in both method signatures and return data formats is essential for the health and scalability of the AgentForge system.

---

## Database Utilities

The `StorageInterface` is designed to work with various database utilities, such as `ChromaUtils` and `PineconeUtils`. Each utility must implement the same set of methods used by `StorageInterface` to maintain seamless functionality.

### [ChromaUtils](../../src/agentforge/utils/chroma_utils.py)

The default database utility `ChromaUtils` integrates with ChromaDB and provides an array of methods for managing collections, querying data, and handling embeddings.

### [PineconeUtils](../../src/agentforge/utils/pinecone_utils.py)

Although the implementation of `PineconeUtils` is currently non-functional, once fixed, it will provide similar functionalities for Pinecone database operations.

## Note on Database Switching

Switching between databases is made straightforward through the `Storage.yaml` configuration.
Users can set the `StorageAPI` to their preferred database,
and as long as the utility class implements the required methods, `StorageInterface` will handle the rest.
See our [Storage Documentation](../Settings/Storage.md) for more details.

## Community Contributions

> **Attention**: The Pinecone database integration is not currently operational. We are open to contributions from the community to either fix the existing `PineconeUtils` or to create new utilities for other databases. Your contributions are highly valuable in enhancing the flexibility and robustness of the AgentForge system.

---

For more detailed usage examples and method descriptions,
please refer to the specific utility class implementation for [ChromaUtils](../../src/agentforge/utils/chroma_utils.py) and [PineconeUtils](../../src/agentforge/utils/pinecone_utils.py).
