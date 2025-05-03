# ChromaStorage Guide

ChromaStorage is the core interface to ChromaDB in **AgentForge**. It uses a thread‑safe registry keyed by `storage_id` to provide singleton storage clients, and supports both persistent and in‑memory (ephemeral) modes based on your configuration.

## 1. Quick Start
```python
from agentforge.storage.chroma_storage import ChromaStorage

# Obtain (or create) a storage client for your context
storage = ChromaStorage.get_or_create(storage_id="my_context_id")
```  
Every call to `get_or_create` with the same `storage_id` returns the same instance.

## 2. Registry & Lifecycle
- **get_or_create(storage_id: str) → ChromaStorage**
  - Returns a singleton for `storage_id`. Raises ValueError if `storage_id` is empty.
- **clear_registry()**
  - Removes all stored instances (useful for tests).
- **describe_instance() → dict**
  - Returns `{ storage_id, db_path, db_embed }` for debugging and verification.

## 3. Configuration Source
ChromaStorage reads from your storage settings (see [Storage Settings](../Settings/Storage.md)):
```yaml
options:
  persist_directory: ./db/ChromaDB
  fresh_start: false
embedding:
  selected: distil_roberta
embedding_library:
  distil_roberta: all-distilroberta-v1
  all_mini: all-MiniLM-L6-v2
```
- **db_path**: `<project_root>/<persist_directory>/<storage_id>`
- **db_embed**: Resolved via `embedding_library[selected]`

## 4. Initialization Steps
1. **init_embeddings()**
   - No `db_embed` → uses `DefaultEmbeddingFunction()`
   - `text-embedding-ada-002` → uses `OpenAIEmbeddingFunction` (requires `OPENAI_API_KEY`)
   - Otherwise → uses `SentenceTransformerEmbeddingFunction(model_name=db_embed)`
2. **init_storage()**
   - **Persistent Mode**: `PersistentClient(path=db_path)` when `db_path` directory exists or is configured.
   - **Ephemeral Mode**: `EphemeralClient()` if no valid `db_path` or purely in-memory use; data will not persist after process exits.
   - If `fresh_start: true`, calls `reset_storage()` to wipe all existing data for the `storage_id`.

## 5. Core Methods
### Collection Management
- **select_collection(name: str)** - 
  Create or switch to a collection by name.
- **collection_list() → list[str]** - 
  List all collections in the current database.
- **delete_collection(name: str)** - 
  Permanently remove a collection.
- **count_collection(name: str) → int** - 
  Return the number of documents in a collection.
- **peek(name: str) → dict** - 
  Get a quick summary of a collection's content.

### Data Operations
- **save_to_storage(name: str, data: list[str], ids: list[str], metadata: list[dict])** - 
  Upsert documents with optional IDs and metadata. Applies timestamps from settings.
- **load_collection(name: str, include: dict = None, where: dict = None, where_doc: dict = None) → dict** - 
  Retrieve raw documents with filter conditions.
- **query_storage(name: str, query: Union[str,list], num_results: int = 1, filter_condition: dict = None, include: list = None, embeddings: list = None) → dict** - 
  Perform similarity search over vector embeddings.
- **delete_from_storage(name: str, ids: Union[str,list])** - 
  Delete documents by ID.
- **return_embedding(text: str) → list[float]** - 
  Compute embedding for a text snippet using the configured model.

## 6. Advanced Operations
- **search_storage_by_threshold(name, query, threshold: float, num_results: int)** - 
  Returns documents found within the storage that meet the similiarity threshold.
- **combine_query_results(\*results) → dict** - 
  Merge multiple query results, dedupe entries, reassign IDs.
- **rerank_results(results, query, temp_collection, num_results: int)** - 
  Rerank a result set by temporarily indexing and re-querying.

## 7. Usage Examples
```python
# Initialize or reuse storage client
storage = ChromaStorage.get_or_create(storage_id="session_42")

# Save a note
storage.save_to_storage(
    name="user_notes",
    data=["Check logs for errors."],
    ids=["note1"],
    metadata=[{"tag": "reminder"}]
)

# Perform a semantic search
results = storage.query_storage(
    name="user_notes",
    query="errors",
    num_results=3
)
for doc in results.get("documents", []):
    print(doc)
```

## 8. Best Practices
- Use clear, context‑specific `storage_id` values (e.g., `persona_name`, `cog_name`).
- Consistently name collections to avoid overlap.
- Attach meaningful metadata for effective filtering.
- Validate setup with `describe_instance()`.
- Call `clear_registry()` in tests to isolate state.

## 9. Related Documentation
- [Storage Settings](../Settings/Storage.md)
- [Memory Guide](Memory.md)
- [Cogs Guide](../Cogs/Cogs.md)
- [Agent Class API](../Agents/AgentClass.md)
