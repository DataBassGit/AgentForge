# Action Priming Agent

## Introduction

`ActionPrimingAgent` is a specialized agent that extends the generic `Agent` class. This agent is specifically designed for priming tools based on defined actions, it also performs customized loading of additional data, output building, and skips the saving of results to memory.

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
        
    def load_additional_data(self):
        # ...
        
    def save_result(self):
        #...
```

The `ActionPrimingAgent` is a specialized agent that inherits its core functionalities from the base `Agent` class. This allows it to utilize the foundational features and methods provided by the `Agent` class. Additionally, `ActionPrimingAgent` customizes its behavior by overriding specific methods from its parent class. Specifically, the methods `build_output`, `load_additional_data`, and `save_result` have been overridden to implement custom functionalities tailored to the needs of this particular agent.


---

## Overriden Agent Methods

### Load Additional Data
### `load_additional_data()`

**Purpose**: This method adds the current task to the agent's data dictionary.

**Workflow**:
1. Fetches the current task object using `self.functions.get_current_task()`.
2. Adds it to the `self.data['task']`.

```python
def load_additional_data(self):
    self.data['task'] = self.functions.get_current_task()['document']
```

>**Note:** In this case the `['document']` attribute is the text describing the task to be done as the actual task object has additional metadata attributes.

---

### Build Output
### `build_output()`

**Purpose**: This method formats the result and sets it as the agent's output.

**Workflow**:
1. Removes newlines and tabs from the result.
2. Attempts to evaluate the formatted result as a Python literal expression using `ast.literal_eval`..
3. Sets the evaluated result as the agent's output.

**Exception Handling**: Logs and raises an error if the evaluation fails.

```python
def build_output(self):
    try:
        formatted_result = self.result.replace('\n', '').replace('\t', '')
        self.output = eval(formatted_result)
    except Exception as e:
        self.logger.log(self.result, 'error')
        raise ValueError(f"\n\nError while building output for agent: {e}")
```

---

### Save Result
### `save_result()`

**Purpose**: Overrides the default behavior to prevent saving the result to memory.

**Workflow**: Does nothing as there's no need to save how a tool is primed.

```python
def save_result(self):
    pass
```

---

## How to Use

### Initialization

To utilize the `ActionPrimingAgent`, you first need to initialize it. This is done using the following line of code:

```python
action_priming_agent = ActionPrimingAgent()
```

### Running the Agent

Once the agent is initialized, you can invoke it to perform its specific tasks by calling the `run` method. This method requires certain parameters:

- `tool`: Represents the tool that needs to be primed.
- `tool_result`: Contains the results returned by the previous execution of the same or different tool. 

The `tool_result` parameter is particularly versatile. In the context of an action sequence, it holds the results from the previous tool execution, whether that's from the same tool or a different one. If this agent is priming the first tool in a sequence, or if the action consists of a single tool, `tool_result` can be set to `None`.

Here's how you would call the agent:

```python
payload = action_priming_agent.run(tool=tool, results=tool_result)
```

In this example, the `ActionPrimingAgent` receives a tool and the previous tool results, it will then return a `payload` which contains the tool in it's primed state ready to be executed.

> **Note**: For a more detailed explanation on how we use actions to string tools together in a sequence, please refer to our [Actions Documentation](../../Tools&Actions/ToolsActions.md) and this specific [Agent's Prompt.](../../../src/agentforge/utils/installer/agents/ActionPrimingAgent.json)

---