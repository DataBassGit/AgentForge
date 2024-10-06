# ChromaUtils Utility Guide

## Introduction

The `ChromaUtils` class in **AgentForge** is a utility for managing interactions with **ChromaDB**, a vector database for efficient storage and retrieval of embeddings. This utility provides methods for initializing embeddings, managing storage, saving data, querying, and handling collections within ChromaDB.

When storage is enabled in the system settings, agents have access to storage through an instance of `ChromaUtils`. This allows agents to save and retrieve data, effectively enabling them to have memory capabilities.

---

## Overview

**ChromaDB** is a vector database that allows for efficient similarity search and storage of high-dimensional embeddings. The `ChromaUtils` class simplifies interactions with ChromaDB, abstracting away the complexity of direct database operations.

Key functionalities include:

- **Initialization**: Setting up embeddings and storage configurations.
- **Data Management**: Saving data to collections and querying data based on similarity or metadata.
- **Collection Management**: Creating, selecting, deleting, and listing collections.
- **Utility Functions**: Additional methods for handling embeddings, counting documents, and combining results.

---

## Using ChromaUtils in Agents

When you create an agent, if storage is enabled, the agent will have access to a `storage` attribute, which is an instance of `ChromaUtils`. You can use this instance to save and query data.

**Example in Agent Context**:

```python
from agentforge import Agent

class MyAgent(Agent):
    def process_data(self):
        # Save data to storage
        self.storage.save_memory(
            collection_name='my_collection',
            data='This is a sample document.',
            metadata=[{'tag': 'sample'}]
        )

    def query_data(self):
        # Query data from storage
        results = self.storage.query_memory(
            collection_name='my_collection',
            query='sample',
            num_results=5
        )
        print(results['documents'])
```

---

## Key Methods

### 1. `save_memory`

**Purpose**: Saves data to a specified collection in the storage.

**Usage**:

```python
self.storage.save_memory(
    collection_name='collection_name',
    data='Your data here',
    ids=['unique_id'],           # Optional
    metadata=[{'key': 'value'}]  # Optional
)
```

**Parameters**:

- `collection_name` (str): The name of the collection to save data to. Will be created if it doesn't exist.
- `data` (str or list): The document(s) to be saved. Can be a single string or a list of strings.
- `ids` (list, optional): A list of unique IDs for the documents. If not provided, IDs will be generated automatically.
- `metadata` (list of dicts, optional): Metadata associated with each document.

**Returns**: None

**Notes**:

- If `data` is a single string, it will be converted to a list.
- Metadata can include timestamps if configured in `system.yaml`.

---

### 2. `query_memory`

**Purpose**: Queries the storage for documents similar to a query string or embedding.

**Usage**:

```python
results = self.storage.query_memory(
    collection_name='collection_name',
    query='Your query text',
    num_results=5
)
```

**Parameters**:

- `collection_name` (str): The name of the collection to query.
- `query` (str or list, optional): The query text(s). If not provided, `embeddings` must be provided.
- `filter_condition` (dict, optional): Conditions to filter the results based on metadata.
- `include` (list, optional): Specifies what to include in the results (e.g., `["documents", "metadatas"]`).
- `embeddings` (list, optional): Precomputed embeddings to use as the query.
- `num_results` (int): The maximum number of results to return.

**Returns**:

- `dict`: A dictionary containing the query results, which may include keys like `'documents'`, `'metadatas'`, and `'distances'`.

**Example**:

```python
results = self.storage.query_memory(
    collection_name='my_collection',
    query='sample',
    num_results=3
)
print(results['documents'])
```

---

### 3. `select_collection`

**Purpose**: Selects or creates a collection within the storage.

**Usage**:

```python
self.storage.select_collection('collection_name')
```

**Parameters**:

- `collection_name` (str): The name of the collection to select or create.

**Returns**: None

**Notes**:

- Typically, you don't need to call this method directly as other methods handle collection selection.

---

### 4. `load_collection`

**Purpose**: Loads data from a collection based on filters.

**Usage**:

```python
data = self.storage.load_collection(
    collection_name='collection_name',
    include=['documents', 'metadatas']
)
```

**Parameters**:

- `collection_name` (str): The name of the collection to load from.
- `include` (list, optional): Specifies what to include in the results.
- `where` (dict, optional): Filters based on metadata.
- `where_doc` (dict, optional): Filters based on document content.

