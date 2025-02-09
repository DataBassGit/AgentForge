# Storage Settings Guide

The `storage.yaml` file controls how **AgentForge** persists and retrieves data, including memory saving, embedding choices, and optional fresh starts for the storage backend. By fine-tuning these settings, you can dictate how agents store and recall data within your AI workflows.

---

## Location

```
your_project_root/.agentforge/settings/storage.yaml
```

---

## Default Structure

A typical `storage.yaml` might look like this:

```yaml
# Default storage settings for all agents unless overridden
options:
  enabled: true
  save_memory: true
  iso_timestamp: true
  unix_timestamp: true
  persist_directory: ./db/ChromaDB
  fresh_start: false

# Selected Embedding
embedding:
  selected: distil_roberta

# Embedding library (mapping of embeddings to their identifiers)
embedding_library:
  distil_roberta: all-distilroberta-v1
  all_mini: all-MiniLM-L6-v2
```

In the **AgentForge** framework, this data is loaded at runtime and made available to agents via `agent_data['settings']['storage']`.

---

## Key Sections

### 1. `options`

```yaml
options:
  enabled: true
  save_memory: true
  iso_timestamp: true
  unix_timestamp: true
  persist_directory: ./db/ChromaDB
  fresh_start: false
```

- **`enabled`**  
  - **Type**: Boolean  
  - **Description**: Determines if storage is active. When `false`, agents will not attempt to read/write from the storage backend.  

- **`save_memory`**  
  - **Type**: Boolean  
  - **Description**: If `true`, agents that collect conversational memory or other data can save that information to the storage system. This only works if `enabled` is also `true`.  

- **Timestamps**  
  - **`iso_timestamp`**: If `true`, stored data includes ISO 8601 timestamps (e.g., `2025-02-08T14:30:00Z`).  
  - **`unix_timestamp`**: If `true`, stored data includes a Unix timestamp. You can enable either, both or none.  

- **`persist_directory`**  
  - **Type**: String  
  - **Description**: The folder path (relative to project root) where the vector database or other persistent storage files are kept.  
  - **Default**: `./db/ChromaDB`  

- **`fresh_start`**  
  - **Type**: Boolean  
  - **Description**: If `true`, the system wipes out the existing storage contents at startup. Useful for local testing but not recommended in production scenarios.  

---

### 2. `embedding`

```yaml
embedding:
  selected: distil_roberta
```

- **`selected`**  
  - **Type**: String  
  - **Description**: Identifies which embedding model to use for vector-based operations.  
  - **Default**: `distil_roberta` (as shown in the example).  

This key is typically leveraged when agents store or query vector data in the configured database. The actual mapping from `distil_roberta` to a model identifier is defined under `embedding_library`.

---

### 3. `embedding_library`

```yaml
embedding_library:
  distil_roberta: all-distilroberta-v1
  all_mini: all-MiniLM-L6-v2
```

- **Purpose**: Maps named embeddings (e.g., `distil_roberta`) to the actual embedding model or pipeline (`all-distilroberta-v1`).  
- **Usage**: If your system or agent references `distil_roberta`, AgentForge will translate it into the `all-distilroberta-v1` embedding. You can add or rename entries here to point to different huggingface or custom embeddings.

---

## Overriding Storage Settings in Agents

Most agents use the global storage settings, but you can override them for specific agents if necessary. For example, an agent might specify a separate directory or disable memory saving. You would typically do this under the agent’s own YAML with a section like:

```yaml
storage_overrides:
  enabled: false
  save_memory: false
  persist_directory: ./db/CustomAgentDB
```

Depending on how your code merges agent-level overrides, you may see them at `self.agent_data['settings']['storage']` within your agent’s methods.

---

## Practical Usage in Agents

Here’s an example of how an agent might conditionally store data:

```python
from agentforge.agent import Agent

class MemoryAgent(Agent):
    def save_to_storage(self):
        # Check if storage is enabled and memory saving is allowed
        storage_opts = self.agent_data['settings']['storage']['options']
        if storage_opts['enabled'] and storage_opts['save_memory']:
            # Perform your vector database writes or other I/O
            self.logger.log("Storing data to vector DB...", "info", "agentforge")
            # Example: self.agent_data['storage'].save_memory(...)
        else:
            self.logger.log("Storage is disabled. Skipping save...", "warning", "agentforge")
```

With this approach, you can dynamically determine whether to save interaction data based on the user’s overarching configuration.

---

## Best Practices

1. **Disable `fresh_start` in Production**  
   You don’t want to wipe your storage each time the system restarts.  
2. **Check `enabled`**  
   If you have an agent relying on memory, ensure storage is turned on.  
3. **Embedding Consistency**  
   Keep the `embedding.selected` consistent across agents that need to query the same vector store. Otherwise, embedding mismatch can lead to suboptimal results or errors.  
4. **Timestamps**  
   Use ISO or Unix timestamps if you need a consistent audit trail or chronological ordering.  

---

## Conclusion

`storage.yaml` centralizes your approach to storing agent data, from toggling memory writes to selecting embeddings. By fine-tuning these fields, you can adapt **AgentForge** to everything from lightweight ephemeral data needs to robust, persistent vector databases for advanced retrieval.

For more insights into how these storage settings interact with the rest of the framework, check out:

- [Settings Overview](Settings.md)
- [System Settings Guide](System.md)  
- [Model Settings Guide](Models.md)  
- [Personas Guide](../Personas/Personas.md)

---

**Need Help?**

If you have questions or need assistance, feel free to reach out:

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)  
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)
