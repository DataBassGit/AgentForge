# Custom Agents Guide

## Overview

Creating a Custom Agent entails building a new class that inherits the `Agent` base class. This endows your class with the default behaviors defined in the `Agent` class. 

To create a custom agent, you'll simply need to create a new `Python` class that inherits from the base `Agent` class. Once you've achieved this, start customizing by overriding the default methods to align them with your specific requirements. 

Additionally, remember to create a corresponding `YAML` file for your agent's prompts. The filename should mirror your agent class name and the YAML file is case-sensitive. With these steps, you've successfully created a customized agent tailored to your specific need!

### Example

```python
from agentforge.agent import Agent

class NewAgent(Agent): 
    pass
```
In this example, `NewAgent` is a mirror of its `Agent` base class template as it doesn't override any methods. 

To utilize this new agent in a different script, import it from its location and provide it the necessary parameters:
```python
from your_custom_agent_location.NewAgent import NewAgent

new_agent = NewAgent()
params = { # ... Dictionary Containing Parameters If Needed by the Agent ... }
results = new_agent.run(**params)
```

---

## Persona Files

In **AgentForge**, **Personas** are utilized to encapsulate the information accessible to the agents. They are a crucial tool to define the body of knowledge that an agent can draw from during its execution. 

A **Persona** is not confined to defining the personality of an agent. Instead, it serves as a store for any kind of information – from data related to a specific subject to general world facts – that the agents might need for providing comprehensive responses to users' input.

Personas are defined using .yaml files within the `.agentforge/personas` folder. You can create as many persona files as needed, allowing you to structure your agents' knowledge in an organized manner and distribute information across them as required.

Each custom agent can be linked to a specific persona file, providing it with the desired set of information. For more details on how to structure the `Persona YAML File`, check out the [Persona Documentation](../Personas/Personas.md).

---

## Agent Prompt Templates

Each custom agent has its own `YAML` file located in the `./agentforge/agents/` folder. This file contains the specific prompt templates used by that agent. The naming convention is crucial here: the filename must match the class name of your agent, and is case-sensitive. So, if you've got a custom agent class named `NewAgent`, your `YAML` file should be `NewAgent.yaml`.

By adhering to this naming convention and populating your `YAML` file with prompt templates, you can create a unique custom agent that inherits default behaviors from the `Agent` base class but also has its own tailored interactions. This approach greatly simplifies and streamlines the agent creation process, making it easier for you to focus on what your agent should do, rather than how it should do it.

For more details on how to structure your agent's prompts, you can refer to the [Agent Prompts Documentation](AgentPrompts.md).

---

## Overriding Agent Methods

If you need to customize the behavior of a custom agent, you can override any of the inherited [Agent Methods](AgentMethods.md). This allows for flexibility in how the agent behaves without affecting the overall architecture.

### Example
```python
class NewAgent(Agent):

    def process_data(self):
        # Custom behavior here
        # ...
     
    
    def save_result(self):
        # Custom behavior here
        # ...
```

In this example, `NewAgent` overrides the `process_data` and `save_result` methods to implement custom behavior. When a method is overridden, the agent's `run` method will automatically call the new version instead of the default one. Want the best of both worlds? You can actually call the default method within your overridden version using the `super()` function. This way, you can extend the default behavior while adding your own special sauce.

---