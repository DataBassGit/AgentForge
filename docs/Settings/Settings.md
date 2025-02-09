# Settings Overview

Welcome to the configuration guide for **AgentForge**. This document provides a high-level look at how settings are organized and managed within the framework. For most developers, it’s enough to know where the main configuration files live, how they interact, and how to override specific settings when needed. Deeper details about each file can be found in their respective guides.

---

## How AgentForge Loads Configurations

All configuration data—covering system behavior, model defaults, and storage settings—is managed by a singleton `Config` class. When you instantiate an agent, **AgentForge**:

1. **Finds the `.agentforge/settings` Directory**  
   Looks for configuration files in your project root (or a custom root, if you specify one).  

2. **Loads Each YAML File**  
   Merges the contents of `system.yaml`, `models.yaml`, and `storage.yaml` into one big dictionary.  

3. **Makes Settings Available to Agents**  
   Any agent you create can access the merged settings via `agent_data['settings']`. 

This structure allows you to separate concerns: **system**-level flags go in `system.yaml`, **model** details go in `models.yaml`, and **storage** specifics go in `storage.yaml`.

---

## The Main Configuration Files

### 1. `system.yaml`

**Purpose**: Controls high-level framework options such as persona handling, logging, debug flags, and miscellaneous settings.

**Key Sections**:
- **`persona`**: Determines if personas are enabled, plus a default persona name.  
- **`debug`**: Toggles debug mode and sets whether to simulate LLM responses.  
- **`logging`**: Controls whether logging is enabled, log levels, and log file destinations.  
- **`misc`**: Houses on-the-fly toggles, file paths, or other system-related flags.

**Detailed Reference**: See the [System Settings Guide](System.md).

---

### 2. `models.yaml`

**Purpose**: Defines which model(s) are available and how they’re configured (APIs, model identifiers, default parameters, etc.).

**Key Sections**:
- **`default_model`**: Picks which API and model name each agent uses by default, unless it specifies an override.  
- **`model_library`**: Contains detailed info for each API/class pair and the specific models they support.  
- **`embedding_library`**: Ties in optional embedding models for tasks like vector storage.

Agents can override these defaults by specifying `model_overrides` in their own YAML files. That override mechanism merges parameters from the global library with agent-level customizations.

**Detailed Reference**: Check out the [Model Settings Guide](Models.md).

---

### 3. `storage.yaml`

**Purpose**: Manages how agents store and retrieve data (vector databases, memory saving, timestamps, etc.).

**Key Sections**:
- **`options`**: Determines whether storage is enabled, memory saving is active, and how timestamps are handled.  
- **`embedding`**: Chooses which embedding to use for data indexing (e.g., `distil_roberta`).  
- **`embedding_library`**: Maps named embeddings (like `distil_roberta`) to the actual models in use (e.g., `all-distilroberta-v1`).

This separation helps you tweak storage parameters independently from system or model settings.

**Detailed Reference**: See the [Storage Settings Guide](Storage.md).

---

## Accessing Settings in Your Agents

When an agent is instantiated, **AgentForge** merges all these settings into `agent_data['settings']`. For instance:

```python
class MyAgent(Agent):
    def process_data(self):
        system_settings = self.agent_data['settings']['system']
        model_defaults = self.agent_data['settings']['models']['default_model']
        storage_options = self.agent_data['settings']['storage']['options']

        # Now do something with system, model, or storage settings...
```

Beyond reading them, you can also specify overrides in an agent’s own YAML if you need certain models or parameters.

---

## On-the-Fly Reloading

If `misc.on_the_fly` in `system.yaml` is set to `true`, **AgentForge** will check for updates to your YAML files at runtime. That means you can update prompts, model parameters, or system flags without having to restart your entire application—a big help during rapid prototyping.

---

## Best Practices

- **Keep Each File Focused**  
  System-wide flags go in `system.yaml`, model info in `models.yaml`, and data storage preferences in `storage.yaml`. This makes changes easier to track.  
- **Use Default Models Wisely**  
  Rely on `default_model` in `models.yaml` when you can, and only override it in an agent’s own YAML if there’s a real need for variation.  
- **Debug Mode**  
  If you’re iterating fast, set `debug.mode` to `true` in `system.yaml` so your agent can use a mocked LLM response without incurring real API calls.  
- **Test Storage**  
  If you enable `storage.options.enabled`, confirm your embedding model and path are set correctly.  

---

## Conclusion

**AgentForge** splits its configuration across three main files (`system.yaml`, `models.yaml`, and `storage.yaml`) to give you a clean, modular way to manage your AI infrastructure. Whether you need to adjust logging levels, define new LLMs, or control how data is persisted, these files provide straightforward handles for each concern.

For a deeper dive, check out the individual guides:

- [System Settings Guide](System.md)  
- [Model Settings Guide](Models.md)  
- [Storage Settings Guide](Storage.md)
- [Personas Guide](../Personas/Personas.md)

---

**Need Help?**

If you have questions or need assistance, feel free to reach out:

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)  
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)
