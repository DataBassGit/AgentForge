# Settings Overview

Welcome to the settings documentation for the system. Our system utilizes `YAML` files for configurations due to their ease of parsing and human-readable nature. This overview provides a brief introduction to what each file entails and directs you to its detailed documentation.

---

## 1. **Directives (`directives.yaml`)**

The `directives.yaml` file houses hard-coded information that the entire system should have access to. Essentially, they're directives, instructions or simply any information meant to guide the system's behavior. The directives can be diverse, but they must adhere to Python's variable naming conventions.

[Directives Documentation](./Directives.md)

---

## 2. **Memories (`memories.yaml`)**

This file serves the purpose of initializing memory collections and pre-loading them with data, if necessary. Memory collections act as the system's repositories, crucial for ongoing tasks and functions.

[Memories Documentation](./Memories.md)

---

## 3. **Models (`models.yaml`)**

Dedicated to the settings of Large Language Models (LLM). It encompasses a list of available models and a set of default parameters. Individual agents can override these parameters when needed.

[Models Documentation](./Models.md)

---

## 4. **Paths (`paths.yaml`)**

Simply put, it's your directory guide. The `paths.yaml` file lays out the directory paths that the system can read and write from. A path signifies where specific files or data are stored and retrieved.

[Paths Documentation](./Paths.md)

---

## 5. **Storage (`storage.yaml`)**

Every system needs storage, and this file chalks out the storage game plan. It defines available storage options and their respective settings. Additionally, it specifies which storage API should be the default for operations.

[Storage Documentation](./Storage.md)

---

Navigate to the detailed documentation for a deep dive into each setting's intricacies and functionalities. Happy configuring!

---