# ScratchPad Memory

The `ScratchPad` memory node provides a collaborative, agent-accessible scratchpad for working notes, intermediate results, or running summaries within a Cog workflow. It is designed for iterative, multi-step processes where agents need to accumulate, reference, or consolidate information over time.

---

## Overview

- **ScratchPad** is a memory node type you can add to any Cog via the YAML `memory` section.
- It maintains two collections: a main scratchpad (consolidated note) and a log (raw entries before consolidation).
- When the log reaches a certain threshold (typically 10 entries), it can automatically consolidate entries into the main pad and clear the log.
- Agents access the scratchpad through the `_mem.scratchpad` context in their prompt templates.
- No manual instantiation or direct code usage is required—just configure your Cog YAML as needed.

---

## Configuration

### Adding a ScratchPad Node

Add a `ScratchPad` node to your Cog YAML like this:

```yaml
cog:
  name: "ScratchPadExample"
  ...
  memory:
    - id: scratchpad
      type: agentforge.storage.scratchpad.ScratchPad
      collection_id: scratchpad
      query_before: [analysis, response]  # Query before these agents run
      update_after: [analysis, response]  # Update after these agents run
      query_keys: [user_input]            # Use user input as context for queries
      update_keys: [user_input, response] # What to potentially store
  ...
```

- **id**: The key used to reference this scratchpad in agent prompts (e.g., `scratchpad`).
- **type**: Must be `agentforge.storage.scratchpad.ScratchPad`.
- **collection_id**: (Optional) Customizes the underlying storage collection name.
- **query_before**/**update_after**: Control when the scratchpad is queried/updated in the workflow.
- **query_keys**/**update_keys**: Specify which fields from the context/state are used for querying/updating.

---

## Example: Agent Prompt Template Usage

Agents access the scratchpad in their prompt templates using the `_mem.scratchpad` context. For example:

```yaml
prompts:
  system:
    scratchpad: |
      ## Scratchpad
      {_mem.scratchpad.readable}
```

- `{_mem.scratchpad.readable}`: Renders a human-readable summary of the current scratchpad contents.

You can combine the scratchpad with other memory nodes (e.g., chat history, persona memory) for richer agent context.

---

## How It Works

- The `MemoryManager` creates and manages the scratchpad node for each Cog as configured in YAML.
- When an agent triggers a query (via `query_before`), the latest scratchpad contents are loaded into the `_mem.scratchpad` context.
- When an agent triggers an update (via `update_after`), new entries are added to the log collection.
- When the log reaches a threshold (typically 10 entries), the scratchpad may automatically consolidate the log into the main pad and clear the log (see class docstring for details).
- Agents never interact with the scratchpad directly; they only access it via the prompt context.

---

## Best Practices

- Use the scratchpad for accumulating intermediate results, notes, or working memory across multiple agents or steps.
- Reference `{_mem.scratchpad.readable}` in prompts to provide agents with the latest consolidated notes.
- Adjust `query_before` and `update_after` to control when the scratchpad is accessed or updated.
- Use a unique `collection_id` if you want to separate scratchpad data across different workflows or Cogs.
- Combine the scratchpad with chat history and persona memory for advanced, context-rich workflows.

---

## Related Documentation
- [Memory in Cogs](memory.md)
- [Cog Guide](../cogs/cogs.md)
- [Prompt Template Examples](../../src/agentforge/setup_files/prompts/) 