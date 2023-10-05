# Reflexion Agent

## Introduction

The `ReflexionAgent` is a specialized agent designed to review responses for accuracy and safety relevant to a given objective. Despite its specialized role, it doesn't override any of the base `Agent` class methods, making it a straightforward extension of the base `Agent` class.

Each agent, including the `ReflexionAgent`, is associated with a specific prompt `YAML` file which determines its interactions. This file contains a set of pre-defined prompts templates that guide the agent's behavior during its execution. For a detailed understanding of how these prompts are structured and utilized, you can refer to our [Prompts Documentation](../Prompts/AgentPrompts.md). To view the specific prompts associated with the `ReflexionAgent`, see its [YAML File](../../../../src/agentforge/utils/installer/agents/ReflexionAgent.yaml).

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
from agentforge.agents.ReflexionAgent import ReflexionAgent
reflexion_agent = ReflexionAgent()
```

### Running the Agent

The `ReflexionAgent` can be invoked with optional parameters to cater to its specific role of reviewing responses:

- `Context`: A summary of previous actions.
- `Instruction`: Description of the task that corresponds to the respondent's answer.
- `Feedback`: The respondent's answer to reflect upon.

```python
reflection_result = reflexion_agent.run()
```

Even in the absence of these optional parameters, the agent will attempt to review the responses based on its inherited methods from the `Agent` class:

```python
reflection_result = reflexion_agent.run()
```

The `ReflexionAgent` is streamlined and flexible, capable of performing its review tasks with or without additional context.