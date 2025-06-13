# Cog (Cognitive Architecture) Guide

Cogs in **AgentForge** are declarative YAML-driven orchestrators that define multi-agent workflows, memory nodes, and branching logic—enabling complex, loopable, and branching AI pipelines without writing custom Python code.

---

## 1. What Is a Cog?
A **Cog** is:
- A YAML file under `.agentforge/cogs/` that declares agents, memory nodes, and flow logic.
- A fully declarative automation: no custom Python is required to configure agent interactions.
- An engine for chaining agents, injecting persona/memory context, and handling routing based on agent outputs.

When you run a Cog, **AgentForge**:
1. Loads and validates the YAML config.
2. Initializes shared memory and persona context.
3. Executes agents in the order defined by `flow.start` and `transitions`.
4. Merges each agent's output into the **internal state**.
5. Routes to next agents via direct or decision-based transitions.
6. Terminates when an `end: true` node is reached.

---

## 2. YAML Schema & Configuration

```yaml
cog:
  name: "ExampleFlow"         # Identifier for this Cog
  description: "A sample decision workflow."

  agents:                       # Declare agent nodes
    - id: analyze
      template_file: analyze_agent  # Required: at least one of template_file or type
      
    - id: decide
      template_file: decide_agent

    - id: respond
      template_file: response_agent

  memory:                       # (Optional) shared memory nodes
    - id: general_memory
      type: agentforge.storage.memory.Memory # Optional: defaults to base Memory
      collection_id: history
      query_before: [analyze]
      update_after: [respond]
      query_keys: [user_input]
      update_keys: [respond]

  flow:                         # Define execution order
    start: "analyze"
    transitions:
      analyze: decide
      decide:
        choice:
          "approve": respond
          "reject": analyze
        fallback: respond
        max_visits: 5
      respond:
        end: true
```

### Top-Level Keys
- **`cog.name`**, **`cog.description`**: Metadata.
- **`agents`**: List of agent definitions:
  - `id`: Unique node key (required).
  - `template_file`: Prompt YAML name (required if `type` not set).
  - `type`: Full Python path to Agent subclass (required if `template_file` not set).
