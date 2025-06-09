# Storage Settings Guide

> **Important:** Storage in AgentForge is managed by cogs through their memory nodes. Individual agents do not directly interact with storage. This design simplifies the architecture and centralizes memory management.

`storage.yaml` is loaded from the project's `.agentforge/settings/storage.yaml` and merged into `Config().data['settings']['storage']`.

## Location

```
<project_root>/.agentforge/settings/storage.yaml
```

## Schema Overview

```yaml
options:
  enabled: true         # Enable or disable storage operations
  save_memory: true     # Persist memory (requires enabled=true)
  iso_timestamp: true   # Include ISO 8601 timestamps in stored records
  unix_timestamp: true  # Include Unix epoch timestamps in stored records
  persist_directory: ./db/ChromaDB  # Path for storage files, relative to project root
  fresh_start: false    # Wipe existing storage on initialization if true (useful for testing)

embedding:
  selected: distil_roberta  # Key from embedding_library to use for vector encoding

embedding_library:
  distil_roberta: all-distilroberta-v1
  all_mini: all-MiniLM-L6-v2
  openai_ada2: text-embedding-ada-002
```

### options

- **enabled** (bool): Toggle storage on or off globally. Default `true`.
- **save_memory** (bool): When `true`, cogs save memory to storage. Only effective if `enabled` is also `true`.
- **iso_timestamp** (bool): Add ISO 8601 timestamps (e.g., `2025-02-08T14:30:00Z`) to stored entries.
- **unix_timestamp** (bool): Add Unix epoch timestamps to stored entries.
- **persist_directory** (string): Folder path (relative to project root) where the vector DB or storage files reside.
- **fresh_start** (bool): When `true`, clears existing storage at startup (useful for testing, avoid in production).

### embedding

- **selected** (string): Chooses an embedding key defined under `embedding_library`. Default `distil_roberta`.

### embedding_library

- **Mapping** `map[string,string]`: Defines named embeddings to actual model identifiers (e.g., `"distil_roberta": "all-distilroberta-v1"`).

## Dynamic `storage_id` Resolution

AgentForge uses a `storage_id` to partition storage contexts (e.g., per persona or cog). `Memory` modules used by cogs derive `storage_id` as follows:

- If a persona is set, the persona name is used as the storage ID.
- Otherwise, the cog name is used.
- If neither is set, `'fallback_storage'` is used.

Example usage:

```python
from agentforge.storage.memory import Memory
# Internally:
resolved_id = Memory._resolve_storage_id()
# Used to create or retrieve storage context:
storage = ChromaStorage.get_or_create(storage_id=resolved_id)
```

Custom storage instances can be created with:

```python
from agentforge.storage.chroma_storage import ChromaStorage
storage = ChromaStorage.get_or_create(storage_id="my_custom_id")
```

## Accessing Storage Settings in Code

```python
from agentforge.config import Config
storage_settings = Config().data['settings']['storage']
options  = storage_settings['options']
embed    = storage_settings['embedding']
library  = storage_settings['embedding_library']
```

## Related Guides

- [Settings Overview](settings.md)
- [System Settings Guide](system.md)
- [Model Settings Guide](models.md)
