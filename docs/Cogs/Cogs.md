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
    - id: general_memory
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
  - id: general_memory
    query_before: [agent1, agent2]  # Query this memory before these agents
    update_after: [agent3]          # Update this memory after these agents
    query_keys: [user_input]        # Keys to extract for querying
    update_keys: [respond]          # Keys to extract for updates
```

### Memory Subclasses and Collection Names
By default, memory nodes use the base Memory class. For specialized memory behavior, specify a subclass with `type`. 

Additionally, memory nodes can be instanciated with a specific vector store collection name `collection_id`, allowing flexibility for each memory node to define where it will store and retreives memories from.

```yaml
memory:
  # Default memory using base Memory class
  - id: general_memory
    collection_id: conversation_history
    ...
    
  # Journal memory for structured conversation history
  - id: conversation_journal
    type: agentforge.storage.journal.Journal
    ...
    
  # Scratchpad for maintaining working notes
  - id: agent_notes
    collection_id: working_notes
    type: agentforge.storage.scratchpad.ScratchPad
    ...
```

### Core Configuration
- **id**: Required. Unique identifier for the memory node, used to access it via `memory[id]` in the context.
- **collection_id**: Optional. The storage collection to use. Defaults to the node's `id` if not specified.
- **type**: Optional. Specifies a Memory subclass to use. Defaults to `agentforge.storage.memory.Memory` (base Memory class) when omitted.

### Query and Update Configuration
Control when memory is used during Cog execution:
- **query_before**: List of agent IDs - memory is queried before these agents run
- **update_after**: List of agent IDs - memory is updated after these agents run
- **query_keys**: Keys to extract from global context for querying memory
- **update_keys**: Keys to extract from global context for updating memory

Each Memory instantiates with the cog's name and uses the collection_id (specified or default). All agents can access memory via their context's `memory` key.

### Accessing Memory in Prompt Templates

Memory is available in two formats in agent prompt templates:

```
# Human-readable formatted string (recommended for prompts)
{memory.general_memory.readable}

# Access to raw Chroma result data
{memory.general_memory.raw.documents[0]}
{memory.general_memory.raw.metadatas[0].timestamp}
```

Example template section using memory:
```yaml
prompts:
  user:
    Memory: |+
      ### Relevant background
      Review these previous interactions for context:
      ---
      {memory.general_memory.readable}
      ---
```

The readable format presents each memory entry as:
```
--- Memory 0: <document_id>
content: <document_text>
metadata:
  timestamp: <timestamp>
  user_input: <user message>
  # Other metadata fields as available
```

---

## 5. Agent Execution & Global Context
1. **Initialization**: Cog builds a `global_context` dict with initial kwargs.
2. **Agent Run**: For each node, `agent.run(**global_context)` is called.
3. **Collect Output**: Agent result stored as `global_context[node_id]`.
4. **Memory Query/Update**: Memory is queried before and updated after agents based on configuration.
5. **Routing**: Next node selected via `flow.transitions[node_id]`, using simple mapping or decision keys.
6. **Loop Control**: If a node's `max_visits` exceeded, uses its `fallback` branch.
7. **Completion**: When `end: true` is reached, `cog.run()` returns the final `global_context`.

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
  name: "SimpleAnalysis"
  description: "Basic analysis flow"

  agents:
    - id: analyze
      template_file: AnalyzeAgent

  flow:
    start: analyze
    transitions:
      analyze:
        end: true
```
- **AnalyzeAgent.yaml** under `.agentforge/prompts/` defines the prompt.
- Running:
  ```python
  from agentforge.cog import Cog
  cog = Cog("SimpleAnalysis")
  out = cog.run(user_input="Analyze this text")
  flow = cog.get_track_flow_trail()
  print(flow)
  print(out)
  ```

---

## 9. Advanced Example with Branching
```yaml
cog:
  name: "AnalysisDecisionFlow"
  description: "A multi-step workflow with decision branching"
  response_format: "auto"

  agents:
    - id: analyze
      template_file: AnalyzeAgent

    - id: decide
      template_file: DecideAgent

    - id: respond
      template_file: ResponseAgent
      response_format: "none"

  memory:
    - id: general_memory
      query_before: [analyze, respond]   # Query this memory before these agents
      update_after: [respond]            # Update this memory after these agents
      query_keys: [user_input]           # Query using user_input
      update_keys: [user_input, respond] # Update with user input and response

  flow:
    start: analyze
    transitions:
      analyze: decide
      decide:
        choice:
          "approve": respond
          "reject": analyze  # Loop back to analyze
        fallback: respond
        max_visits: 3        # Prevent infinite loops
      respond:
        end: true
```

In this workflow:
1. The `analyze` agent examines user input
2. The `decide` agent evaluates the analysis and makes a decision
3. If approved, flow continues to `respond`
4. If rejected, flow loops back to `analyze` for refinement
5. If other, or After 3 loops, the flow proceeds to `respond` via fallback

Example prompt template using memory (from AnalyzeAgent.yaml):
```yaml
prompts:
  user:
    Memory: |+
      ### Relevant background
      Review these previous interactions for patterns or user history:
      ---
      {memory.general_memory.readable}
      ---
```

---

## 10. Best Practices

1. **Prompt Engineering**
   - Structure prompts with clear sections
   - Use memory in context sections
   - Include relevant parts of previous agent outputs

2. **Decision Branches**
   - Always quote branch names in YAML (`"yes"`, not just yes)
   - Set reasonable `max_visits` limits
   - Always define `fallback` paths

3. **Memory Management**
   - Use appropriate `query_before` and `update_after` configurations
   - Be explicit about `query_keys` and `update_keys`
   - Ensure memory nodes have descriptive `id` values
   - Use `{memory.node_id.readable}` in prompts for human-friendly formatting

4. **Testing**
   - Use `cog.get_track_flow_trail()` to inspect execution path
   - Review the global context to see how data flows between agents
   - Test edge cases for decision branches

---

## 11. Related Documentation
- [Agent Class](../Agents/AgentClass.md)  
- [Memory Guide](../Storage/Memory.md)  
- [Settings Overview](../Settings/Settings.md)
