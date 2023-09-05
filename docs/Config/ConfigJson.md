# `config.json` Attributes

The `config.json` file serves as the primary configuration source for the system. It encompasses various settings that dictate the system's behavior, ensuring it operates efficiently and tailors its responses accurately. Below is a breakdown of the attributes within this file:



---
# Overriding Default LLM Configurations

For specialized tasks or requirements, each agent in the system can autonomously override the default LLM (Large Language Model) configurations that are set in the `config.json` file. This capability ensures that agents can operate with specific models or parameters that are best suited for their individual roles.

To understand the format and usage of overriding defaults for agents, refer to the [**Overriding Default Configurations Documentation**](./OverridingConfig.md).

---
>**Note**: The breakdown below represents a sample configuration. The actual settings might vary based on user needs and system requirements.
---

## 1. **Persona**

- **selected**: The selected persona for the system, determining the system's behavior and interactions.

Example:
```json
"Persona" : {
    "selected" : "persona"
}
```

---

## 2. **Objective**

Specifies the primary goal or objective of the system.

Example:
```json
"Objective": "Build a web scraping script"
```

---

## 3. **Storage**

The `Storage` attribute represents the memory collections in the database, specifically ChromaDB in this setup. Each key inside the `Storage` attribute denotes a distinct memory collection that the bot can access. Some collections, like `Tasks`, can be preloaded with data as shown in the example. Others, such as `Results`, `Tools`, and `Actions`, merely indicate the bot's request to create an empty collection in the database, reserved for future data storage.

It's essential to understand that these collections serve as the bot's memory repositories. As the bot operates, it can read from and write to these collections, making them crucial for its ongoing tasks and functions.

**Example:**
```json
"Storage": {
    "Tasks": ["Task 1", "Task 2", "Task 3"],
    "Results": "",
    "Tools": "",
    "Actions": ""
}
```

---

## 4. **ChromaDB**

Configurations related to the ChromaDB database.

- **chroma_db_impl**: The database implementation type.
- **persist_directory**: Directory where the database is persisted.
- **collection_name**: Name of the database collection.
- **DBFreshStart**: A flag to indicate if the database should start afresh, can be set to `false` to start with the memory from a previous run.
- **embedding**: Embedding type used.

Example:
```json
"ChromaDB" : {
    "chroma_db_impl" : "duckdb+parquet",
    "persist_directory" : "./DB/ChromaDB",
    "collection_name" : "collection-test",
    "DBFreshStart" : "True",
    "embedding" : "all-distilroberta-v1"
}
```

---

## 5. **EmbeddingLibrary**

- **library**: The library used for embeddings.

Example:
```json
"EmbeddingLibrary" : {
    "library" : "sentence_transformers"
}
```

---

## 6. **LanguageModelAPI**

The configurations related to the language model APIs.

- **library**: Primary library for the language model.
- **oobabooga, oobaboogaV2**: Other available APIs.

Example:
```json
"LanguageModelAPI" : {
    "library" : "openai_api",
    "oobabooga" : "oobabooga_api",
    "oobaboogaV2" : "oobabooga_v2_api"
}
```

---

## 7. **ModelLibrary**

Configurations concerning the language models.

- **claude**: The Claude model version.
- **fast_model**: Model optimized for speed.
- **smart_model**: Model optimized for intelligence.

Example:
```json
"ModelLibrary" : {
    "claude" : "claude-2",
    "fast_model" : "gpt-3.5-turbo-0613",
    "smart_model" : "gpt-4"
}
```

---

## 8. **StorageAPI**

- **selected**: Specifies the selected storage API.

Example:
```json
"StorageAPI" : {
    "selected" : "chroma"
}
```

---

## 9. **Pinecone**

Configuration related to the Pinecone settings.

- **environment**: Specifies the environment.
- **index_name**: Name of the index.
- **dimension**: Dimension settings.

Example:
```json
"Pinecone" : {
    "environment" : "us-east4-gcp",
    "index_name" : "test-table",
    "dimension" : "768"
}
```

---

## 10. **Defaults**

The `Defaults` attribute sets the primary configurations that will be employed throughout the system. Unless specific agents override these settings, the system will rely on these defaults for its operations.

- **API**: Specifies the default API to be used.
- **Model**: Determines the default model for the system.
- **Params**: Contains the set of parameters tailored for the chosen default model.

> **Note**: The parameters depend on the specific model being used. However, they can coexist together within the configuration, as each API implementation will only use the parameters it requires, ignoring any extras. It's crucial to refer to the specific model's API documentation for the required parameters. Currently, the configuration is set up with all necessary parameters for both OpenAI and Claude.

Example:
```json
"Defaults" : {
    "API" : "claude_api",
    "Model": "claude",
    "Params": {
      // ... model parameters ...
    }
}
```


