# Cognitive Architectures Guide (Cogs)

**AgentForge** introduces a **Cognitive Architecture** feature—referred to as **Cog**—that lets you orchestrate multi-agent workflows using a single YAML file. By defining your entire multi-agent script declaratively, you can build complex, loopable, and branching flows without hardcoding the interactions in Python.

---

## Introduction

The **Cog** feature in **AgentForge** offers you a powerful way to:

- **Centralize Multi-Agent Logic**: Define your entire multi-agent workflow—including agent definitions and transitions—in one YAML file for improved clarity and maintainability.  
- **Enable Complex Decision-Making**: Each agent’s output can include decision variables that dictate the next step, allowing for dynamic routing within your flow.
- **Maintain a Global Context**: A shared dictionary accumulates the outputs from each agent, ensuring that every subsequent agent has access to the latest data.  
- **Support Looping and Branching**: Design flows that loop, branch, or terminate based on conditions defined directly in your YAML.  
- **Audit the Thought Flow**: Optionally, a thought flow trail logs the output of each agent as the workflow progresses, making debugging and analysis straightforward.

---

## Core Concepts

1. **Agents**:  
   Each agent (or node) is defined in the YAML file with a unique `id`. An agent definition can specify:
   - **`type`**: A fully qualified class path (e.g., `myapp.agents.MyAgent`) that will be instantiated. If omitted, the base `Agent` is used.
   - **`template_file`**: The prompt template file used by the agent. If not provided, it defaults to the agent’s class name.

2. **Flow**:  
   The `flow` section defines how agents connect:
   - **`start`**: The `id` of the first agent to run.
   - **`transitions`**: A mapping of each agent to its subsequent agent(s). A transition can be a simple direct mapping or a decision-based block.

3. **Global Context**:  
   As the **Cog** executes, each agent’s output is merged into a shared `global_context` dictionary under its agent `id`. This allows later agents to access data produced earlier in the flow.

4. **Thought Flow Trail**:  
   If enabled, the engine records a snapshot of each agent’s output in a “thought flow trail.” This is useful for debugging and auditing the entire execution sequence.

5. **Decision Variables & Max Visits**:  
   Decision nodes use an output variable (for example, `choice`) to determine the next agent. Additionally, a decision node may define a `max_visits` limit to prevent infinite loops. Once the agent has been visited more than the allowed number, the default branch is automatically taken.

---

## YAML Specification

A typical Cog YAML file resides in your project’s configuration folder (for example, in `.agentforge/cogarchs/`). Below is a simplified example:

```yaml
cog:
  name: "SimpleFlow"
  description: "Demonstration of a basic flow with decisions."

  agents:
    - id: thought
      type: myapp.agents.MyAgent
      template_file: ThoughtAgent

    - id: reflect
      type: myapp.agents.ReflectAgent

    - id: respond
      type: myapp.agents.MyAgent
      template_file: ResponseAgent

  flow:
    start: "thought"
    transitions:
      thought: reflect
      reflect:
        choice:
          approve: respond
          revise: thought
          default: respond
      respond:
        end: true
```

### YAML Elements

1. **`cog`**: The root key that encapsulates everything about your cognitive workflow.  
2. **`name` and `description`**: Metadata fields for identifying your flow.  
3. **`agents`**: A list of agent definitions:
   - **`id`**: Unique identifier (e.g., `"reflect"`).  
   - **`type`**: The fully qualified Python path to the class (e.g., `"myapp.agents.MyAgent"`). If omitted, defaults to the base `Agent`.  
   - **`template_file`**: Which YAML prompt file to load for that agent. If omitted, defaults to the class name.  
4. **`flow`**:
   - **`start`**: Which agent `id` to run first.  
   - **`transitions`**: Describes how each agent (identified by its `id`) moves to the next. Possible ways to define transitions:
     - **Simple String**: `"agentA: agentB"` means once `agentA` finishes, move to `agentB`.  
     - **Decision (dictionary)**: If `agentA` returns a key named `"choice"`, the flow checks if `"approve"`, `"revise"`, etc. is in the agent’s output, and transitions accordingly. You can define a `"default"` if no match is found.  
     - **`end: true`**: Marks a terminal node that stops the flow.  
     - **`max_visits`**: (Optional) If included in the node’s transition dictionary, it prevents looping indefinitely. Once an agent is visited more than `max_visits` times, the flow takes the `default` path.

---

## Using the Cog Feature

### 1. Creating a Cog Instance

Place your Cog YAML file (e.g., `simple_flow.yaml`) in your configuration folder. Then, create a Cog instance by providing the YAML file name:

```python
from agentforge.cog import Cog

# Create a Cog instance with the simple_flow.yaml file, thought flow trail logging enabled by default
cog = Cog("simple_flow.yaml")
```

### 2. Running the Cog

You can pass initial parameters (e.g., `user_input`) to the Cog’s `run` method. The engine will initialize the global context with these values, execute the flow, and return the final context.

```python
result_context = cog.run(user_input="Hello, world!")
print("Final Global Context:", result_context)
```


During execution:
1. **Start Node**: The Cog looks for the `start` key in the YAML (`thought` in this example).  
2. **Agent Execution**:  
   - The agent’s `run()` method is called with the current global context.  
   - The agent’s output is stored under `global_context[agent_id]`.  
