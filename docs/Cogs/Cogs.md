# Cognitive Architecture Guide

**AgentForge** introduces a **Cognitive Architecture** (CogArch) feature that allows you to define multi-agent workflows in a single YAML file. By using a declarative approach, you can orchestrate multiple agents (nodes) with transitions and decisions, forming dynamic, loopable, and potentially branching flows—without needing to hardcode these interactions in Python.

---

## Introduction

The **CogArch** feature in **AgentForge**:

1. **Centralizes Multi-Agent Logic**: Put your entire multi-agent script (with references to specific agent IDs, prompt files, or classes) in a single YAML file for maintainability and clarity.  
2. **Enables Complex Decision-Making**: Agents can provide variables in their output (e.g., `"decision"`) that direct the next step in the workflow.  
3. **Manages a Global Context**: Each agent’s output is merged into a shared context, ensuring later agents have the most up-to-date data.  
4. **Supports Looping, Conditional Branching, and Termination**: The architecture can incorporate multiple paths, iteration, and explicit end conditions, all declared in YAML.

---

## Core Concepts

1. **Nodes (Agents)**: Each node references an **Agent** definition. You specify an `id` (unique identifier), a `type` (the agent class to instantiate), and optionally a `template_file`.  
2. **Flow**: A section describing how these agents connect. Nodes can simply move to the next node or make a “decision” that routes to different outcomes.  
3. **Global Context**: A shared dictionary passed from one agent to the next, storing all partial results or variables.  
4. **Thought Flow Trail**: An optional history of the context after each node’s execution, useful for debugging or auditing the multi-agent process.  
5. **Decision Variable**: A variable in an agent’s output used to pick the next node. For example, an agent might output `"decision": "reject"`, sending the flow to a loop or different node.

---

## YAML Specification

A **CogArch** YAML file typically resides in `project_root/.agentforge/cogarchs`. For example:

```yaml
cogarch:
  description: "A sample architecture orchestrating five agents in sequence with a reflection step."

  agents:
    - id: ThoughtAgent
      type: ChatAgent
      template_file: ThoughtAgent
    - id: TheoryAgent
      type: ChatAgent
      template_file: TheoryAgent
    - id: ThoughtProcessAgent
      type: ChatAgent
      template_file: ThoughtProcessAgent
    - id: ReflectionAgent
      type: ChatAgent
      template_file: ReflectionAgent
    - id: GenerateAgent
      type: ChatAgent
      template_file: GenerateAgent

  flow:
    start: ThoughtAgent
    transitions:
      ThoughtAgent: TheoryAgent
      TheoryAgent: ThoughtProcessAgent
      ThoughtProcessAgent: ReflectionAgent
      ReflectionAgent:
        decision:  # The agent outputs a variable named 'decision' in the context
          approve: GenerateAgent
          revise: ThoughtProcessAgent
          reject: ThoughtProcessAgent
          default: GenerateAgent
      GenerateAgent:
        end: true
```

### YAML Elements

1. **`cogarch`**: The root key that encapsulates your entire architecture.  
2. **`agents`**: A list of participating agents, each with:  
   - **`id`**: Unique node identifier used by transitions.  
   - **`type`**: The agent class to instantiate (e.g., `ChatAgent`); if missing, defaults to the base `Agent`.  
   - **`template_file`**: The prompt file. If missing, it may default to the `type` or `id`.  
3. **`flow`**:
   - **`start`**: Which agent (`id`) to run first.  
   - **`transitions`**: A dictionary describing how each node moves to the next.  
     - A **simple transition** is `NodeA: NodeB`.  
     - A **decision** block references an output variable (like `decision`) and maps each possible value to the next node. A `default` case is optional.  
     - A node can be marked with `end: true` to terminate the flow.

---

## Using the CogArch Feature

### 1. Loading the CogArch YAML

You place your `.yaml` file in `project_root/.agentforge/cogarchs/`. Then you create or use a **CogArchEngine** (or similarly named class) that reads and interprets the file. Example (pseudocode):

```python
from agentforge.cogarch_engine import CogArchEngine

engine = CogArchEngine("my_cogarch.yaml")
result_context = engine.run()
print("Final context:", result_context)
```

### 2. Execution Flow

1. **Start Node**: The engine looks up the `start` agent and instantiates it.  
2. **Running Agents**: Each agent’s `run()` method is called with the global context. The agent’s output merges back into the global context.  
3. **Decision**: If the node’s transition is a dictionary referencing a decision variable, the engine checks that variable in the global context to pick a next node.  
4. **Looping**: If the decision routes the flow back to an earlier agent, the engine repeats that cycle, continuing until a node’s transition has `end: true` or an error stops the flow.

### 3. Global Context

All data that each agent outputs is merged into a single `global_context` dictionary. For instance, if `ThoughtAgent` returns `{'thought': 'We should ask for more info'}`, subsequent agents see `global_context['thought']` set to that value. This allows for flexible data sharing without tight coupling.

### 4. Thought Flow Trail

If you enable a “thought_flow_trail,” the engine stores snapshots of the `global_context` after every node’s execution. This helps you debug or analyze how the architecture evolved the data. If logging is turned on, you can optionally write this data to a log file.

---

## Error Handling and Retries

1. **Agent Failures**: If an agent’s `run()` method raises an exception, the engine can retry that node a configurable number of times before aborting.  
2. **Unknown Decision Values**: If a node is decision-based but the returned value doesn’t match any outcome (and no `default` is defined), the engine should raise an error or halt the flow.  
3. **Missing Agents or Start Node**: The engine will validate references in the YAML. If something is missing, it fails fast with a clear message.

---

## Example Usage: Orchestrating a Reflection Loop

1. You define five agents in your YAML (like `ThoughtAgent`, `TheoryAgent`, `ThoughtProcessAgent`, `ReflectionAgent`, `GenerateAgent`), each with a `template_file`.  
2. The flow transitions from `ThoughtAgent` → `TheoryAgent` → `ThoughtProcessAgent` → `ReflectionAgent`, then uses `decision` from ReflectionAgent to decide whether to go to `GenerateAgent` (approve) or loop back to `ThoughtProcessAgent` (reject/revise).  
3. Once `GenerateAgent` is called, it has `end: true`, stopping the flow and returning the final context.

---

## Best Practices

- **Keep Flows Simple**: While loops and branching are powerful, aim for clarity in your YAML.  
- **Use Meaningful Decision Variables**: ReflectionAgent might return `decision: "approve"`, but you can name that variable anything. Ensure it’s consistent across the agent prompt logic and the CogArch transitions.  
- **Manage Context**: Avoid polluting the global context with too many ephemeral keys. Keep it tidy so subsequent agents only see relevant data.  
- **Debugging**: Turn on the thought flow trail and logging if you need to observe exactly how data evolves.

---

## Conclusion

By defining a YAML-based **Cognitive Architecture**, you can orchestrate multiple agents in **AgentForge** without hardcoding multi-step logic in Python. The **CogArch Engine**:

1. Loads your architecture definition.  
2. Instantiates nodes (agents) as specified.  
3. Executes them in sequence or via decisions based on agent output.  
4. Maintains a global context (and optional trail) for maximum transparency and debugging.

This modular approach keeps your agent orchestration flexible, maintainable, and easy to evolve as your system grows in complexity.

---

**Need Help?**  
- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)  
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)