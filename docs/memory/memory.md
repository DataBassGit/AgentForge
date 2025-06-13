# Memory in AgentForge Cogs

Memory in AgentForge is designed to be used as part of a **Cog**—not as a standalone utility. Memory nodes are declared in your Cog YAML, managed by the `MemoryManager`, and made available to agents as part of the execution context. This enables agents to access, share, and update contextual information throughout a workflow.

---

## 1. How Memory Works in a Cog

- **Memory nodes** are defined in the `memory` section of your Cog YAML.
- The **MemoryManager** instantiates and manages all memory nodes for the Cog.
- Memory is **queried automatically before** and **updated after** specified agents, as configured in YAML.
- Agents access memory through the context provided by the Cog engine—typically via the `_mem` variable in prompt templates.

---

## 2. Example: Cog YAML with Memory

```yaml
cog:
  name: "ExampleCogWithMemory"
  description: "A sample decision workflow with memory."
  chat_memory_enabled: false # disables automatic chat history for this example

  agents:
    - id: analysis
      template_file: cog_analyze_agent
    - id: decision
      template_file: cog_decide_agent
    - id: response
      template_file: cog_response_agent

  memory:
    - id: general_memory
      query_before: analysis
      update_after: response
      query_keys: [user_input]
      update_keys: [user_input, response]

  flow:
    start: analysis
    transitions:
      analysis: decision
      decision:
        choice:
          "approve": response
          "reject": analysis
        fallback: response
        max_visits: 3
      response:
        end: true
```

- **query_before**: Memory is queried before the listed agent(s) run.
- **update_after**: Memory is updated after the listed agent(s) run.
- **query_keys**/**update_keys**: Specify which fields from the context/state are used for querying/updating memory.

> **Tip:** You do not need to instantiate memory classes directly—define them in YAML and let the Cog engine handle everything.

---

## 3. Example: Agent Prompt Template Usage

Agents access memory via the `_mem` context in their prompt templates. For example:

```yaml
prompts:
  system:
    intro: |
      You are an analysis agent. Your job is to extract key insights, user intent, and relevant topics from user messages.
      
    chat_history: |
      ## Chat History
      {_mem.chat_history.history}

    relevant_history: |
      ## Relevant Past Conversations
      {_mem.chat_history.relevant}

    scratchpad: |
      ## Scratchpad
      {_mem.scratchpad.readable}
      
    persona_context: |
      ## Current Persona Understanding
      {_mem.persona_memory._narrative}
      
  user:
    analysis_task: |
      ## User Message to Analyze
      {_ctx}
```

- `{_mem.<node_id>.readable}`: Human-readable summary of memory node if available.
- `{_mem.persona_memory._narrative}`: Narrative summary from PersonaMemory.
- `{_mem.chat_history.history}`: Recent chat turns (recency slice).
- `{_mem.chat_history.relevant}`: Semantically relevant past messages (semantic slice, if enabled).

The `_mem` variable is automatically constructed by the Cog engine and contains all memory nodes defined in your YAML (plus `chat_history` if enabled).

---

## 4. MemoryManager and Execution Flow

- The `MemoryManager` is created automatically for each Cog and manages all memory nodes.
- It ensures memory is queried/updated at the right points in the workflow, based on your YAML configuration.
- Agents never interact with memory nodes directly—they receive memory context via `_mem` in their prompt templates.
- Direct instantiation of memory classes is rare and not recommended; always use Cog YAML for configuration.

---

## 5. Types of Memory Nodes

AgentForge currently ships with the following memory node types:

- **Memory** (base): General-purpose vector memory for storing and retrieving context data.
- **PersonaMemory**: Specialized memory for managing persona-related facts and generating dynamic persona narratives ([see persona_memory.md](persona_memory.md)).
- **ChatHistoryMemory**: Automatically manages chat history for a Cog, providing recent conversation context to agents. This node is added automatically unless disabled.
- **ScratchPad**: A memory node for maintaining a working scratchpad or notes, with support for log consolidation.

> **Note:** Additional memory types may be released in the future as the framework evolves.

---

## 6. Best Practices for Cog-Based Memory

- Always define memory nodes in your Cog YAML, not in code.
- Use `query_before` and `update_after` to control when memory is accessed.
- Use clear, descriptive `id` values for each memory node.
- Leverage `{_mem.<node_id>.readable}` or other context keys in your prompt templates for agent access.
- Use the automatic `chat_history` node for conversation context unless you have a specific reason to disable it.
- For advanced use, see the [PersonaMemory documentation](persona_memory.md) and class docstrings for each memory type.

---

## 7. Related Documentation
- [Cog Guide](../cogs/cogs.md)
- [PersonaMemory](persona_memory.md)
- [Prompt Template Examples](../../src/agentforge/setup_files/prompts/)