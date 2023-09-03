# Custom Agents

---

## Creating Custom Agents

Creating a Custom Agent is pretty straightforward. A  class only needs to inherit from the `Agent` superclass. By doing so, it gains access to all the default behaviors defined in the `Agent` class.

Creating a Custom Agent from the base class is pretty straightforward. All you need to do is create a new `Python` class that inherits from the base `Agent` class. 

Once that's set up, you have the freedom to override any of the default methods to fit your specific needs. Don't forget to create a corresponding `JSON` file for your agent's prompts; it should be named after your agent class and is case-sensitive. And just like that, you've got yourself a fully customized agent ready to tackle whatever tasks you throw its way!

### Example
```python
from agentforge.agent import Agent

class NewAgent(Agent):
    pass
```

In this example, `NewAgent` will behave exactly like its `Agent` base class since it doesn't override any methods.

---

## Persona Files

Each bot or architecture is associated with a persona, which is defined in a `Persona JSON file` located in the `./agentforge/personas` folder. The persona file contains all the data related to the persona of the Cognitive Architecture (bot). For more details on how to structure the `Persona JSON File`, check out the [Persona Documentation](../Personas/Personas.md).

> **Note**: Personas are **NOT** currently implemented, right now it is simply setting the groundwork for future implementation. Soon, you'll be able to select from multiple persona files, define specific personality traits, and possibly more. So, keep an eye out for that; exciting stuff is on the way!

---

## Agent Prompt Templates

Each custom agent has its own `JSON` file located in the `./agentforge/agents/` folder. This file contains the specific prompt templates used by that agent. The naming convention is crucial here: the filename must match the class name of your agent, and is case-sensitive. So, if you've got a custom agent class named `NewAgent`, your `JSON` file should be `NewAgent.json`.

By adhering to this naming convention and populating your `JSON` file with prompt templates, you can create a unique custom agent that inherits default behaviors from the `Agent` base class but also has its own tailored interactions. This approach greatly simplifies and streamlines the agent creation process, making it easier for you to focus on what your agent should do, rather than how it should do it.

For more details on how to structure your agent's prompts, you can refer to the [Agent Prompts Documentation](Prompts/AgentPrompts.md).

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

## Examples of Custom Agents

For a deeper understanding of how you can take advantage of method overriding to implement custom behaviors, we've provided some examples from our default custom agents. These examples showcase how a custom agent can override the default methods to perform specialized tasks.

- [Action Priming Agent](SubAgents/ActionPrimingAgent.md)
- (NOTE TO DEVS: NEED TO DOCUMENT THE REST)

Feel free to explore these examples to get inspired and learn more about the flexibility and power of our agent framework.

---
