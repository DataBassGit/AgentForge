# Custom Agents in AgentForge

## Overview
This example demonstrates how to build and implement custom agents within the AgentForge framework. By leveraging the extensible design of AgentForge, you can add unique functionalities to your agents while still benefiting from the core capabilities of the framework. 

## How it Works

### Importing the `Agent` Superclass
Custom agents are created by subclassing the `Agent` superclass from the AgentForge library. This enables them to inherit the functionalities of the default agents, such as managing tasks and handling results. The custom agents can then be modified to meet the specific requirements of your application.

Here is an example where we import the `Agent` superclass in our custom agent:

```python
from agentforge.agent import Agent

class TestAgent(Agent):
    def save_result(self):
        pass
```

### Overriding Functions
In this example, we override the `save_result` function of the `Agent` superclass. By default, this function would save the agent's results to some storage medium. However, in this case, we've overridden it to do nothing (`pass`), essentially disabling the data saving feature for this custom agent.

### Configuration JSON
Every agent uses a JSON file to define its prompts, which are the set of questions or instructions the agent uses to interact with the user or perform tasks. In this example, the JSON file `TestAgent.json` contains various prompt templates and variables that can be used by the agent.

## Example Usage

### Main Script: `customagents.py`
Here's how you can use the custom agent:

```python
from customagents.TestAgent import TestAgent
from agentforge.utils.function_utils import Functions

var = TestAgent()
string = "testing 123"
functions = Functions()

result = var.run(context=string)
functions.printing.print_result(result, "Test Results")
```

This main script imports our custom `TestAgent`, sets up a context ("testing 123"), and then runs the agent with this context. The results are then printed out.

## Conclusion
Creating custom agents in AgentForge is as simple as subclassing the built-in `Agent` class and modifying or extending its functionalities as needed. This way, you can easily tailor the behavior of agents to better fit your specific requirements.

Feel free to extend, modify, or override more functionalities as your project grows. The AgentForge framework is designed to be as flexible and extensible as possible, allowing for a wide range of applications.