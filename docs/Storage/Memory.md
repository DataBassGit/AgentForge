# Memory Guide

**AgentForge** memory classes provide a high‑level API for storing and retrieving context data using ChromaStorage under the hood. Each memory instance resolves a `storage_id` and maps to one or more collections in ChromaDB.

---

## 1. Quick Start
```python
from agentforge.storage.memory import Memory

# Create a base memory context (by cog or persona)
mem = Memory(cog_name="MyCog", persona="default", collection_id="session_123")

# Store structured data
mem.update_memory(
    data={"user_input": "Hello world"},
    context={"session_id": "123"}
)

# Query similar items
results = mem.query_memory(query_text="Hello", num_results=5)
print(results)

# Delete an entry by ID
mem.delete(ids=["doc_1"])

# Wipe all memory (use with caution)
mem.wipe_memory()
```

---

## 2. Storage ID Resolution
Memory instances derive `storage_id` to partition data:
1. If `persona` is provided (and personas are enabled), uses `persona` name.  
2. Else if `cog_name` is given, uses that.  
3. Fallback to `"fallback_storage"` if neither.

This normalized `storage_id` is passed to `ChromaStorage.get_or_create(...)`. See [ChromaStorage Guide](ChromaStorage.md).

---

## 3. Base Memory API
### Constructor
```python
Memory(cog_name: str, persona: Optional[str] = None, collection_id: Optional[str] = None)
```  
- **cog_name**: Name of your code module or component.  
- **persona**: (Optional) Persona name for finer partitioning.  
- **collection_id**: (Optional) Overrides default collection naming; if omitted, defaults to `collection_id` in constructor.

### Methods
- **update_memory(data: dict, context: dict = None, ids: Union[str,list] = None, metadata: list[dict] = None)**  
  Flatten `data`, combine with `context` as metadata, and upsert into the collection.  
- **query_memory(query_text: Union[str,list], num_results: int = 5) → Optional[dict]**  
  Perform a semantic search, update `mem.store`, and return matching items.  
- **delete(ids: Union[str,list])**  
  Remove specific documents by ID.  
- **wipe_memory()**  
  Reset the entire ChromaDB for this `storage_id` (drops all collections).

---

## 4. ScratchPad
The `ScratchPad` subclass manages two collections:
1. **Main scratchpad** (`collection_id`): Holds the consolidated note.
2. **Log collection** (`scratchpad_log_{collection_id}`): Accumulates raw entries before consolidation.

```python
from agentforge.storage.scratchpad import ScratchPad
sp = ScratchPad(cog_name="MyCog", persona="alice", collection_id="notes")

# Add an entry
sp.update_memory(data={"content": "User said X"})

# Retrieve or initialize
pad = sp.query_memory(query_text=None)
print(pad["content"])
```
- When log entries ≥10, `ScratchPad` automatically consolidates via a helper agent, updates main pad, and clears the log.

---

## 5. Journal
The `Journal` subclass streamlines journaling workflows:
```python
from agentforge.storage.journal import Journal
jr = Journal(chroma_instance=mem.storage)
jr.save_journal_log(interaction=["msg1", "msg2"], metadata={"channel": "chat"})
entries = jr.recall_journal_entry(message="msg", categories="general", num_entries=3)
print(entries)
```  
- **save_journal_log**: Append raw interactions to `journal_log_table`.  
- **recall_journal_entry**: Semantic recall over logs, returns formatted history.

---

## 6. Episodic Memory
The `EpisodicMemory` class (in `episodic_memory.py`) supports:
- Chunking long entries via semantic split.  
- Storing both whole entries and individual chunks in separate collections.  
- Reflective agents for summarization and retrieval.

Example usage mirrors `Journal` but writes to `whole_journal_entries` and `journal_chunks_table`.

---

## 7. Best Practices
- Choose clear `collection_id` to avoid overlap across components.  
- Use metadata fields for rich filtering (`session_id`, `user_id`, `channel`).  
- Monitor collection size with `count_collection()`.  
- Leverage `mem.store` after queries for in‑memory caching.  
- For advanced control, interact directly with `mem.storage` (see [ChromaStorage Guide](ChromaStorage.md)).

---

## 8. Related Documentation
- [ChromaStorage Guide](ChromaStorage.md)  
- [Storage Settings](../Settings/Storage.md)  
- [AgentClass API](../../Agents/AgentClass.md) 