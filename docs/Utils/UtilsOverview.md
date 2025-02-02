# Utilities Overview

## Introduction

The **AgentForge** framework provides a suite of utility classes that facilitate various operations within agents and the system as a whole. These utilities are designed to be imported and used as needed, offering flexibility and modularity in your projects.

---

## Available Utilities

The utilities are located in the `.agentforge/utils/` directory and include the following:

### [1. Chroma Utils](ChromaUtils.md)

- **Description**: A class for interacting with the vector database **ChromaDB**. It provides methods for managing and using storage, enabling agents to store and retrieve data efficiently.
- **Use Cases**:
  - Data persistence and retrieval.
  - Implementing agent memory functionalities.

### [2. Discord Client](DiscordClient.md)

- **Description**: A class for connecting agents to Discord. It can be used to create Discord bots, allowing agents to interact with users through Discord channels.
- **Use Cases**:
  - Real-time communication with users. (Real-time is subjective as it depends on your unique implementation and LLM)
  - Building chatbots for Discord servers.
  - Integrating agents into Discord communities.

### [3. Logger](Logger.md)

- **Description**: Contains functions for logging to both files and the console, allowing for enhanced debugging and monitoring.
- **Use Cases**:
  - Debugging agent behaviors.
  - Tracking system activities.
  - Recording errors and important events.

### [4. Parsing Utils](ParsingUtils.md)

- **Description**: Provides methods for parsing formatted text into Python dictionaries.
- **Use Cases**:
  - Parsing agent responses formatted in **YAML**. (More Parsing Formats Coming Soon...ish)
  - Converting structured text data into usable Python objects.

### [5. Prompt Handling](PromptHandling.md)

- **Description**: Manages the rendering and handling of prompts that guide agent actions and responses.
- **Use Cases**:
  - Dynamically generating prompts with variable substitution.
  - Managing prompt templates.
  - Ensuring prompts are correctly formatted for the LLM.

### [6. Tool Utils](ToolUtils.md)

- **Description**: Facilitates the dynamic execution of tools, integral to performing actions within the system.
- **Use Cases**:
  - Managing and executing agent tools.
  - Integrating external functionalities.
  - Extending agent capabilities with custom actions.

---

## Using Utilities

You can import and utilize these utilities directly in your code as needed. Below is an example of how to use one of the utilities.

### Example: Using `ParsingUtils`

```python
from agentforge.utils.parsing_processor import ParsingProcessor

# Initialize the ParsingUtils class
parsing_utils = ParsingProcessor()

# Example YAML string
yaml_string = '''
name: AgentForge
description: An advanced agent framework.
'''

# Parse the YAML content
parsed_yaml = parsing_utils.parse_yaml_content(yaml_string)

# Output the parsed YAML
print(parsed_yaml)
```

**Output:**

```
{'name': 'AgentForge', 'description': 'An advanced agent framework.'}
```

In this example, we parse a **YAML**-formatted string into a Python dictionary using the `ParsingUtils` utility. This is particularly useful when processing agent responses or configuration data formatted in YAML.

---

## Notes

- **Modularity**: Each utility is designed to be independent and can be imported as needed without unnecessary overhead.
- **Flexibility**: Utilities can be combined to enhance agent functionalities and streamline development.
- **Documentation**: For detailed information on each utility, refer to their respective guides:
  - [Chroma Utils Guide](ChromaUtils.md)
  - [Discord Client Guide](DiscordClient.md)
  - [Logger Guide](Logger.md)
  - [ParsingUtils Guide](ParsingUtils.md)
  - [PromptHandling Guide](PromptHandling.md)
  - [ToolUtils Guide](ToolUtils.md)

---

## Conclusion

The utilities provided by **AgentForge** enhance the capabilities of your agents and simplify the development process. By leveraging these tools, you can build robust and feature-rich agents tailored to your specific needs.

---

**Need Help?**

If you have questions or need assistance, feel free to reach out:

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)

---