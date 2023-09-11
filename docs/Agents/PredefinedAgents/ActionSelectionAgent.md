# Action Selection Agent

## Introduction

The `ActionSelectionAgent` is another specialized agent that derives its capabilities from the foundational `Agent` class. This agent is primarily responsible for selecting actions based on the current task and other parameters. It also overrides some default methods to tailor its behavior to this specific purpose.

Each agent, including the `ActionSelectionAgent`, is associated with a specific prompt `JSON` file which determines its interactions. This file contains a set of pre-defined prompts templates that guide the agent's behavior during its execution. For a detailed understanding of how these prompts are structured and utilized, you can refer to our [Prompts Documentation](../Prompts/AgentPrompts.md). To view the specific prompts associated with the `ActionSelectionAgent`, see its [JSON File](../../../src/agentforge/utils/installer/agents/ActionSelectionAgent.json).

---

## Import Statements
```python
from agentforge.agent import Agent
```

The `ActionSelectionAgent` imports its base `Agent` class from the `.agentforge/` directory. This allows the `ActionSelectionAgent` to inherit the essential features and methods defined in the `Agent` class.

---

## Class Definition

```python
class ActionSelectionAgent(Agent):

    def load_additional_data(self):
        # ...
        
    def parse_result(self):
        # ...
        
    def save_result(self):
        #...
```

The `ActionSelectionAgent` class inherits from the `Agent` base class. This enables it to utilize the foundational features and methods provided by the `Agent` class. Additionally, it overrides the methods `load_additional_data`, `parse_result`, and `save_result` to implement specific functionalities for action selection.

---

## Overridden Agent Methods

### Load Additional Data
#### `load_additional_data()`

**Purpose**: Adds the current task document to the agent's data dictionary.

**Workflow**:
1. Retrieves the current task using `self.functions.get_current_task()`.
2. Adds it to `self.data['task']`.

```python
def load_additional_data(self):
    self.data['task'] = self.functions.get_current_task()['document']
```

>**Note:** In this case the `['document']` attribute is the text describing the task to be done as the actual task object has additional metadata attributes.

---

### Parse Result
#### `parse_result()`

**Purpose**: Parses the results and performs a storage search based on specific thresholds to determine the action to be taken.

**Workflow**:
1. Retrieves the value of `frustration` from the agent's data.
2. Sets and calculates thresholds.
3. Calls the storage search function with the defined parameters and thresholds.

```python
def parse_result(self):
    frustration = self.data.get('frustration', 0)
    max_threshold = 0.8
    threshold = 0.3 + frustration
    threshold = min(threshold, max_threshold)

    params = {
        "collection_name": 'Actions',
        "query": self.result,
        "threshold": threshold,
        "num_results": 1,  # optional
    }

    self.result = self.storage.search_storage_by_threshold(params)
```

>**Note:** The current implementation of threshold for frustration needs to be improved as it is currently hard coded. 

---

### Save Result
#### `save_result()`

**Purpose**: Overrides the default behavior to prevent saving the result to memory.

**Workflow**: Does nothing, as this agent does not require the result to be saved.

```python
def save_result(self):
    pass
```

---

## How to Use

### Initialization

To use `ActionSelectionAgent`, you first need to initialize it:

```python
from agentforge.agents.ActionSelectionAgent import ActionSelectionAgent
action_selection_agent = ActionSelectionAgent()
```

### Running the Agent

To invoke the agent's specific tasks, call its `run` method:

```python
selected_action = action_selection_agent.run()
```

Here, `current_task` and `current_frustration` are variables that contain the task to be performed and the current frustration level, respectively. The agent will return a selected action to accomplish the task.

> **Note**: For a more detailed explanation of actions and how they play a role in this architecture, please refer to our [Actions Documentation](../../Tools&Actions/ToolsActions.md).

---