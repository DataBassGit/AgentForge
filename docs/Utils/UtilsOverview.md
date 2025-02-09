# Utilities Overview

## Introduction

In **AgentForge**, various utility classes make building and extending agents easier. Each utility focuses on a specific aspect of agent functionality—handling everything from logging, prompt rendering, and parsing structured data, to dynamic tool execution, and Discord integration.

---

## Available Utilities

The core utility modules (found under `agentforge/utils/`) are summarized below. For more details on each, see the linked individual guides.

### **1. Discord Client**

- **Guide**: [Discord Guide](DiscordClient.md)
- **Description**: A class for connecting agents to Discord. It can create Discord bots, allowing agents to receive and send messages in channels, post embeds, manage threads, and more.
- **Use Cases**:
  - Building real-time chat interfaces for your agents on Discord servers.
  - Enabling interactive command-based bots or multi-agent discussions in a community.

---

### **2. Logger**

- **Guide**: [Logger Guide](Logger.md)
- **Description**: A robust logging system to track agent actions, debug processes, and store audit trails. Logs can be split across multiple files with configurable levels, and dynamic creation of new log files.
- **Use Cases**:
  - Debugging behaviors in custom agents.
  - Monitoring system health, errors, and warnings.
  - Maintaining detailed logs for compliance or review.

---

### **3. Parsing**

- **Guide**: [ParsingUtils Guide](ParsingUtils.md)
- **Description**: Provides methods for extracting code blocks and parsing common data formats, including YAML, JSON, XML, INI, CSV, and Markdown. Useful when agents embed structured information in their outputs or require configuration data from text.
- **Use Cases**:
  - Parsing agent responses that include code-fenced JSON or YAML.
  - Converting user-supplied text into Python data structures for further processing.

---

### **4. Prompt Handling**

- **Guide**: [PromptHandling Guide](PromptHandling.md)
- **Description**: Manages the rendering and validation of prompt templates that guide agent behaviors. Substitutes placeholders (`{var_name}`) with actual data, checks formatting, and ensures non-empty results.
- **Use Cases**:
  - Dynamically generating prompts based on user input or agent context.
  - Maintaining multi-section prompts (like system vs. user) without manual string concatenation.
  - Overriding default prompt rendering logic for advanced customization.

---

### **5. Tool Utils**

- **Guide**: [ToolUtils Guide](ToolUtils.md)
- **Description**: Facilitates on-the-fly importing and execution of tool modules or built-in functions, plus formatting those tools for display. Enables flexible, pluggable functionality so agents can call new or external code.
- **Use Cases**:
  - Letting agents choose from multiple “actions” at runtime, referencing user-defined modules.
  - Dynamically expanding an agent’s capabilities without redeploying the entire application.

---

## Notes

1. **Modularity**  
   Each utility is standalone—import only what you need, where you need it.  
2. **Extendibility**  
   If you have specialized requirements (e.g., advanced prompt placeholders), you can override or subclass these utilities.  
3. **Documentation**  
   Each utility has its own dedicated guide detailing methods, usage examples, and common pitfalls.

---

## Conclusion

These **AgentForge** utilities provide foundational functionality to handle everything from logs and prompts to Discord interactions and tool execution. By combining them, you can create more intelligent, modular, and maintainable agents that adapt to various scenarios.

**Need Help?**
- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)  
- **Discord**: [Join our Discord Server](https://discord.gg/ttpXHUtCW6)
