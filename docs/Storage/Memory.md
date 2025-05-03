# Memory Guide

**AgentForge** memory classes provide a high‑level API for storing and retrieving context data using ChromaStorage under the hood. Memory is a critical component in both individual agents and multi-agent Cogs, enabling contextual awareness and information persistence.

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

# Access the memory store directly
print(mem.store)  # Contains all retrieved items

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
- **cog_name**: Name of your cog or component.  
- **persona**: (Optional) Persona name for finer partitioning.  
- **collection_id**: (Optional) Overrides default collection naming; if omitted, defaults to the memory's instance ID.

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

## 4. Memory in Cogs
Cogs can define multiple memory nodes that are shared across agents:

```yaml
cog:
  name: "ConversationFlow"
  
  memory:
    - id: chat_history
      type: agentforge.storage.memory.Memory
      collection_id: conversation_log
      query_before: [respond]   # Query this memory before these agents run
      update_after: [analyze]   # Update this memory after these agents run
      query_keys: [user_input]  # Keys to extract from context for queries
      update_keys: [analysis]   # Keys to extract from context for updates
```

During execution, the Cog engine:
1. Instantiates each memory node with the cog's name and collection ID
2. Makes memory available to agents via their context as `memory[node_id]`
3. Automatically queries/updates memory at the appropriate stages based on configuration

See the [Cogs Documentation](../Cogs/Cogs.md) for more details on memory integration in multi-agent workflows.

---

## 5. Memory Subclasses

### ScratchPad
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

### Journal
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

### Episodic Memory
The `EpisodicMemory` class (in `episodic_memory.py`) supports:
- Chunking long entries via semantic split.  
- Storing both whole entries and individual chunks in separate collections.  
- Reflective agents for summarization and retrieval.

Example usage mirrors `Journal` but writes to `whole_journal_entries` and `journal_chunks_table`.

---

## 6. Best Practices
- Choose clear `collection_id` values to avoid overlap across components.  
- Use metadata fields for rich filtering (`session_id`, `user_id`, `channel`).  
- Monitor collection size with `count_collection()`.  
- Leverage `mem.store` after queries for in‑memory access.
- When using memory in Cogs, specify appropriate `query_before` and `update_after` agents.
- For advanced control, interact directly with `mem.storage` (see [ChromaStorage Guide](ChromaStorage.md)).

---

## 7. Related Documentation
- [Cogs Guide](../Cogs/Cogs.md)  
- [ChromaStorage Guide](ChromaStorage.md)  
- [Storage Settings](../Settings/Storage.md)  
- [Agent Class API](../Agents/AgentClass.md) 