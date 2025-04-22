# Cog (Cognitive Architecture) Guide

Cogs are declarative YAML-driven orchestrators in **AgentForge**. They define multi-agent workflows, memory nodes, and branching logic without writing Python, enabling complex, loopable, and branching AI pipelines.

---

## 1. What Is a Cog?
A **Cog** is:
- A single YAML file under `.agentforge/cogs/` that declares agents, memory nodes, and flow logic.
- A fully declarative automation: no custom Python is required to configure how agents interact.
- An engine for chaining agents, injecting persona/memory context, and handling routing based on agent outputs.

When you run a Cog, **AgentForge**:
1. Loads the YAML config and validates schema.  
2. Initializes shared memory and persona context.  
3. Executes agents in the order defined by `flow.start` and `transitions`.  
4. Merges each agent’s output into a **global context**.  
5. Routes to next agents via direct or decision-based transitions.  
6. Terminates when an `end: true` node is reached.

---

## 2. YAML Schema
```yaml
cog:
  name: "ExampleFlow"         # Identifier for this Cog
  description: "A sample decision workflow."

  agents:                       # Declare agent nodes
    - id: analyze
      type: agentforge.agent.Agent  # Python class (defaults to base Agent)
      template_file: AnalyzeAgent

    - id: decide
      # No type defined as it will default to base Agent
      template_file: DecideAgent


    - id: respond
      template_file: ResponseAgent

  memory:                       # (Optional) shared memory nodes
    - id: chat_history
      type: agentforge.storage.memory.Memory # Python class (defaults to base Memory)
      collection_id: history

  flow:                         # Define execution order
    start: "analyze"
    transitions:
      analyze: decide
      decide:
        choice:
          yes: respond
          no: analyze
        default: respond
        max_visits: 5           # Prevent infinite loops (fallback after 5)
      respond:
        end: true
```

### Top-Level Keys
- **`cog.name`**, **`cog.description`**: Metadata.
- **`agents`**: List of agent definitions:
  - `id`: Unique node key.
  - `type`: Full Python path to Agent subclass (default: base `Agent`).
  - `template_file`: Prompt YAML name (defaults to class name).
- **`memory`**: List of memory nodes:
  - `id`: Key for memory instance.
  - `type`: Memory class to instantiate (e.g., `Memory`, `ScratchPad`).
  - `collection_id`: Optional override for storage partition.
- **`flow`**:
  - `start`: `agents.id` to run first.
  - `transitions`: Mapping from each `id` to next steps:
    - **Simple**: `agentA: agentB`
    - **Decision**: Use an output field (e.g., `choice`) to branch:
      ```yaml
      agentA:
        choice:
          branch1: agentX
          branch2: agentY
        default: agentZ
      ```
    - **Loop Guard**: `max_visits` prevents infinite cycling.
    - **Terminate**: `agent_id:
        end: true` marks a terminal node.

---

## 3. Memory Nodes
Memory nodes declared under `memory` are shared across all agents in a Cog:
```yaml
memory:
  - id: session_mem
    type: agentforge.storage.memory.Memory # Python class (defaults to base Memory)
    collection_id: session123
```
- Instantiates `Memory(cog_name=cog.name, collection_id)`.
- Uses `collection_id` or defaults to node `id` for storage partition.
- All agents read/write this memory via `mem = cog.memory.session_mem`.

---

## 4. Agent Execution & Global Context
1. **Initialization**: Cog builds a `global_context` dict with initial kwargs.
2. **Agent Run**: For each node, `agent.run(**global_context)` is called.
3. **Collect Output**: Agent result stored as `global_context[node_id]`.
4. **Routing**: Next node selected via `flow.transitions[node_id]`, using simple mapping or decision keys.
5. **Loop Control**: If a node’s `max_visits` exceeded, uses its `default` branch.
6. **Completion**: When `end: true` is reached, `cog.run()` returns the final `global_context`.

Agents can access memory or persona data via `self.agent_data['storage']` and `self.agent_data['persona']` inside their logic.

---

## 5. Minimal Example
```yaml
cog:
  name: SimpleEcho
  description: "Echo flow"

  agents:
    - id: echo
      type: agentforge.agent.Agent
      template_file: EchoAgent

  flow:
    start: echo
    transitions:
      echo:
        end: true
```
- **EchoAgent.yaml** under `.agentforge/prompts/` defines the prompt.
- Running:
  ```python
  from agentforge.cog import Cog
  cog = Cog("simple_echo.yaml")
  out = cog.run(user_input="Test")
  print(out)
  ```

---

## 6. Advanced Example with Branching
```yaml
cog:
  name: ApprovalFlow
  description: "Demo approval vs. revision"

  agents:
    - id: draft
      template_file: DraftAgent

    - id: review
      template_file: ReviewAgent

    - id: publish
      template_file: PublishAgent

  memory:
    - id: log_mem
      type: agentforge.storage.scratchpad.ScratchPad
      collection_id: approval_log

  flow:
    start: draft
    transitions:
      draft: review
      review:
        approval:
          yes: publish
          no: draft
        default: publish
        max_visits: 2
      publish:
        end: true
```
- `ReviewAgent` must output a field named `approval` (e.g., `"yes"` or `"no"`).
- Memory `approval_log` accumulates interactions.

---

## 7. Best Practices
- Use clear, hyphenated `id` values (e.g., `data_fetch`, `summarize_step`).
- Keep flows short and focused—split large pipelines into multiple Cogs if needed.
- Leverage `max_visits` to guard loops.
- Share memory sparingly; name collections to reflect their purpose.
- Include `description` metadata for clarity in dashboards or logs.

---

## 8. Related Documentation
- [Agent Class](../Agents/AgentClass.md)  
- [Memory Guide](../Storage/Memory.md)  
- [Settings Overview](../Settings/Settings.md)
