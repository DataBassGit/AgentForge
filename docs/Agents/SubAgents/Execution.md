# Execution Agent

## Overview

The `ExecutionAgent` is a subagent that inherits functionalities from the main [Agent](./Agent.md) superclass. It's an example of a simple subagent that doesn't override any methods from the superclass. The main distinction is its name, which determines the prompts that are loaded into its data.

For a deep dive into how to create more complex subagents, see [SubAgents](./SubAgents.md).

---

## Class Definition

```python
from .agent import Agent

class ExecutionAgent(Agent):
    pass
```

## Key Features

- **Inherits All Functionalities**: Since it doesn't override any methods, it inherits all functionalities from the `Agent` superclass.
- **Prompt Loading**: The name 'ExecutionAgent' is critical as it dictates what prompts are loaded for this agent from the [Persona File](./PersonaFile.md).

---

## How to Use

To utilize `ExecutionAgent`, you can simply instantiate it like any other Python class:

```python
execution_agent = ExecutionAgent()
```

This will automatically load all relevant prompts and execute tasks based on its name.

For more customization, you can override its methods as described in the [Agent Methods Page](./AgentMethods.md).