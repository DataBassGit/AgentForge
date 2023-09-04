# Reflexion Agent

## Introduction

The `ReflexionAgent` is a specialized agent designed to review responses for accuracy and safety relevant to a given objective. Despite its specialized role, it doesn't override any of the base `Agent` class methods, making it a straightforward extension of the general `Agent` class.

---

## Import Statements
```python
from agentforge.agent import Agent
```

The `ReflexionAgent` imports the foundational `Agent` class from the `.agentforge/` directory. This import allows the `ReflexionAgent` to inherit all the core features and methods provided by the `Agent` class.

---

## Class Definition

```python
class ReflexionAgent(Agent):
    pass
```

The `ReflexionAgent` class inherits from the `Agent` base class, utilizing all its core features and methods without any overrides.

---

## How to Use

### Initialization

To make use of the `ReflexionAgent`, it first needs to be initialized:

```python
reflexion_agent = ReflexionAgent()
```

### Running the Agent

The `ReflexionAgent` can be invoked with optional parameters to cater to its specific role of reviewing responses:

- `Context`: A summary of previous actions.
- `Instruction`: Description of the task that corresponds to the respondent's answer.
- `Feedback`: The respondent's answer to reflect upon.

```python
reflection_result = reflexion_agent.run(Context=context, Instruction=instruction, Feedback=feedback)
```

Even in the absence of these optional parameters, the agent will attempt to review the responses based on its inherited methods from the `Agent` class:

```python
reflection_result = reflexion_agent.run()
```

The `ReflexionAgent` is streamlined and flexible, capable of performing its review tasks with or without additional context.

> **Note:** For more details on how to structure your agent's prompts, please refer to our [Prompts Documentation](../../Prompts/Prompts.md) and this specific [Agent's Prompt.](../../../src/agentforge/utils/installer/agents/ReflexionAgent.json)