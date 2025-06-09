# Utilities Overview

## Introduction

In **AgentForge**, utility classes make building and extending agents easier. Each utility focuses on a specific aspect of agent functionality—handling everything from logging, prompt rendering, and parsing structured data and Discord integration.

---

## Available Utilities

The core utility modules (found under `agentforge/utils/`) are summarized below. For more details on each, see the linked individual guides.

### **1. Discord Client**

- **Guide**: [Discord Guide](discord_client.md)
- **Description**: Connects agents to Discord, enabling bots to send/receive messages, post embeds, manage threads, and more.
- **Use Cases**:
  - Building real-time chat interfaces for agents on Discord servers.
  - Enabling interactive command-based bots or multi-agent discussions.

---

### **2. Logger**

- **Guide**: [Logger Guide](logger.md)
- **Description**: A robust logging system to track agent actions, debug processes, and store audit trails. Supports multiple log files and configurable levels.
- **Use Cases**:
  - Debugging agent behaviors.
  - Monitoring system health, errors, and warnings.
  - Maintaining detailed logs for compliance or review.

---

### **3. Parsing**

- **Guide**: [ParsingUtils Guide](parsing_utils.md)
- **Description**: Methods for extracting code blocks and parsing common data formats (YAML, JSON, XML, INI, CSV, Markdown). Useful for agents that embed structured information in outputs or require configuration data from text.
- **Use Cases**:
  - Parsing agent responses that include code-fenced JSON or YAML.
  - Converting user-supplied text into Python data structures.

---

### **4. Prompt Handling**

- **Guide**: [PromptHandling Guide](prompt_handling.md)
- **Description**: Manages the rendering and validation of prompt templates. Substitutes placeholders (`{var_name}`) with actual data, checks formatting, and ensures non-empty results.
- **Use Cases**:
  - Dynamically generating prompts based on user input or agent context.
  - Maintaining multi-section prompts (like system vs. user) without manual string concatenation.
  - Overriding default prompt rendering logic for advanced customization.

---

### **5. Tool Utils**

# ⚠️ DEPRECATION WARNING

**The Tools system is DEPRECATED.**

Do NOT use in production or with untrusted input. This system will be replaced in a future version with a secure implementation based on the MCP standard.

See: https://github.com/DataBassGit/AgentForge/issues/116 for details.

- **Guide**: [ToolUtils Guide](tool_utils.md)
- **Description**: Facilitates dynamic importing and execution of tool modules or built-in functions, plus formatting those tools for display. Enables flexible, pluggable functionality so agents can call new or external code.
- **Use Cases**:
  - Letting agents choose from multiple "actions" at runtime, referencing user-defined modules.
  - Dynamically expanding an agent's capabilities without redeploying the entire application.

---

## Notes

1. **Modularity**  
   Each utility is standalone—import only what you need, where you need it.  
2. **Extendibility**  
   If you have specialized requirements (e.g., advanced prompt placeholders), you can override or subclass these utilities.  
3. **Documentation**  
   Each utility is documented in its own guide. Refer to those guides for up-to-date usage and best practices.

---

## Conclusion

These **AgentForge** utilities provide foundational functionality to handle everything from logs and prompts to Discord interactions and tool execution. By combining them, you can create more intelligent, modular, and maintainable agents that adapt to various scenarios.

**Need Help?**
- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)  
- **Discord**: [Join our Discord Server](https://discord.gg/ttpXHUtCW6)
