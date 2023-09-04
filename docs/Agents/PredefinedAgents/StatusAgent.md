# Status Agent

## Introduction

The `StatusAgent` is a specialized agent that inherits from the base `Agent` class. It focuses on managing and updating the status of tasks based on the results obtained. This agent provides methods to load task data, parse the result for status and reasons, log completed tasks, and save the updated status to memory.

As with other agents, the `StatusAgent` is associated with a specific prompt `JSON` file which guides its interactions. This file contains a set of pre-defined prompt templates that dictate the agent's behavior. For an in-depth understanding of how these prompts are structured and used, refer to our [Prompts Documentation](../Prompts/AgentPrompts.md). To view the specific prompts associated with the `StatusAgent`, see its [JSON File](../../../src/agentforge/utils/installer/agents/StatusAgent.json).

---

## Import Statements
```python
from agentforge.agent import Agent
```

The `StatusAgent` imports the fundamental `Agent` class from the `.agentforge/` directory, allowing it to utilize the core features and methods provided by the `Agent` class.

---

## Class Definition

```python
class StatusAgent(Agent):

    def load_additional_data(self):
        # ...
    
    def parse_result(self, **kwargs):
        # ...

    def save_status(self):
        # ...
    
    def save_result(self):
        # ...
```

The `StatusAgent` class is derived from the `Agent` base class. By doing so, it can leverage the foundational features and methods of the `Agent` class. However, to fit its unique role, the `StatusAgent` overrides methods such as `load_additional_data`, `parse_result`, `save_status`, and `save_result`.

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

---

### Parse Result
#### `parse_result()`

**Purpose**: Parses the result to extract the task's status and reason.

**Workflow**:
1. Extracts the status and reason from the result.
2. Constructs a `task` dictionary with task details.
3. Logs the task details if the status is "completed".
4. Sets the parsed data to `self.result`.

```python
def parse_result(self, **kwargs):
    status = self.result.split("Status: ")[1].split("\n")[0].lower().strip()
    reason = self.result.split("Reason: ")[1].rstrip()

    task = {
        "task_id": self.data['current_task']['id'],
        "description": self.data['current_task']['metadata']['Description'],
        "status": status,
        "order": self.data['current_task']['metadata']['Order'],
    }

    # Log results
    if status == "completed":
        filename = "./Logs/results.txt"
        separator = "\n\n\n\n---\n\n\n\n"
        task_to_append = "\nTask: " + self.data['current_task']['metadata']['Description'] + "\n\n"
        text_to_append = self.data['task_result']
        with open(filename, "a") as file:
            file.write(separator + task_to_append + text_to_append)

    self.result = {
        "task": task,
        "status": status,
        "reason": reason,
    }
```

---

### Save Status
#### `save_status()`

**Purpose**: Updates the task's status in memory.

**Workflow**:
1. Constructs the parameters with the updated task status and other details.
2. Calls `self.storage.save_memory(params)` to save the updated status.

```python
def save_status(self):
    status = self.result["status"]
    task_id = self.result["task"]["task_id"]
    text = self.result["task"]["description"]
    task_order = self.result["task"]["order"]

    params = {
        'collection_name': "Tasks",
        'ids': [task_id],
        'data': [text],
        'metadata': [{"Status": status, "Description": text, "Order": task_order}]
    }

    self.storage.save_memory(params)
```
---

### Save Result
#### `save_result()`

**Purpose**: Calls the `save_status` method to save the task's status.

**Workflow**:
1. Invokes the `save_status` method.

```python
def save_result(self):
    self.save_status()
```

---

## How to Use

### Initialization

To employ the `StatusAgent`, you first need to initialize it:

```python
from agentforge.agents.StatusAgent import StatusAgent
status_agent = StatusAgent()
```

### Running the Agent

After initialization, the `StatusAgent` is designed to manage and update the status of tasks based on the results obtained from previous agent executions or other processes.

Here's an example of how the `StatusAgent` is used to check and update tasks statuses:

```python
# The StatusAgent is invoked with the task result obtained from a previous agent's execution
status_results = self.status_agent.run(task_result)
task['status'] = status_results['status']
task['reason'] = status_results['reason']
```

In this example, the `StatusAgent` analyzes a `task_result` variable, which contains the results of a task that a preceding agent executed. The agent then determines if the task has been completed or not, and updates the status and reason accordingly.
