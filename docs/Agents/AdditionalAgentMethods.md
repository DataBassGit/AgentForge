# Additional Agent Methods

Welcome to the in-depth section of the Agent Methods documentation! Here, we'll explore the additional methods within the `Agent` class that weren't covered in the main [Agent Methods Page](AgentMethods.md). These methods are for those who wish to dig deeper and understand the nitty-gritty details of the agent's functionalities.


These additional methods are static methods found in the `agent.py` file but not in the actual `Agent` class. These methods are not meant to be overridden and serve specific purposes within the framework.

---

## Calculate Next Task Order

### `_calculate_next_task_order(this_task_order)`

**Purpose**: Calculates the order of the next task based on the current task order.

**Arguments**:
- `this_task_order`: The order number of the current task.

**Returns**: 
- The order number for the next task.

```python
def _calculate_next_task_order(this_task_order):
    return int(this_task_order) + 1
```

---

## Handle Prompt Type

### `_handle_prompt_type(prompts, prompt_type)`

**Purpose**: Handles each type of prompt and returns the template and variables.

**Arguments**:
- `prompts`: The prompt data dictionary.
- `prompt_type`: The type of the prompt to handle.

**Returns**: 
- A list of tuples containing the template and variables for the specified prompt type.

```python
def _handle_prompt_type(prompts, prompt_type):
    prompt_data = prompts.get(prompt_type, {})
    if prompt_data:
        return [(prompt_data['template'], prompt_data['vars'])]
    return []
```

---

## Load Agent Data

### `_load_agent_data(agent_name)`

**Purpose**: Loads data specific to a particular agent, including the agent's API, parameters, and persona data.

**Arguments**:
- `agent_name`: The name of the agent for which the data is being loaded.

**Returns**: 
- A dictionary containing data specific to the agent.

**Workflow**:
1. Load persona data using the `config.persona()` function.
2. Retrieve specific and default agent data from the persona data.
3. Initialize `agent_data` dictionary with relevant fields like API, Params, etc.

```python
def _load_agent_data(agent_name):
    # Load persona data
    persona_data = config.persona()

    agent = persona_data[agent_name]
    defaults = persona_data['Defaults']

    api = agent.get('API', defaults['API'])
    params = agent.get('Params', defaults['Params'])

    # Initialize agent data
    agent_data: Dict[str, Any] = dict(
        name=agent_name,
        llm=config.get_llm(api, agent_name),
        objective=persona_data['Objective'],
        prompts=agent['Prompts'],
        params=params,
        storage=StorageInterface().storage_utils,
    )

    return agent_data
```

---

## Remove Prompt If None

### `remove_prompt_if_none(prompts, kwargs)`

**Purpose**: Removes prompts that have missing or `None` variables.

**Arguments**:
- `prompts`: The prompt data dictionary.
- `kwargs`: The existing keyword arguments.

**Workflow**:
1. Create a copy of the original prompts dictionary to iterate over.
2. Loop through each prompt type and its associated data.
3. Check the required variables for each prompt type.
4. If any required variable is `None`, remove that prompt type from the original prompts dictionary.

```python
def remove_prompt_if_none(prompts, kwargs):
    prompts_copy = prompts.copy()
    for prompt_type, prompt_data in prompts_copy.items():
        required_vars = prompt_data.get('vars', [])
        # If there are no required vars or all vars are empty, we keep the prompt
        if not required_vars or all(not var for var in required_vars):
            continue
        for var in required_vars:
            if kwargs.get(var) is None:
                prompts.pop(prompt_type)
                break  # Exit this loop, the dictionary has been changed
```

---

## Show Task

### `_show_task(data)`

**Purpose**: Prints the current task to the console in green text if it exists in the data dictionary.

**Arguments**:
- `data`: The data dictionary containing the task information.

```python
def _show_task(data):
    if 'task' in data:
        cprint(f'\nTask: {data["task"]}', 'green', attrs=['dark'])
```

---

## Set Task Order

### `_set_task_order(data)`

**Purpose**: Sets the order for the next task based on the current task order.

**Arguments**:
- `data`: The data dictionary containing the current task order.

```python
def _set_task_order(data):
    task_order = data.get('this_task_order')
    if task_order is not None:
        data['next_task_order'] = _calculate_next_task_order(task_order)
```

---