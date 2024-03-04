# Storage Interface Documentation

## Overview

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

## Custom Database Integration with Storage Interface

### Overview

The **AgentForge** framework offers flexibility in database selection, allowing developers to integrate their preferred database solutions. While `ChromaDB` (accessed via the `ChromaUtils` class) is the default storage option, the framework's design accommodates the use of alternative databases to meet specific needs or preferences.

### Storage Interface and `storage_utils` Attribute

- The `storage_utils` attribute within the storage interface class serves as a gateway to the database functionalities. By default, it is instantiated as an instance of `ChromaUtils`, which interacts with `ChromaDB`.
  
- Developers aiming to integrate a different database solution must create a custom class that adheres to the interface defined by `ChromaUtils`. This custom class should then be assigned to the `storage_utils` attribute, ensuring seamless interoperability within the framework.

### Ensuring Compatibility

To ensure full compatibility and maintain the framework's expected behavior, any custom database utility class must:

- **Match Method Names**: Implement all the methods provided by `ChromaUtils`, using the same method names to preserve the consistency of database operations across the framework.

- **Align Method Signatures**: Ensure that the intake attributes (parameters) for each method correspond precisely with those defined in `ChromaUtils`. This alignment guarantees that the rest of the framework can interact with the storage layer without encountering method signature mismatches.

- **Replicate Return Formats**: Ensure that the data returned by each method matches the format expected by the **AgentForge** framework, as established in the `ChromaUtils` documentation below.

### Example Scenario

If a developer wishes to integrate a SQL-based storage system, they would need to:

1. **Create a Custom Class**: Develop a class, say `SQLUtils`, implementing the necessary storage operations like `collection_list`, `save_memory`, `query_memory`, etc.

2. **Ensure Method Consistency**: Adopt the same method names and parameters as those in `ChromaUtils`, adapting the internal logic to interact with the SQL database.

3. **Integrate with AgentForge**: Assign the `SQLUtils` instance to the `storage_utils` attribute within the storage interface, replacing the default `ChromaUtils` instance.

By adhering to these guidelines, developers can leverage the **AgentForge** framework's robust features while utilizing their database of choice, ensuring that agents operate effectively and consistently regardless of the underlying storage solution.

---

## Common Methods in Chroma Utils

The `storage_utils` provided by the `ChromaUtils` class facilitate a range of database interactions crucial for the AgentForge framework. Below are the core methods offered by the `ChromaUtils` class, serving as standards for any database utility classes within the framework:

- **`collection_list()`**: Returns an array of collection names available within the database.

- **`load_collection(collection_name, include=None, where=None, where_doc=None)`**: Retrieves data from a specified collection, allowing for filter criteria to refine the data fetched.

- **`save_memory(collection_name, data, ids=None, metadata=None)`**: Persists data within a specified collection, organizing it based on provided identifiers and metadata.

- **`query_memory(collection_name, query=None, filter_condition=None, include=None, embeddings=None, num_results=1)`**: Executes a query against a specified collection, returning data that meets the query conditions.

- **`count_collection(collection_name)`**: Counts the number of documents within a specified collection, providing insights into its size.

- **`delete_collection(collection_name)`**: Removes an entire collection from the database, along with all its data.

- **`peek(collection_name)`**: Offers a preview of the latest document within a specified collection, useful for quick inspections or validations.

- **`reset_memory()`**: Clears the database entirely, removing all data and collections, to be used with caution due to its irreversible nature.

- **`search_storage_by_threshold(collection_name, query_text, threshold=0.7, num_results=1)`**: Searches a collection for documents that meet a defined semantic similarity threshold to the provided query text.

- **`return_embedding(text_to_embed)`**: Generates an embedding for the specified text using the configured embedding function, essential for semantic comparisons and searches.

### Initialization and Configuration

- **`init_embeddings()`**: Sets up the embedding function critical for supporting semantic operations within the database, chosen based on system configuration.

- **`init_storage()`**: Establishes the database connection, determining whether to connect to a persistent storage path or operate in an ephemeral mode.

- **`select_collection(collection_name)`**: Activates or creates a collection within the database, preparing it for subsequent data operations.

### Advanced Data Management

- **`delete_collection(collection_name)`**: Eliminates the specified collection from the database.

- **`peek(collection_name)`**: Retrieves a brief snapshot of the most recent content in a collection.

- **`reset_memory()`**: Wipes the entire database, removing all stored data and collections.

### Semantic Search and Embeddings

- **`search_storage_by_threshold(collection_name, query_text, threshold, num_results)`**: Performs semantic search within a collection, identifying documents that closely align with the query based on a similarity threshold.

- **`return_embedding(text_to_embed)`**: Produces an embedding vector for text, facilitating semantic comparisons and retrieval operations.

For detailed examples and further information on each method's implementation, developers are encouraged to refer directly to the [ChromaUtils](../../src/agentforge/utils/chroma_utils.py) source code.

---

## Note on Database Switching

Switching between databases is made straightforward through the `Storage.yaml` configuration.
Users can set the `StorageAPI` to their preferred database,
and as long as the utility class implements the required methods, `StorageInterface` will handle the rest.
See our [Storage Documentation](../Settings/Storage.md) for more details.

## Community Contributions

> **Attention**: The Pinecone database integration is not currently operational. We are open to contributions from the community to either fix the existing `PineconeUtils` or to create new utilities for other databases. Your contributions are highly valuable in enhancing the flexibility and robustness of the **AgentForge** framework.

