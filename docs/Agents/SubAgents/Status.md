# Status Agent

## Overview

Meet the `StatusAgent`, a specialized subagent that inherits from the [Agent](./Agent.md) superclass. This subagent focuses on updating and logging task statuses.

For the uninitiated, read about subagents here: [SubAgents](./SubAgents.md).

---

## Class Definition

```python
from .agent import Agent, _set_task_order, _show_task

class StatusAgent(Agent):

    def parse_result(self, result, **kwargs):
        # ...
        
    def load_additional_data(self, data):
        # ...
        
    def save_status(self, parsed_data):
        # ...
        
    def save_parsed_data(self, parsed_data):
        # ...
```

## Overridden Methods

### `parse_result(self, result, **kwargs)`

Extracts the task status and reason from the result. Optionally logs completed tasks.

```python
def parse_result(self, result, **kwargs):
    status = result.split("Status: ")[1].split("\n")[0].lower().strip()
    reason = result.split("Reason: ")[1].rstrip()
    task = {
        "task_id": kwargs['data']['current_task']['id'],
        "description": kwargs['data']['current_task']['metadata']['Description'],
        "status": status,
        "order": kwargs['data']['current_task']['metadata']['Order'],
    }

    # Log results
    if status == "completed":
        filename = "./Logs/results.txt"
        separator = "\n\n\n\n---\n\n\n\n"
        task_to_append = "\nTask: " + kwargs['data']['current_task']['metadata']['Description'] + "\n\n"
        text_to_append = kwargs['data']['task_result']
        with open(filename, "a") as file:
            file.write(separator + task_to_append + text_to_append)

    return {
        "task": task,
        "status": status,
        "reason": reason,
    }
```

---

### `load_additional_data(self, data)`


Adds 'objective' and 'task' to the data dictionary, similar to other SubAgents.

```python
def load_additional_data(self, data):
    data['objective'] = self.agent_data.get('objective')
    data['task'] = self.load_current_task()['task']

    _show_task(data)
```

---

### `save_status(self, parsed_data)`

Saves the task status to the storage.

```python
def save_status(self, parsed_data):
    status = parsed_data["status"]
    task_id = parsed_data["task"]["task_id"]
    text = parsed_data["task"]["description"]
    task_order = parsed_data["task"]["order"]+

    params = {
        'collection_name': "Tasks",
        'ids': [task_id],
        'data': [text],
        'metadata': [{"Status": status, "Description": text, "Order": task_order}]
    }

    self.storage.save_memory(params)
```

---

### `save_parsed_data(self, parsed_data)`

Calls `save_status` to save the parsed data.

```python
def save_parsed_data(self, parsed_data):
    self.save_status(parsed_data)
```

---

## How to Use

To make use of `StatusAgent`, simply instantiate it:

```python
status_agent = StatusAgent()
```