3. **Decision Handling**: If the current agent’s transition is a dictionary with a decision key (like `"choice"`), the Cog checks `global_context[agent_id]["choice"]` to decide the next node. If the agent’s choice is unrecognized, the `default` path is used (if defined).  
4. **Max Visits (Optional)**: If the node’s transition includes `max_visits`, once that agent is visited more times than allowed, the flow automatically takes the `default` branch.  
5. **Termination**: If a node is marked `end: true`, the flow stops. The final `global_context` (with all agents’ outputs) is returned by `cog.run()`.

---

## Execution Flow

1. **Initialization**: The Cog engine resets its global context and thought flow trail, then loads and validates the YAML configuration.
2. **Agent Execution**: Starting from the agent specified in the `start` key, each agent is executed sequentially. Their outputs are merged into the global context.
3. **Decision Handling**: For decision-based transitions, the engine uses the decision variable (e.g., `choice`) from the agent’s output to select the next agent. If a node’s `max_visits` limit is reached, the default branch is taken.
4. **Termination**: The flow continues until a transition marked with `end: true` is reached, at which point the final global context is returned.

---

## Global Context & Thought Flow Trail

- **Global Context**: The final global context is a dictionary where each key is an agent’s `id` and the corresponding value is that agent’s output. This context aggregates data across the entire workflow.
- **Thought Flow Trail**: If enabled, the Cog engine logs the output of each agent as it is executed. This trail is useful for auditing or debugging the flow of information through your architecture.

### Accessing the Thought Flow Trail

When `enable_trail_logging=True`, each agent’s output is appended to an internal list. This can be used for debugging or analytics:

```python
print("Thought Flow Trail:", cog.thought_flow_trail)
```

`thought_flow_trail` is a list where each entry looks like `{"agent_id": {...agent output...}}`.

---

## Example: Orchestrating a Reflection Loop

Consider a scenario where an agent (e.g., `reflect`) determines whether to continue refining a thought process or move on to produce a final response. The YAML might look like:

```yaml
cog:
  name: "ReflectionFlow"
  description: "A reflection loop that can revise or move on."

  agents:
    - id: reason
      type: myapp.agents.MyAgent
      template_file: ReasonAgent

    - id: reflect
      type: myapp.agents.ReflectAgent

    - id: respond
      template_file: GenerateAgent

  flow:
    start: "reason"
    transitions:
      reason: reflect
      reflect:
        choice:
          approve: respond
          revise: reason
          default: respond
        max_visits: 3
      respond:
        end: true
```

In this example:
- The `reason` agent is defined being of type `MyAgent` and will use the defined `ReasonAgent` prompt template file.
- The `reflect` agent is defined being of type `ReflectAgent` and has no `template_file` attribute defined, so it will default to using the `ReflectAgent` prompt template file based on the agent type class name.
- The `reason` agent only defines a `template_file` attribute so it will use the `GenerateAgent` template prompt file and it will default to an agent of type `Agent` which is the base agent class implementation of the framework.

The **Cognitive Flow** looks as follows:
- The flow begins with the `reason` agent and once it return it's output the flow will pass onto the `reflect` agent.
- The `reflect` agent outputs a decision (under the key `choice`), which determines whether to loop back to `reason` or proceed to `respond`.
- The `max_visits` property on `reflect` ensures that if it is revisited more than 3 times, the default branch (`respond`) is taken, preventing an infinite loop.
- Once `respond` is executed and marked with `end: true`, the flow terminates and the final global context is returned.

## Example Output:
```python
from agentforge.cog import Cog

cog = Cog("example_cog.yaml")
result_context = cog.run(user_input="Hello, world!")
```
```python
result_context = 
{
    'user_input': "Hello, world!",
    'reason': <response given by the 'reason' agent>,
    'reflect': {'choice': <choice made by the 'reflect' agent>}, # Assuimg the `ReflectAgent` returns a choice inside a Dict
    'respond': <response given by the 'respond' agent>,
}        
```

---

## Error Handling

- **Invalid YAML Config**: If the Cog file is missing essential keys (e.g., `start`, `agents`), a `ValueError` or `ImportError` is raised at initialization.  
- **Agent Failures**: If an agent returns `None` or raises an exception internally, the `Cog.run()` currently stops execution and returns whatever context was accumulated (or `None` if no output).
- **Unknown Decision Value**: If a decision output (e.g., `"choice": "foo"`) doesn’t match a branch and no `default` is provided, the flow can’t proceed. You can handle this gracefully in your implementation.

---

## Best Practices

- **Define Clear Agent IDs**: Use meaningful and unique identifiers for each agent to make the flow easy to understand.
- **Use Descriptive Decision Variables**: Ensure that the decision variable (e.g., `choice`) used by decision nodes is consistently referenced in your agent outputs and YAML. **Note**: Decision variable keys can have any name.
- **Limit Loops with max_visits**: Set appropriate `max_visits` values on decision nodes to prevent infinite loops while still allowing for necessary iteration.
- **Define Default Paths in Decision Nodes**: Make sure that agents that make decisions based on a returned key have a default path they can follow in case the agent fails to respond with a valid decision.
- **Leverage the Thought Flow Trail**: Thought trail logging is enabled by default to trace the evolution of the global context and debug complex flows.

---

## Conclusion

By using a YAML-based configuration, **AgentForge’s Cog Engine** lets you orchestrate complex, multi-agent workflows in a flexible and maintainable way. The engine loads your architecture, instantiates agents as defined, and executes them in sequence or based on decisions, all while maintaining a global context for data sharing and an optional trail for auditing. This modular approach keeps your multi-agent orchestration transparent and easy to evolve as your system grows.

---

**Need Help?**  
- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)  
- **Discord**: [Join our Discord Server](https://discord.gg/ttpXHUtCW6)
