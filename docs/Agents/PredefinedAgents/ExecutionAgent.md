# Execution Agent

## Introduction

The `ExecutionAgent` is a specialized but straightforward agent that extends from the base `Agent` class. Its primary role is to take a task and attempt to execute it. This agent closely resembles the behavior of the base `Agent` class, with some specific overrides to suit its particular needs.

Each agent, including the `ExecutionAgent`, is associated with a specific prompt `JSON` file which determines its interactions. This file contains a set of pre-defined prompts templates that guide the agent's behavior during its execution. For a detailed understanding of how these prompts are structured and utilized, you can refer to our [Prompts Documentation](../Prompts/AgentPrompts.md). To view the specific prompts associated with the `ExecutionAgent`, see its [JSON File](../../../src/agentforge/utils/installer/agents/ExecutionAgent.json).

---

## Import Statements
```python
from agentforge.agent import Agent
```

The `ExecutionAgent` imports its foundational `Agent` class from the `.agentforge/` directory. This allows the `ExecutionAgent` to inherit the core features and methods provided by the `Agent` class.

---

## Class Definition

```python
class ExecutionAgent(Agent):

    def load_additional_data(self):
        # ...
```

The `ExecutionAgent` class inherits from the `Agent` base class. It makes use of the core features and methods of the `Agent` class, while overriding the `load_additional_data` method to include the current task in its data dictionary.


---

## Overridden Agent Methods

### Load Additional Data
#### `load_additional_data()`

**Purpose**: Adds the current task document to the agent's data dictionary.

**Workflow**:
1. Retrieves the current task using `self.functions.get_current_task()`.
2. Adds it to `self.data['task']`.

```python
def load_additional_data(self):
    self.data['task'] = self.functions.get_current_task()['document']
```

---

## How to Use

### Initialization

To use the `ExecutionAgent`, you first need to initialize it:

```python
from agentforge.agents.ExecutionAgent import ExecutionAgent
execution_agent = ExecutionAgent()
```

### Running the Agent

The `ExecutionAgent` can be run with varying levels of contextual information. You can invoke its `run` method with optional parameters:

- `summary`: A recollection of previous memories relevant to the task.
- `context`: Internal feedback from the previous action (useful for retries or failures).
- `feedback`: User feedback.

```python
task_result = execution_agent.run(summary=summary, context=context, feedback=feedback)
```

These additional parameters match the variables used in the prompt templates. For more details on how to structure your agent's prompts, please refer to our [Prompts Documentation](../Prompts/AgentPrompts.md)

Even without these additional parameters, the agent can still attempt to execute the current task:

```python
task_result = execution_agent.run()
```

And there you have it! The `ExecutionAgent` is designed to be flexible, capable of executing tasks with or without additional context.

---