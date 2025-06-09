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
- **get_or_create(storage_id: str) -> ChromaStorage**
  - Returns a singleton for `storage_id`. Raises ValueError if `storage_id` is empty.
- **clear_registry()**
  - Removes all stored instances (useful for tests).
- **describe_instance() -> dict**
  - Returns `{ storage_id, db_path, db_embed }` for debugging and verification.

## 3. Configuration Source
ChromaStorage reads from your storage settings (see [Storage Settings](../settings/storage.md)):
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
- **select_collection(collection_name: str)**
  - Create or switch to a collection by name. Automatically creates the collection if it does not exist.
- **collection_list() -> list**
  - List all collections in the current database.
- **delete_collection(collection_name: str)**
  - Permanently remove a collection.
- **count_collection(collection_name: str) -> int**
  - Return the number of documents in a collection.
- **peek(collection_name: str) -> dict**
  - Get a quick summary of a collection's content.

### Data Operations
- **save_to_storage(collection_name: str, data: Union[str, list], ids: Optional[list] = None, metadata: Optional[list[dict]] = None)**
  - Upsert documents with optional IDs and metadata. Applies timestamps and UUIDs if configured. If `ids` is not provided, sequential IDs are assigned automatically.
- **load_collection(collection_name: str, include: list = None, where: dict = None, where_doc: dict = None) -> dict**
  - Retrieve raw documents with filter conditions. `include` specifies which fields to return (default: `["documents", "metadatas"]`).
- **query_storage(collection_name: str, query: Optional[Union[str, list]] = None, filter_condition: Optional[dict] = None, include: Optional[list] = None, embeddings: Optional[list] = None, num_results: int = 1) -> dict**
  - Perform similarity search over vector embeddings. Either `query` or `embeddings` must be provided.
- **delete_from_storage(collection_name: str, ids: Union[str, list])**
  - Delete documents by ID.
- **return_embedding(text_to_embed: str) -> list**
  - Compute embedding for a text snippet using the configured model.

### Advanced Operations
- **search_storage_by_threshold(collection_name: str, query: str, threshold: float = 0.8, num_results: int = 1) -> dict**
  - Returns documents found within the storage that meet the similarity threshold.
- **combine_query_results(*query_results) -> dict**
  - Merge multiple query results, deduplicate entries, and reassign IDs.
- **rerank_results(query_results: dict, query: str, temp_collection_name: str, num_results: Optional[int] = None) -> dict**
  - Rerank a result set by temporarily indexing and re-querying.
- **get_last_x_entries(collection_name: str, x: int, include: list = None) -> dict**
  - Retrieve the last X entries from a collection, ordered by sequential ID. `include` specifies which fields to return (default: `["documents", "metadatas", "ids"]`).
- **search_metadata_min_max(collection_name: str, metadata_tag: str, min_max: str) -> dict or None**
  - Retrieve the collection entry with the minimum or maximum value for the specified metadata tag (`min_max` is either "min" or "max").
- **combine_and_rerank(query_results: list, rerank_query: str, num_results: int = 5) -> dict**
  - Combine multiple query results, rerank them based on a new query, and return the top results.
- **get_next_sequential_id(collection_name: str) -> int**
  - Get the next sequential integer ID for a collection.
- **apply_sequential_ids(collection_name: str, data: list, metadata: list[dict]) -> tuple[list, list[dict]]**
  - Assign sequential IDs to a batch of data and update their metadata accordingly.

## 6. Usage Examples
```python
# Initialize or reuse storage client
storage = ChromaStorage.get_or_create(storage_id="session_42")

# Save a note
storage.save_to_storage(
    collection_name="user_notes",
    data=["Check logs for errors."],
    ids=["1"],
    metadata=[{"tag": "reminder"}]
)

# Perform a semantic search
results = storage.query_storage(
    collection_name="user_notes",
    query="errors",
    num_results=3
)
for doc in results.get("documents", []):
    print(doc)

# Get the last 5 entries
recent = storage.get_last_x_entries(
    collection_name="user_notes",
    x=5
)
print(recent)
```

## 7. Best Practices
- Use clear, context‑specific `storage_id` values (e.g., `persona_name`, `cog_name`).
- Consistently name collections to avoid overlap.
- Attach meaningful metadata for effective filtering.
- Validate setup with `describe_instance()`.
- Call `clear_registry()` in tests to isolate state.

## 8. Related Documentation
- [Storage Settings](../settings/storage.md)
- [Cogs Guide](../cogs/cogs.md)
- [Agent Class API](../agents/agent_class.md)
