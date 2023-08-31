# Action Selection Agent

## Overview

The `ActionSelectionAgent` is another specialized subagent derived from the [Agent](./Agent.md) superclass. This one is more focused on action selection and adds its own twist to the methods for parsing results and loading additional data.

For a primer on subagents, hop over to [SubAgents](./SubAgents.md).

---

## Class Definition

```python
class ActionSelectionAgent(Agent):

    def parse_result(self, result, **kwargs):
        # ...
        
    def load_additional_data(self, data):
        # ...
        
    def save_parsed_data(self, parsed_data):
        pass
```

## Overridden Methods

### `parse_result(self, result, **kwargs)`

This method has been customized to include a frustration threshold which adjusts the query parameters when searching the storage.

```python
def parse_result(self, result, **kwargs)
    frustration = kwargs['data'].get('frustration', 0)
    max_threshold = 0.8
    threshold = 0.3 + frustration
    threshold = min(threshold, max_threshold)

    threshold = 0.99

    print(f'\nFrustration Threshold: {threshold}')

    params = {
        "collection_name": 'Actions',
        "query": result,
        "threshold": threshold,
        "num_results": 1,  # optional
    }

    search = self.storage.search_storage_by_threshold(params)

    return search
```

---

### `load_additional_data(self, data)`

Adds 'objective' and 'task' to the data dictionary and displays the current task.

```python
def load_additional_data(self, data):
    # Add 'objective' to the data
    data['objective'] = self.agent_data.get('objective')
    data['task'] = self.functions.get_current_task()['document']

    _show_task(data)
```

---

### `save_parsed_data(self, parsed_data)`

This method is overridden but intentionally left empty so no data is saved to memory.

```python
def save_parsed_data(self, parsed_data):
    pass
```

---

## How to Use

To use the `ActionSelectionAgent`, instantiate it like so:

```python
action_selection_agent = ActionSelectionAgent()
```
