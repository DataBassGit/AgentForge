# Agent Methods

Welcome to the Agent Methods documentation! In this section, we'll walk you through the key methods within the `Agent` class that are most relevant for creating subagents. Understanding these methods will help you customize and extend the capabilities of your subagents effectively.

---

## Run Method

### `run(bot_id=None, **kwargs)`

**Purpose**: This method orchestrates the agent's execution process. It loads and processes data, generates prompts, executes prompt using the LLM, and saves and returns the parsed data.

**Arguments**:
- `bot_id`: An optional identifier for the bot. Defaults to `None`.
- `**kwargs`: Additional keyword arguments.

**Workflow**:
1. Load and process relevant data.
2. Generate the prompt required for the LLM.
3. Run the LLM with the generated prompt.
4. Parse the result from the LLM.
5. Save the parsed data.
6. Build the output.

```python
def run(self, bot_id=None, **kwargs):
    self.agent_name = self.__class__.__name__  # Get the name of the agent class

    data = self.load_and_process_data(**kwargs)  # Load and process data based on additional keyword arguments
    prompts = self.generate_prompt(**data)  # Generate the prompt required for the LLM
    result = self.run_llm(prompts)  # Execute prompt using the LLM and receive the result
    parsed_data = self.parse_result(result=result, data=data)  # Parse the received result to obtain usable data
    self.save_parsed_result(parsed_data)  # Save the parsed data for future use or reference
    output = self.build_output(parsed_data)  # Build the output based on the parsed data

    return output
```

---

## Load & Process Data - Method

### `load_and_process_data(**kwargs)`

**Purpose**: This method loads and processes the data required for the agent to operate. It gathers data from multiple sources, including the agent's internal data and additional keyword arguments.

**Arguments**:
- `**kwargs`: Additional keyword arguments that can supplement or override the default data.

**Workflow**:
1. Load internal agent data into `self.agent_data`.
2. Initialize the `data` dictionary with parameters and prompts from `self.agent_data`.
3. Incorporate any supplementary data passed through `kwargs`.
4. Call `self.load_additional_data(data)` to load any other required data from storage.
5. Return the consolidated `data` dictionary.

```python
def load_and_process_data(self, **kwargs):
    # Load agent-specific data
    self.agent_data = _load_agent_data(self._agent_name)
    
    # Initialize data dictionary with parameters and prompts
    data = {'params': self.agent_data.get('params').copy(),
            'prompts': self.agent_data['prompts'].copy()}
    
    # Add any supplementary data from kwargs
    for key in kwargs:
        data[key] = kwargs[key]
    
    # Load any additional data from storage
    self.load_additional_data(data)
    
    return data
```

---

## Load Additional Data - Method

### `load_additional_data(data)`

**Purpose**: This method is intended to be overridden by subagents to load any additional data required for their specific functionalities. By default, it doesn't do much, but you can customize it as needed in the subagent.

**Arguments**:
- `data`: The existing data dictionary that can be extended or modified.

**Default Behavior**:
- Adds an `objective` key-value pair from `self.agent_data`.
- Adds a `task` key-value pair by calling `self.load_current_task()['task']`.
- Calls `_set_task_order(data)` to possibly rearrange tasks.
- Calls `_show_task(data)` to display the current task.

```python
def load_additional_data(self, data):
    # By default, it does nothing; meant to be overridden by each subagent
    data['objective'] = self.agent_data.get('objective')
    data['task'] = self.functions.get_current_task()['document']

    _set_task_order(data)
    _show_task(data)
```

---

## Generate Prompt

### `generate_prompt(**kwargs)`

**Purpose**: This method generates the prompts required for the LLM to function. It uses predefined templates and variables to construct a list of prompts that will be used in the prompt execution. The prompts come from the persona data, which is loaded from the [Persona JSON File](./Persona_File.md).

**Arguments**:
- `**kwargs`: Additional keyword arguments that might contain extra data or overrides for the prompts.

**Workflow**:
1. Load prompts from persona data.
2. Initialize a list of templates starting with the system prompt.
3. Remove any prompts for which there's no corresponding data in `kwargs`.
4. Handle other types of prompts aside from the system prompt.
5. Render the prompts using the templates and variables.
6. Return the list of rendered prompts.

```python
def generate_prompt(self, **kwargs):
    # Load Prompts from Persona Data
    prompts = kwargs['prompts']
    templates = []

    # Handle system prompt
    system_prompt = prompts['System']
    templates.append((system_prompt["template"], system_prompt["vars"]))

    # Remove prompts if there's no corresponding data in kwargs
    remove_prompt_if_none(prompts, kwargs)

    # Handle other types of prompts
    other_prompt_types = [prompt_type for prompt_type in prompts.keys() if prompt_type != 'System']
    for prompt_type in other_prompt_types:
        templates.extend(_handle_prompt_type(prompts, prompt_type))

    # Render Prompts
    prompts = [
        _render_template(template, variables, data=kwargs)
        for template, variables in templates
    ]

    return prompts
```

