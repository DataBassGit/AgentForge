## **Storage YAML Documentation**

### **Overview**

The `storage.yaml` file manages the available storage options and their respective settings. It plays a pivotal role in configuring the system's storage mechanisms.
You can find this directory at `your_project_root/.agentforge/settings`

### **Formatting Guidelines**

- This file lists available storage options and a set of configurations for each.
- The `StorageAPI` attribute indicates the default storage option in use.

### **Sample Configuration**

```yaml
StorageAPI: ChromaDB

ChromaDB:
  chroma_db_impl: duckdb+parquet
  persist_directory: ./DB/ChromaDB
  collection_name: collection-test
  DBFreshStart: true
  embedding: all-distilroberta-v1

Pinecone:
  environment: us-east4-gcp
  index_name: test-table
  dimension: "768"
```

---