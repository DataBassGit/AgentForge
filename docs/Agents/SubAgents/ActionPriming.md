# Action Priming Agent

## Overview

The `ActionPrimingAgent` is a specialized subagent that inherits from the [Agent](./Agent.md) superclass. Unlike the basic `ExecutionAgent`, this one overrides several methods to customize its behavior.

For more on the basics of creating subagents, see [SubAgents](./SubAgents.md).

---

## Class Definition and Additional Function

Firstly, there's an additional function `extract_metadata` used in this subagent:

```python
def extract_metadata(results):
    # extract the 'metadatas' key from results
    extracted_metadata = results['metadatas'][0][0]

    return extracted_metadata
```

Now, the class definition:

```python
class ActionPrimingAgent(Agent):

    def build_output(self, result, **kwargs):
        # ...
        
    def load_additional_data(self, data):
        # ...
        
    def load_tool(self, tool):
        # ...
        
    def save_parsed_data(self, parsed_data):
        pass
```

## Overridden Methods

### `build_output(self, result, **kwargs)`


This method formats the result by removing newline and tab characters. Then it converts the string to a Python object using `ast.literal_eval`.

```python
def build_output(self, result, **kwargs):
    formatted_result = result.replace('\n', '').replace('\t', '')
    payload = ast.literal_eval(formatted_result)

    return payload
```

---

### `load_additional_data(self, data)`

Adds 'objective' and 'task' to the data dictionary and displays the current task.

```python
def load_additional_data(self, data):
    # Add 'objective' to the data
    data['objective'] = self.agent_data.get('objective')
    data['task'] = self.load_current_task()['task']

    _show_task(data)
```

---

### `load_tool(self, tool)`

Queries the storage to load a specific tool and filters the result using `extract_metadata()`.

```python
def load_tool(self, tool):
    params = {
        "collection_name": 'Tools',
        "query": tool,
        "include": ["documents", "metadatas"]
    }

    results = self.storage.query_memory(params)
    filtered = extract_metadata(results)

    return filtered
```

---

### `save_parsed_data(self, parsed_data)`

This method is overridden but left empty so no data is saved to memory.

```python
def save_parsed_data(self, parsed_data):
    pass
```

---

## How to Use

Just like any other SubAgent, instantiate it:

```python
action_priming_agent = ActionPrimingAgent()
```