# `Config` Class

---

## Overview

The `Config` class plays a pivotal role in the system, orchestrating the seamless management and handling of all essential settings. It fetches its configurations from the `config.json` file located in the `/.agentforge/` directory. Designed as a Singleton, this class ensures that only one instance is created and utilized throughout the system's lifecycle.

---

## Class Attributes

- **_instance**: An attribute that holds the single instance of the `Config` class, ensuring the Singleton pattern.
- **config_path**: The path to the configuration directory. Defaults to the environment variable `AGENTFORGE_CONFIG_PATH` or `.agentforge` if not set.
- **data**: A dictionary that contains the configuration data loaded from the `config.json` file.
- **persona, actions, agent, tools**: Attributes for specific configuration data subsets, populated from their respective `JSON` files.

## Initialization:

The `Config` class leverages the `__new__` method to implement the Singleton pattern. This ensures that only one instance of the `Config` class is created, even if multiple instantiation attempts are made.

Within the `__init__` method, the path to the configuration directory is determined, defaulting to the `.agentforge` directory unless overridden by the `AGENTFORGE_CONFIG_PATH` environment variable.

After initializing its attributes, the class invokes the `load()` method. This method loads the configuration data from the respective `JSON` files into the appropriate class attributes.

```python
import importlib
import json
import os
import pathlib

class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
            cls._instance.__init__()
        return cls._instance

    def __init__(self, config_path=None):
        self.config_path = config_path or os.environ.get("AGENTFORGE_CONFIG_PATH", ".agentforge")
        self.data = {}
        self.persona = {}
        self.actions = {}
        self.agent = {}
        self.tools = {}
        self.load()
```

---

Certainly! Let's set it up following your format:

---

## Data Attribute - `config.json`

For a comprehensive understanding of the attributes and settings contained within the `config.json` file, refer to the dedicated [**Config JSON File Documentation**](ConfigJson.md).

---

## Persona Attribute - `persona.json`

To delve into the configurations that manage the system's behavior and interactions, determining its persona, check out the [**Personas Documentation**](../Personas/Personas.md).

>**Important Note:** No documentation exists for personas yet as it has not been implemented yet!

---

## Agent Prompts Configuration

Each agent in the system has its own dedicated `JSON` file that dictates its prompt templates. This file is essential for guiding the agent's behavior and interactions. It's vital to note that the name of this `JSON` file directly corresponds to the agent class name and is case-sensitive. For example, an agent class named `ExecutionAgent` would have its prompt configurations in a `JSON` file named `ExecutionAgent.json`.

For in-depth details regarding the configurations specific to different agents, please refer to the [**Agent Prompts Documentation**](../Agents/Prompts/AgentPrompts.md).

---

## Actions & Tools Attributes - `actions.json` & `tools.json`

Detailed information about configurations concerning actions and tools, and how they interact within the system, can be found in the [**Actions & Tools Documentation**](../Tools&Actions/ToolsActions.md).

---

# Overriding Default LLM Configurations

For specialized tasks or requirements, each agent in the system can autonomously override the default LLM (Large Language Model) configurations that are set in the `config.json` file. This capability ensures that agents can operate with specific models or parameters that are best suited for their individual roles.

To understand the format and usage of overriding defaults for agents, refer to the [**Overriding Default Configurations Documentation**](./OverridingConfig.md).

---