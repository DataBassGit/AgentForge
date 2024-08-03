# Action Selection Agent

## Introduction

The `ActionSelectionAgent` extends the foundational `Agent` class with specialized capabilities for action selection based on current tasks and parameters.

The `ActionSelectionAgent` is configured through a specific YAML file that dictates its interactions through predefined prompt templates. These templates are crucial for guiding the agent's behavior during execution. For details on prompt structure and usage, refer to the [Prompts Documentation](../../Agents/AgentPrompts.md). The specific prompts for the `ActionSelectionAgent` can be found in its [YAML](../../../src/agentforge/setup_files/agents/ModuleAgents/ActionSelectionAgent.yaml) file.

---

## Class Definition

```python
from agentforge.agent import Agent


class ActionSelectionAgent(Agent):
    pass
```

This import statement allows the `ActionSelectionAgent` to inherit features and methods from the base `Agent` class, facilitating the use of foundational functionalities. This agent does not require any custom methods to perform its task.

---

## How to Use

### Running the Agent

To utilize the `ActionSelectionAgent`, you first need to initialize it. You can then invoke it to perform action selection based on current tasks and parameters by calling the `run` method. This method requires the following parameters:

- `objective`: The main objective that needs to be achieved.
- `action_list`: A list of available actions to choose from.
- `context`: Any relevant context that might influence the action selection. - `Optional`

Here's how you would call the agent:

```python
from agentforge.agents.ActionSelectionAgent import ActionSelectionAgent
action_selection_agent = ActionSelectionAgent()

selected_action = action_selection_agent.run(objective=objective, action_list=action_list, context=context)
```

In this example, the `ActionSelectionAgent` receives an objective, a list of available actions, and optional context. It will then return a `selected_action`, which is the most appropriate action for achieving the objective.

---

## Prompts

The `ActionSelectionAgent` utilizes a set of predefined prompts to guide its behavior. These prompts are structured as follows:

```yaml
Prompts:
  System: |+
    Your task is to decide whether the following objective requires the use of an action:

    {objective}

  Actions: |+
    Consider the following actions available, including the option to choose "Nothing" if no action is required:

    ```
    {action_list}
    ```

  Instruction: |+
    Review the actions in light of the main objective provided.

    You must recommend the most effective action from the list, or "Nothing" if no action is necessary.

    Provide your reasoning and any relevant feedback.

    Strictly adhere to the response format below. Only provide the selected action, reasoning, and feedback without any additional commentary outside of the allowed fields in the format.

  Response: |-
    RESPONSE FORMAT:
    ```yaml
    action: <selected action>
    reasoning: <reasoning for the selected action>
    ```

Persona: default
```

The agent uses these prompts to systematically evaluate the objective and the list of available actions, ultimately selecting the most appropriate action or determining that no action is necessary.