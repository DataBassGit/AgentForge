# SubAgent Creation

---

## Creating SubAgents

Creating a SubAgent is straightforward. A `SubAgent` class only needs to inherit from the `Agent` superclass. By doing so, it gains access to all the default behaviors defined in the `Agent` class.

### Example
```python
from .agent import Agent

class NewAgent(Agent):
    pass
```

In this example, `NewAgent` will behave exactly like its superclass `Agent` since it doesn't override any methods.

---

## Persona Files

Each bot or architecture is associated with a persona, which is defined in a Persona JSON file located in the `./agentforge/personas` folder. The persona file contains the name of the persona (bot) along with its default data. For more details on how to structure the Persona JSON File, check out the [Persona Documentation](../Persona/Persona.md).

> **Note**: We're planning on expanding the functionality of personas. Soon, you'll be able to select from multiple persona files, define specific personality traits, and possibly more. So, keep an eye out for that; exciting stuff is on the way!

---

## Agent Prompts

Each agent (sub-agent) has its own JSON file located in the `./agentforge/agents/` folder. This file contains the specific prompts used by that agent. The naming convention is crucial here: the filename must match the class name of your agent, but in lowercase. So, if you've got a sub-agent class named `NewAgent`, your JSON file should be `newagent.json`.

By adhering to this naming convention and populating your JSON file with prompts, you can create a unique sub-agent that inherits default behaviors from the superclass but also has its own tailored interactions. This approach greatly simplifies and streamlines the agent creation process, making it easier for you to focus on what your agent should do, rather than how it should do it.

For more details on how to structure your agent's prompts, you can refer to the [Agent Prompts Documentation](Prompts/AgentPrompts.md).

---

## Overriding Agent Methods

If you need to customize the behavior of a SubAgent, you can override any of the inherited [methods](AgentMethods.md). This allows for flexibility in how the agent behaves without affecting the overall architecture.

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

In this example, `NewAgent` overrides the `process_data` and `save_result` methods to implement custom behavior.

---

## Examples of Custom SubAgents

For a deeper understanding of how you can take advantage of method overriding to implement custom behaviors, we've provided some examples from our default sub-agents. These examples showcase how a `SubAgent` class can override the default methods to perform specialized tasks.

- [Action Priming Agent](SubAgents/ActionPrimingAgent.md)
- (NOTE TO DEVS: NEED TO DOCUMENT THE REST)

Feel free to explore these examples to get inspired and learn more about the flexibility and power of our agent architecture.

---
