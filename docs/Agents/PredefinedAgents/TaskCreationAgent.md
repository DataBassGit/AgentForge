# Task Creation Agent

## Introduction

The `TaskCreationAgent` is a specialized agent that extends from the base `Agent` class. It's designed with a primary role of creating and managing task lists based on given objectives. These tasks are then stored in memory, ready for other agents, forming part of the same cognitive architecture, to pick up and execute. The agent retrieves its objective from memory, ensuring a seamless integration with other parts of the system.

Each agent, including the `TaskCreationAgent`, is associated with a specific prompt `YAML` file which determines its interactions. This file contains a set of pre-defined prompt templates that guide the agent's behavior during its execution. For a comprehensive understanding of how these prompts are structured and utilized, you can refer to our [Prompts Documentation](../AgentPrompts.md). To view the specific prompts associated with the `TaskCreationAgent`, see its [YAML File](../../../src/agentforge/utils/installer/agents/TaskCreationAgent.yaml).

---

## Import Statements

```python
from agentforge.agent import Agent
import uuid
```

For the `TaskCreationAgent` to function correctly, it imports the foundational `Agent` class from the `.agentforge/` directory. This gives it access to the core features and methods provided by the `Agent` class. Moreover, the `uuid` library is imported to generate unique identifiers for the created tasks.

---

## Class Definition

```python
class TaskCreationAgent(Agent):

    def parse_result(self):
        # ...
        
    def save_result(self):
        # ...
    
    def save_tasks(self, task_list):
        # ...
    
    def build_output(self):
        # ...
```

The `TaskCreationAgent` class is an extension of the `Agent` base class. While it capitalizes on the foundational features of the `Agent` class, it also introduces specific methods to handle task creation, parsing, storage, and output building. This makes it adept at crafting task lists and ensuring they're stored appropriately.

---

## Agent Methods

### Parse Result
#### `parse_result()`

**Purpose**: Parses the result to extract and format tasks.

**Workflow**:
1. Splits the result into individual tasks.
2. Filters and orders tasks based on their description.
3. Returns the ordered tasks.

```python
def parse_result(self):
    new_tasks = self.result.split("\n")

    result = [{"Description": task_desc} for task_desc in new_tasks]
    filtered_results = [task for task in result if task['Description'] and task['Description'][0].isdigit()]

    try:
        ordered_tasks = [{
            'Order': int(task['Description'].split('. ', 1)[0]),
            'Description': task['Description'].split('. ', 1)[1]
        } for task in filtered_results]
    except Exception as e:
        raise ValueError(f"\n\nError ordering tasks. Error: {e}")

    self.result = ordered_tasks
```

---

### Save Result
#### `save_result()`

**Purpose**: Saves the parsed tasks to memory.

**Workflow**:
1. Calls the `save_tasks` method with the parsed task list.

```python
def save_result(self):
    self.save_tasks(self.result)
```

---

### Save Tasks
#### `save_tasks(task_list)`

**Purpose**: Stores a list of tasks in memory with unique identifiers.

**Workflow**:
1. Deletes any existing tasks from memory.
2. Generates metadata for each task.
3. Constructs and saves each task to memory with its metadata.

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

### Build Output
#### `build_output()`

**Purpose**: Overrides the default behavior to prevent building an output since this agent's primary function is to save tasks to memory.

**Workflow**: Does nothing.

```python
def build_output(self):
    pass
```

---

## How to Use

### Initialization

To employ the `TaskCreationAgent`, start by initializing it:

```python
from agentforge.agents.TaskCreationAgent import TaskCreationAgent
task_creation_agent = TaskCreationAgent()
```

### Running the Agent

Invoke the `run` method of the `TaskCreationAgent` to allow it to craft and save tasks based on a given objective:

```python
task_creation_agent.run()
```

This invocation enables the agent to retrieve an objective from memory, craft a list of tasks, and save them. These stored tasks are then readily available for other agents within the same cognitive architecture to act upon.

---