- **`memory`**: List of memory nodes (optional):
  - `id`: Key for memory instance (required).
  - `type`: Memory class to instantiate (optional; defaults to base Memory).
  - `collection_id`: Optional override for storage partition (defaults to node's `id` for base Memory; subclasses may override).
  - `query_before`/`update_after`: List or string of agent IDs (always treated as lists internally).
  - `query_keys`/`update_keys`: Keys to extract from context/state for querying/updating memory.
- **`flow`**:
  - `start`: `agents.id` to run first.
  - `transitions`: Mapping from each `id` to next steps:
    - **Simple**: `agentA: agentB`
    - **Decision**: Use an output field (e.g., `choice`) to branch:
      ```yaml
      agentA:
        choice:
          "approve": agentX
          "reject": agentY
        fallback: agentZ
      ```
    - **Loop Guard**: `max_visits` prevents infinite cycling.
    - **Terminate**: `agent_id: end: true` marks a terminal node.

---

## 3. Decision-Based Transitions

Decision-based transitions route flow based on values in the agent's output.

- **Decision Key**: The field name in the agent's output that determines the next branch.
- **Value Normalization**: Matching is case-insensitive and normalizes booleans/strings. Always quote branch labels in YAML to avoid type conversion issues.
- **Fallback**: If a decision value doesn't match, or the key is missing, or `max_visits` is exceeded, the `fallback` branch is used. If no fallback is defined, the flow terminates with an exception.

---

## 4. Memory Nodes & Chat History

Memory nodes declared under `memory` are shared across all agents in a Cog. Each node can:
- Specify when to query or update (before/after specific agents)
- Use `query_keys` and `update_keys` to control what data is used
- Use a custom `type` for specialized memory behavior

**Collection Naming:**
- For base Memory, `collection_id` defaults to the node's `id` if not specified.
- Some subclasses (e.g., PersonaMemory) may override this logic and append suffixes or use different naming.

**Automatic Chat History Memory:**
- Unless `chat_memory_enabled: false` is set at the top level, a `chat_history` memory node is automatically added for you.
- Configure the recency slice with `chat_history_max_results` (default: 20, `0` = no limit) and the semantic slice with `chat_history_max_retrieval` (default: 20, `0` = disable semantic retrieval).
- Access chat history in prompts with `{_mem.chat_history.history}` (recent turns) and `{_mem.chat_history.relevant}` (semantically relevant turns).

> **Note:** You do not need to define a `chat_history` memory node yourself—this is handled automatically when chat memory is enabled.

---

## 5. Agent Execution & Context

- **Initialization**: Cog builds a `context` dict (external input) and a `state` dict (internal agent outputs).
- **Agent Run**: For each node, the agent is called with the current context and state.
- **Collect Output**: Agent result is stored in `state[node_id]`.
- **Memory Query/Update**: Memory is queried before and updated after agents as configured.
- **Routing**: Next node is selected via `flow.transitions[node_id]`.
- **Loop Control**: If a node's `max_visits` is exceeded, the `fallback` branch is used.
- **Completion**: When `end: true` is reached, `cog.run()` returns the final state or specified output.

### How Agents Access Context, State, and Memory

When an agent runs, the Cog engine provides three key variables in the prompt template context:

- **`_ctx`**: The current external context, such as user input and any runtime values passed to `cog.run()`.
- **`_state`**: The internal state dictionary, containing outputs from all previously executed agents in the workflow.
- **`_mem`**: The memory manager, where each memory node is accessible as an attribute. For example, if you have a memory node with `id: persona_memory`, you can access its properties in your prompt as `{_mem.persona_memory.<property>}`.

This allows agents to reference both the latest user input/context and the outputs of other agents. For example, in a prompt template:

```yaml
prompts:
  user:
    context: |
      ## User Input
      {_ctx.user_input}

    analysis: |
      ## Previous Analysis
      {_state.analysis}

    persona_info: |
      ## Persona Info
      {_mem.persona_memory._narrative}
```

- `{_ctx.user_input}`: Accesses the current user input or context value.
- `{_state.analysis}`: Accesses the output of the `analysis` agent node.
- `{_mem.persona_memory._narrative}`: Accesses the contents of the persona narrative built by the `PersonaMemory` memory node.

---

## 6. Return Values

The Cog's `run()` method returns values based on the `end` keyword configuration:

- **Default**: Returns the internal state dictionary with all agent outputs.
- **`end: true`**: Returns only the output of the last agent executed.
- **`end: "dot.notation.key"`**: Returns a specific value from the state using dot notation.

**Example:**
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

The Cog engine handles errors as follows:
- **Invalid Transitions**: If a transition points to a non-existent agent, an exception is raised.
- **Missing Decision Keys/No Matching Branch**: If the decision key is missing or the value doesn't match, the `fallback` branch is used. If no fallback is defined, the flow terminates with an exception.
- **Loop Prevention**: When `max_visits` is exceeded, the `fallback` branch is used. If no fallback, the flow terminates with an exception.

---

## 8. Minimal Example

```yaml
cog:
  name: "SimpleAnalysis"
  description: "Basic analysis flow"

  agents:
    - id: analyze
      template_file: analyze_agent

  flow:
    start: analyze
    transitions:
      analyze:
        end: true
```

---

## 9. Advanced Example with Branching

```yaml
cog:
  name: "AnalysisDecisionFlow"
  description: "A multi-step workflow with decision branching"

  agents:
    - id: analyze
      template_file: analyze_agent
    - id: decide
      template_file: decide_agent
    - id: respond
      template_file: response_agent

  memory:
    - id: general_memory
      query_before: [analyze, respond]
      update_after: [respond]
      query_keys: [user_input]
      update_keys: [user_input, respond]

  flow:
    start: analyze
    transitions:
      analyze: decide
      decide:
        choice:
          "approve": respond
          "reject": analyze
        fallback: respond
        max_visits: 3
      respond:
        end: true
```

---

## 10. Best Practices

- **Prompt Engineering**: Structure prompts with clear sections and use memory in context sections.
- **Decision Branches**: Always quote branch names in YAML, set reasonable `max_visits`, and define `fallback` paths.
- **Memory Management**: Use `query_before` and `update_after` to control memory usage, and be explicit about `query_keys` and `update_keys`. Use `{_mem.<node_id>.readable}` in prompts for human-friendly formatting.
- **Chat History**: Leverage the automatic `chat_history` memory node for conversation context unless explicitly disabled.
- **Testing**: Use `cog.get_track_flow_trail()` to inspect execution order and outputs.

---

## 11. Related Documentation
- [Memory Guide](../memory/memory.md)
- [Settings Overview](../settings/settings.md)