---

## Run LLM

### `run_llm(prompt)`

**Purpose**: This method runs the LLM to generate text based on the provided prompt. It accesses the LLM instance and relevant parameters from the agent's data.

**Arguments**:
- `prompt`: The prompt (or list of prompts) to be fed into the LLM.

**Workflow**:
1. Retrieve the LLM instance from `self.agent_data['llm']`.
2. Get any additional parameters for the LLM from `self.agent_data.get("params", {})`.
3. Call the `generate_text` method of the LLM instance with the prompt and any additional parameters.
4. Strip any leading or trailing whitespace from the generated text.
5. Return the cleaned-up text.

```python
def run_llm(self, prompt):
    model: LLM = self.agent_data['llm']
    params = self.agent_data.get("params", {})
    return model.generate_text(prompt, **params,).strip()
```

---

## Parse Result

### `parse_result(result, **kwargs)`

**Purpose**: This method is intended for parsing the result obtained from the LLM. By default, it simply returns the result as-is. It's designed to be overridden by [SubAgents](SubAgents.md) to implement specific parsing logic.

**Arguments**:
- `result`: The raw result obtained from the LLM.
- `**kwargs`: Additional keyword arguments that might be used for parsing.

**Default Behavior**:
1. Return the received result without any modifications.

```python
def parse_result(self, result, **kwargs):
    return result
```

---

## Save Parsed Data

### `save_parsed_data(parsed_data)`

**Purpose**: This method saves the parsed data obtained from the LLM. It acts as a wrapper for the `save_results` method, providing a point of customization for subagents.

**Arguments**:
- `parsed_data`: The parsed data to be saved.

**Workflow**:
1. Call the `save_results` method with the parsed data.

```python
def save_parsed_data(self, parsed_data):
    self.save_results(parsed_data)
```

---

## Save Results

### `save_results(result)`

**Purpose**: This method directly interacts with the agent's storage to save the result. It's designed so that subagents can either modify how the data is stored or choose not to store it at all.

**Arguments**:
- `result`: The result to be saved.

**Workflow**:
1. Prepare a `params` dictionary with the result and collection name 'Results'.
2. Call `self.storage.save_memory(params)` to save the data in the agent's storage.

```python
def save_results(self, result):
    params = {
        'data': [result],
        'collection_name': 'Results',
    }

    self.storage.save_memory(params)
```

---

## Build Output

### `build_output(parsed_data)`

**Purpose**: This method is responsible for constructing the final output that the agent will return. By default, it simply returns the parsed data as-is. It's designed to be overridden by [SubAgents](SubAgents.md) for custom output formatting or additional logic.

**Arguments**:
- `parsed_data`: The parsed data that needs to be formatted or otherwise processed for output.

**Default Behavior**:
1. Return the received parsed data without any modifications.

```python
def build_output(self, parsed_data):
    return parsed_data
```

---

## Get Task List

### `get_task_list()`

**Purpose**: Retrieves the list of tasks from the agent's storage. This method accesses the storage component to fetch the tasks collection along with its documents and metadata.

**Arguments**: None

**Returns**: 
- A collection containing tasks, including both the documents and metadata.

**Workflow**:
1. Create a query dictionary with the collection name 'Tasks' and specify the fields to include ('documents', 'metadatas').
2. Call `self.storage.load_collection` with the query dictionary.

```python
def get_task_list(self):
    return self.storage.load_collection({'collection_name': "Tasks",
                                         'include': ["documents", "metadatas"]})
```

---

## Load Current Task

### `load_current_task()`

**Purpose**: Fetches the current task from the task list in the agent's storage. This method utilizes the `get_task_list` method to obtain the tasks and then retrieves the first task.

**Arguments**: None

**Returns**: 
- A dictionary containing the current task.

**Workflow**:
1. Call `self.get_task_list()` to fetch the list of tasks.
2. Retrieve the first task from the `documents` field of the task list.
3. Return a dictionary containing the current task.

```python
def load_current_task(self):
    task_list = self.functions.get_task_list()
    task = task_list['documents'][0]
    return {'task': task}
```

---

## Note: Additional Agent Methods

While the key methods relevant for agent creation have been covered, the `Agent` class contains additional methods for those who want to dive deeper into its functionalities. For a complete list and documentation of these extra methods, refer to the [Additional Agent Methods Page](AdditionalAgentMethods.md).

---