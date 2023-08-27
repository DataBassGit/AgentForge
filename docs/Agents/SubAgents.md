# SubAgents and Method Overriding

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

## Persona Files and Prompts

Each agent gets its prompts based on its name and the associated [Persona File](./Persona.md). Simply by naming the subclass and creating the corresponding prompts, you can create a unique agent with default behaviors.

---

## Overriding Methods

If you need to customize the behavior of a SubAgent, you can override any of the inherited methods. This allows for flexibility in how the agent behaves without affecting the overall architecture.

### Example
```python
class NewAgent(Agent):

    def load_and_process_data(self, **kwargs):
        # Custom behavior here
        # ...
        
    def generate_prompt(self, **data):
        # Custom behavior here
        # ...
    
    def save_parsed_data(self, parsed_data):
        # Custom behavior here
        # ...
```

In this example, `NewAgent` overrides the `load_and_process_data`, `generate_prompt`, and `save_parsed_data` methods to implement custom behavior.

---

