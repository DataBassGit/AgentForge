# ChatHistoryMemory

The `ChatHistoryMemory` class provides automatic, workflow-integrated chat history for Cogs in AgentForge. It enables agents to access recent conversation turns, supporting context-aware responses and multi-turn workflows.

---

## Overview

- **ChatHistoryMemory** is automatically added to every Cog unless explicitly disabled in the YAML config.
- It stores recent user and agent messages, making them available to all agents in the workflow.
- Agents access chat history through the `_mem.chat_history` context in their prompt templates.
- No manual instantiation or direct code usage is required—just configure your Cog YAML as needed.

---

## Configuration

### Enabling/Disabling Chat History

By default, chat history is enabled for every Cog. To disable it, set `chat_memory_enabled: false` at the top level of your Cog YAML:

```yaml
cog:
  name: "NoChatHistoryExample"
  chat_memory_enabled: false
  ...
```

### Configuring Number of Results

You can control how many recent messages are included in the chat history context with `chat_history_max_results`:

```yaml
cog:
  name: "CustomChatHistoryExample"
  chat_history_max_results: 20  # Default is 10; 0 means no limit
  ...
```

> **Note:** You do **not** need to define a `chat_history` memory node in your YAML. It is managed automatically by the framework.

---

## Example: Cog YAML with Chat History

```yaml
cog:
  name: "ChatHistoryMemoryExample"
  description: "Example workflow demonstrating ChatHistoryMemory functionality"
  # chat_memory_enabled: false  # Optional: disable chat history
  # chat_history_max_results: 20  # Optional: set max results

  agents:
    - id: understanding
      template_file: understand_agent
    - id: response
      template_file: response_agent

  # No explicit memory section needed for chat history if enabled

  flow:
    start: understanding
    transitions:
      understanding: response
      response:
        end: true
```

---

## Example: Agent Prompt Template Usage

Agents access chat history in their prompt templates using the `_mem.chat_history` context. For example:

```yaml
prompts:
  system:
    chat_history: |
      ## Chat History
      {_mem.chat_history.history}
```

- `{_mem.chat_history.history}`: Renders a human-readable summary of recent conversation turns.

You can combine chat history with other memory nodes in your prompts for richer context.

---

## How It Works

- The `MemoryManager` automatically creates and manages the `chat_history` node for each Cog (unless disabled).
- After each agent execution, the latest user and agent messages are recorded in chat history.
- When an agent runs, the most recent N messages (as configured) are loaded into the `_mem.chat_history` context.
- Agents never interact with chat history directly; they only access it via the prompt context.

---

## Best Practices

- Use chat history in your agent prompts to provide context for multi-turn conversations.
- Adjust `chat_history_max_results` to balance context richness and prompt length.
- Disable chat history only if your workflow does not require prior conversation context.
- Combine chat history with other memory nodes (e.g., PersonaMemory, ScratchPad) for advanced workflows.

---

## Related Documentation
- [Memory in Cogs](memory.md)
- [Cog Guide](../cogs/cogs.md)
- [Prompt Template Examples](../setup_files/prompts/) 