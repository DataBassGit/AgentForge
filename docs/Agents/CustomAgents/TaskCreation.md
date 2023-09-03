# Task Creation Agent

## Overview

The `TaskCreationAgent` is your go-to subagent for task management. From creating to saving tasks, it's got you covered. This agent inherits from the [Agent](./Agent.md) superclass.

Learn more about SubAgents [here](./SubAgents.md).

---

## Class Definition

```python
from .agent import Agent

class TaskCreationAgent(Agent):

    def load_additional_data(self, data):
        # ...
        
    def parse_result(self, result, **kwargs):
        # ...
        
    def save_parsed_data(self, parsed_data):
        # ...
        
    def save_tasks(self, task_list):
        # ...
        
    def build_output(self, parsed_data):
        pass
```

## Overridden Methods

### `load_additional_data(self, data)`

Sets the 'goal' in data if not already present.

```python
def load_additional_data(self, data):
    if data['goal'] is None:
        data['goal'] = self.agent_data.get('objective')
```

---

### `parse_result(self, result, **kwargs)`

Parses the result to create a list of tasks.

```python
def parse_result(self, result, **kwargs):
    new_tasks = result.split("\n")

    result = [{"Description": task_desc} for task_desc in new_tasks]
    filtered_results = [task for task in result if task['Description'] and task['Description'][0].isdigit()]

    try:
        order_tasks = [{
            'Order': int(task['Description'].split('. ', 1)[0]),
            'Description': task['Description'].split('. ', 1)[1]
        } for task in filtered_results]
    except Exception as e:
        raise ValueError(f"\n\nError ordering tasks. Error: {e}")

    return order_tasks
```

---

### `save_parsed_data(self, parsed_data)`

Saves the parsed tasks.

```python
def save_parsed_data(self, parsed_data):
    self.save_tasks(parsed_data)
```

---

### `save_tasks(self, task_list)`

Clears the existing tasks and saves the new ones.

```python
def save_tasks(self, task_list):
    collection_name = "Tasks"
    self.storage.delete_collection(collection_name)

    metadatas = [{
        "Status": "not completed",
        "Order": task["Order"],
        "Description": task["Description"],
        "List_ID": str(uuid.uuid4())
    } for task in task_list]

    task_orders = [str(task["Order"]) for task in task_list]
    task_desc = [task["Description"] for task in task_list]

    params = {
        "collection_name": collection_name,
        "ids": task_orders,
        "data": task_desc,
        "metadata": metadatas,
    }

    self.storage.save_memory(params)
```

---

### `build_output(self, parsed_data)`

Doesn't do anything for this agent as the summarization is saved to memory.

```python
    def build_output(self, parsed_data):
        pass
```

---

## How to Use

Create an instance like so:

```python
task_creation_agent = TaskCreationAgent()
```

---