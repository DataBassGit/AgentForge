# Action Priming Agent

## Introduction

`ActionPrimingAgent` is a specialized agent that extends the base `Agent` class. This agent is specifically designed for priming tools based on defined actions, it also performs customized loading of additional data, output building, and skips the saving of results to memory.

Each agent, including the `ActionPrimingAgent`, is associated with a specific prompt `YAML` file which determines its interactions. This file contains a set of pre-defined prompts templates that guide the agent's behavior during its execution. For a detailed understanding of how these prompts are structured and utilized, you can refer to our [Prompts Documentation](../../Agents/AgentPrompts.md). To view the specific prompts associated with the `ActionPrimingAgent`, see its [YAML File](../../../src/agentforge/utils/installer/agents/PredefinedAgents/ActionPrimingAgent.yaml).

---

## Import Statements
```python
from agentforge.agent import Agent
from ast import literal_eval as eval
```

In this section, the necessary libraries and modules are imported for the functionality of the `ActionPrimingAgent`. The `Agent` class is imported from the `.agentforge/` directory, serving as the base class from which `ActionPrimingAgent` will inherit its core features. Additionally, the Python standard library `ast` (Abstract Syntax Trees) is imported to assist in specific parsing operations.

---

## Class Definition

```python
class ActionPrimingAgent(Agent):

    def build_output(self, result, **kwargs):
        # ...
        
    def save_result(self):
        #...
```

The `ActionPrimingAgent` is a specialized agent that inherits its core functionalities from the base `Agent` class. This allows it to utilize the foundational features and methods provided by the `Agent` class. Additionally, `ActionPrimingAgent` customizes its behavior by overriding specific methods from its parent class. Specifically, the methods `build_output` and `save_result` have been overridden to implement custom functionalities tailored to the needs of this particular agent.


---

## Overridden Agent Methods

---

### Build Output
### `build_output()`

**Purpose**: In this specific agent implementation, the `build_output` method is tailored to parse the result from the LLM, which is assumed to be in YAML format. The method transforms the raw YAML string into a structured format, thereby refining the agent's output for more sophisticated use cases. This custom implementation demonstrates how agents can be adapted to process and deliver outputs that meet specific operational or application requirements.

**Workflow**:
1. Utilizes a utility function, `parse_yaml_string`, designed to interpret a YAML formatted string and convert it into a structured Python object.
2. Sets the parsed structured object as the agent's output, enhancing the comprehensibility and utility of the data for downstream processes or interfaces.

**Exception Handling**:
- In case of an error during the parsing process, the method logs the error using a specialized logger method `parsing_error`, which records the raw result and the exception details.
- Subsequently, the method re-raises the exception to signal the occurrence of a critical issue that needs attention, ensuring that error handling mechanisms can respond appropriately.

```python
def build_output(self):
	"""
	Overrides the build_output method from the Agent class to parse the result string into a structured format.
	This method attempts to parse the result (assumed to be in YAML format) using the agent's utility functions
	and sets the parsed output as the agent's output.

	Raises:
		Exception: If there's an error during parsing, it logs the error and re-raises the exception for
		further handling. This approach ensures that any parsing issues are immediately flagged and can be
		addressed in a timely manner.
	"""
	try:
		# The 'parse_yaml_string' method takes a YAML formatted string and returns a structured object
		self.output = self.functions.agent_utils.parse_yaml_string(self.result)
	except Exception as e:
		self.logger.parsing_error(self.result, e)  # Custom logging for parsing errors
		raise  # Re-raises the exception to ensure it's not silently ignored
```

> **Note**: This override emphasizes the importance of custom processing capabilities within agents, allowing them to tailor their output processing to fit specific data formats and requirements. By converting YAML formatted strings into structured objects, this method significantly enhances the usability and integration capabilities of the agent's output.

---

### Save Result
### `save_result()`

**Purpose**: Overrides the default behavior to prevent saving the result to memory.

**Workflow**: Does nothing as there's no need to save how a tool is primed.

```python
def save_result(self):
    """
    Overrides the save_result method from the Agent class to provide custom behavior for saving results.
    
    For this custom agent, the method is intentionally left empty to bypass the default saving mechanism,
    indicating that this agent does not require saving its results in the same manner as the base Agent class.
    """
    pass
```

---

## How to Use

### Initialization

To utilize the `ActionPrimingAgent`, you first need to initialize it. This is done using the following line of code:

```python
from agentforge.agents.ActionPrimingAgent import ActionPrimingAgent
action_priming_agent = ActionPrimingAgent()
```

### Running the Agent

Once the agent is initialized, you can invoke it to perform its specific tasks by calling the `run` method. This method requires certain parameters:

- `tool`: Represents the tool that needs to be primed.
- `tool_result`: Contains the results returned by the previous execution of the same or different tool. 

The `tool_result` parameter is particularly versatile. In the context of an action sequence, it holds the results from the previous tool execution, whether that's from the same tool or a different one. If this agent is priming the first tool in a sequence, or if the action consists of a single tool, `tool_result` can be set to `None`.

Here's how you would call the agent:

```python
payload = action_priming_agent.run()
```

In this example, the `ActionPrimingAgent` receives a tool and the previous tool results, it will then return a `payload` which contains the tool in it's primed state ready to be executed.

> **Note**: For a more detailed explanation on how we use actions to string tools together in a sequence, please refer to our [Actions Documentation](../../ToolsAndActions/Overview.md)

---