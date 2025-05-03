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
4. Merges each agent's output into a **global context**.  
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
        choice:                   # This is the decision key from agent output
          "yes": respond          # Note: quotes for yes/no recommended
          "no": analyze
        fallback: respond         # Used when no match or missing key
        max_visits: 5             # Prevent infinite loops
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
          "yes": agentX
          "no": agentY
        fallback: agentZ
      ```
    - **Loop Guard**: `max_visits` prevents infinite cycling.
    - **Terminate**: `agent_id:
        end: true` marks a terminal node.

---

## 3. Decision-Based Transitions

Decision-based transitions route flow based on values in the agent's output.

### Key Concepts

#### Decision Keys
The decision key is the field name in the agent's output that determines the next branch:

```yaml
transitions:
  decide:
    verdict:         # 'verdict' is the decision key
      approve: publish
      reject: revise
    fallback: error
```

The agent must output a dictionary containing the decision key:
```
{
  "verdict": "approve",  # This value determines the next branch
  "rationale": "..."
}
```

#### Value Normalization
**AgentForge** normalizes decision values for flexible matching:

1. **Case-Insensitive Matching**: `"YES"`, `"Yes"`, and `"yes"` all match the same branch
2. **Type Normalization**: Boolean values (`true`/`false`) and their string equivalents (`"true"`/`"false"`) are normalized
3. **YAML Boolean Conversion**: YAML automatically converts unquoted `yes`, `no`, `true`, `false` to Boolean values

**Important:** To ensure values are treated as strings in YAML, always quote your decision branch labels:

```yaml
choice:
  "yes": approve    # Quoted to ensure it's a string
  "no": reject      # Quoted to ensure it's a string
```

This ensures that both Boolean values and string representations will match correctly.

#### Fallback Mechanism
When a decision path can't be resolved, these fallback options are used in order:

1. The matched transition branch isn't found: use `fallback` value
2. The decision key isn't in agent output: use `fallback` value
3. The `max_visits` limit is exceeded: use `fallback` value
4. If no `fallback` is specified in any of these cases, the flow will terminate with an exception

```yaml
transitions:
  decide:
    choice:
      "yes": branch_a
      "no": branch_b
    fallback: default_branch  # Used when choice doesn't match or is missing
    max_visits: 3             # After 3 visits, use fallback
```

---

## 4. Memory Nodes
Memory nodes declared under `memory` are shared across all agents in a Cog:
```yaml
memory:
  - id: session_mem
    type: agentforge.storage.memory.Memory
    collection_id: session123
    query_before: [agent1, agent2]  # Query this memory before these agents
    update_after: [agent3]          # Update this memory after these agents
```
- Instantiates `Memory(cog_name=cog.name, collection_id)`.
- Uses `collection_id` or defaults to node `id` for storage partition.
- All agents can access memory via the context's `memory` key.

---

## 5. Agent Execution & Global Context
1. **Initialization**: Cog builds a `global_context` dict with initial kwargs.
2. **Agent Run**: For each node, `agent.run(**global_context)` is called.
3. **Collect Output**: Agent result stored as `global_context[node_id]`.
4. **Routing**: Next node selected via `flow.transitions[node_id]`, using simple mapping or decision keys.
5. **Loop Control**: If a node's `max_visits` exceeded, uses its `fallback` branch.
6. **Completion**: When `end: true` is reached, `cog.run()` returns the final `global_context`.

Agents can access memory or persona data via `self.agent_data['storage']` and `self.agent_data['persona']` inside their logic.

---

## 6. Return Values
The Cog's `run()` method returns different values based on the `end` keyword configuration:

1. **Default Return**: Returns the full internal context dictionary with all agent outputs.
2. **End: true**: Returns only the output of the last agent executed.
3. **End: "dot.notation.key"**: Returns a specific value from the context using dot notation.

Example:
```yaml
transitions:
  final_agent:
    end: true  # Returns only final_agent's output
```

Or using a specific key:
```yaml
transitions:
  final_agent:
    end: "final_agent.summary"  # Returns only the summary key from final_agent's output
```

---

## 7. Error Handling

The Cog engine handles several error conditions:

1. **Invalid Transitions**: If a transition points to a non-existent agent, an exception is raised.
2. **Missing Decision Keys**: If the decision key isn't in the agent's output, the `fallback` branch is used.
3. **Loop Prevention**: When `max_visits` is exceeded, the `fallback` branch is used.
4. **No Matching Branch**: If the decision value doesn't match any branch, the `fallback` branch is used.

If `fallback` is not defined in these error cases, the behavior depends on the error:
- Missing decision keys or no matching branch with no fallback: the flow will terminate
- Invalid transitions always raise an exception

---

## 8. Minimal Example
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
  cog = Cog("SimpleEcho")
  out = cog.run(user_input="Test")
  flow = cog.get_track_flow_trail()
  print(flow)
  print(out)
  ```

---

## 9. Advanced Example with Branching
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
          "yes": publish  # Quoted to ensure string matching
          "no": draft
        fallback: publish
        max_visits: 2
      publish:
        end: true
```
- `ReviewAgent` must output a field named `approval` (e.g., `"yes"` or `"no"`).
- Memory `approval_log` accumulates interactions.

---

## 10. Best Practices
- Use clear, hyphenated `id` values (e.g., `data_fetch`, `summarize_step`).
- Always quote string values in YAML transitions (`"yes"`, `"no"`, `"true"`, `"false"`) to avoid automatic conversion.
- Keep flows short and focused—split large pipelines into multiple Cogs if needed.
- Leverage `max_visits` and `fallback` to guard loops and handle edge cases.
- Share memory sparingly; name collections to reflect their purpose.
- Include `description` metadata for clarity in dashboards or logs.

---

## 11. Related Documentation
- [Agent Class](../Agents/AgentClass.md)  
- [Memory Guide](../Storage/Memory.md)  
- [Settings Overview](../Settings/Settings.md)
