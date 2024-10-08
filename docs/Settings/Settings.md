# Settings Overview

Welcome to the configuration guide for **AgentForge**. Here, you'll interact with **YAML** files designed for ease of use and readability. This guide will help you navigate and customize the various configuration settings of the system.

---

## Configuration Management in AgentForge

While the framework's configurations are centrally managed by an internal `Config` class, as a developer, you don't need to interact with it directly. Instead, you can focus on configuring settings that impact your agents and their interactions with Large Language Models (LLMs).

**Key Point**: All settings (models and system) are parsed and made available to each agent through the `agent_data['settings']` variable. This allows your agents to access configuration settings as needed.

For more information on how agents work and how they utilize `agent_data`, please refer to the [Agents Documentation](../Agents/Agents.md).

---

## Models

Configure the Large Language Models (LLMs) used by your agents. This section provides detailed information about:

- Available models and their configurations.
- Default parameters and how to customize them.
- Instructions on setting up API keys and endpoints.

[**Learn more about configuring models ›**](Models.md)

---

## System

Adjust general system configurations and logging settings. This section covers:

- Paths for system agents and other global settings.
- Storage settings.
- Logging levels and formats.
- Miscellaneous system-wide configurations.

[**Learn more about system settings ›**](System.md)

---

## Accessing Settings Within Agents

All the settings from the `Models` and `System` configurations are available to your agents through the `agent_data['settings']` variable. This means you can access and utilize these settings directly within your custom agents.

**Example Usage in an Agent**:

```python
class MyCustomAgent(Agent):
    def load_additional_data(self):
        # Accessing model settings
        model_settings = self.agent_data['settings']['models']
        
        # Accessing system settings
        system_settings = self.agent_data['settings']['system']
        
        # Use the settings as needed
        model_name = model_settings['ModelSettings']['Model']
```

**Note**: For more information on how to work with agent variables and `agent_data`, please refer to the [Agent Methods Guide](../Agents/AgentMethods.md).

---

**Need Help?**

If you have questions or need assistance, feel free to reach out:

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)

---