**Returns**:

- `dict`: The data loaded from the collection.

---

### 5. `reset_memory`

**Purpose**: Resets the entire storage, removing all collections and data.

**Usage**:

```python
self.storage.reset_memory()
```

**Parameters**: None

**Returns**: None

**Warning**:

- This method will permanently delete all data in the storage. Use with caution.

---

### 6. `return_embedding`

**Purpose**: Generates an embedding for a given text.

**Usage**:

```python
embedding = self.storage.return_embedding('Text to embed')
```

**Parameters**:

- `text_to_embed` (str): The text to generate an embedding for.

**Returns**:

- `list`: A list containing the embedding vector.

---

### 7. `delete_collection`

**Purpose**: Deletes a specified collection from storage.

**Usage**:

```python
self.storage.delete_collection('collection_name')
```

**Parameters**:

- `collection_name` (str): The name of the collection to delete.

**Returns**: None

---

### 8. `collection_list`

**Purpose**: Lists all collections currently in storage.

**Usage**:

```python
collections = self.storage.collection_list()
print(collections)
```

**Parameters**: None

**Returns**:

- `list`: A list of collection names.

---

### 9. `peek`

**Purpose**: Retrieves a brief overview of a collection's contents.

**Usage**:

```python
overview = self.storage.peek('collection_name')
print(overview)
```

**Parameters**:

- `collection_name` (str): The name of the collection to peek into.

**Returns**:

- `dict` or `None`: A dictionary containing an overview of the collection's contents.

---

### 10. `count_collection`

**Purpose**: Counts the number of documents in a collection.

**Usage**:

```python
count = self.storage.count_collection('collection_name')
print(f'There are {count} documents in the collection.')
```

**Parameters**:

- `collection_name` (str): The name of the collection.

**Returns**:

- `int`: The number of documents in the collection.

---

## Practical Application

### Saving Agent Memories

Agents can use `save_memory` to store important information, such as user interactions, context, or any data they might need to recall later.

**Example**:

```python
self.storage.save_memory(
    collection_name='agent_memory',
    data='Remember to check the user\'s preferences.',
    metadata=[{'type': 'reminder'}]
)
```

### Querying Agent Memories

Agents can retrieve stored information using `query_memory`, allowing them to recall previous interactions or relevant data.

**Example**:

```python
results = self.storage.query_memory(
    collection_name='agent_memory',
    query='preferences',
    num_results=1
)
if results and results.get('documents'):
    reminder = results['documents'][0]
    print(f'Reminder: {reminder}')
```

---

## Best Practices

- **Consistent Collection Names**: Use consistent and meaningful collection names to organize your data effectively.
- **Metadata Usage**: Leverage metadata to store additional information about your documents, making it easier to filter and query.
- **Error Handling**: Always check the results returned by query methods for `None` or empty results before proceeding.
- **Caution with Resetting Storage**: Be careful when using `reset_memory`, as it will delete all stored data.

---

## Configuration in `system.yaml`

The behavior of `ChromaUtils` can be configured in the `system.yaml` file under the storage settings.

**Example Configuration**:

```yaml
# Storage Settings
StorageEnabled: true
SaveMemory: true
ISOTimeStampMemory: true
UnixTimeStampMemory: true
PersistDirectory: ./DB/ChromaDB
DBFreshStart: false
Embedding: all-distilroberta-v1
```

- **`StorageEnabled`**: Enables or disables the storage system.
- **`SaveMemory`**: Determines if agents save data to storage.
- **`ISOTimeStampMemory`**: Includes ISO 8601 timestamps when saving data.
- **`UnixTimeStampMemory`**: Includes Unix timestamps when saving data.
- **`PersistDirectory`**: Specifies the path for persistent storage.
- **`DBFreshStart`**: If `true`, wipes storage on initialization.
- **`Embedding`**: Specifies the embedding model used.

---

## Conclusion

The `ChromaUtils` utility in **AgentForge** provides agents with the ability to store and retrieve data efficiently using ChromaDB. By utilizing the methods provided, developers can enhance their agents with memory capabilities, enabling more complex and stateful interactions.

---

**Need Help?**

If you have questions or need assistance, feel free to reach out:

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)

---