# Agent Methods

Welcome to the Agent Methods documentation! In this section, we'll walk you through the key methods within the `Agent` class that are most relevant for creating SubAgents. Understanding these methods will help you customize and extend the capabilities of your SubAgents effectively.

## Methods
1. [Run](#run)
2. [Load Data](#load-data)
3. [Load Agent Data](#load-agent-data)
4. [Load Main Data](#load-main-data)
5. [Load Additional Data](#load-additional-data)
6. [Process Data](#process-data)
7. [Generate Prompt](#generate-prompt)
8. [Run LLM](#run-llm)
9. [Parse Result](#parse-result)
10. [Save Parsed Result](#save-parsed-result)
11. [Build Output](#build-output)
12. [Additional Functions](#note-additional-functions)

---

## Run

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
    """This function is the heart of all Agents, it defines how Agents receive and process data"""
    agent_name = self.__class__.__name__

    cprint(f"\n{agent_name} - Running Agent...", 'red', attrs=['bold'])

    data = self.load_data(**kwargs)
    self.process_data(data)
    prompt = self.generate_prompt(**data)
    result = self.run_llm(prompt)
    parsed_result = self.parse_result(result=result, data=data)
    self.save_parsed_result(parsed_result)
    output = self.build_output(parsed_result)

    cprint(f"\n{agent_name} - Agent Done...\n", 'red', attrs=['bold'])

    return output
```

---

## Load Data

### `load_data(**kwargs)`

**Purpose**: This method orchestrates the data loading process. It's the maestro directing the orchestra of `load_agent_data`, `load_main_data`, and `load_additional_data`.

**Arguments**:
- `**kwargs`: Additional keyword arguments that may be needed for loading the agent's data.

**Workflow**:
1. Calls `self.load_agent_data(**kwargs)` to load agent-specific data into a new dictionary `data`.
2. Invokes `self.load_main_data(data)` to populate the `data` dictionary with core data required for the agent's operation.
3. Executes `self.load_additional_data(data)` to supplement the `data` dictionary with any extra information.
4. Returns the consolidated `data` dictionary, ready for action.

```python
def load_data(self, **kwargs):
    """This function is in charge of calling all the relevant load data methods"""
    data = self.load_agent_data(**kwargs)
    self.load_main_data(data)
    self.load_additional_data(data)

    return data
```
---
## Load Agent Data

### `load_agent_data(**kwargs)`

**Purpose**: This method is responsible for loading the core data specific to the agent.

**Arguments**:
- `**kwargs`: Additional keyword arguments that can be used to add more data to the agent's repertoire.

**Workflow**:
1. Refreshes `self.agent_data` by calling `self.functions.load_agent_data(self._agent_name)`.
2. Initializes a `data` dictionary with two keys: 
  - `params`: A copy of the parameters from `self.agent_data`.
  - `prompts`: A copy of the prompts from `self.agent_data`.
3. Iterates through `kwargs` to add any additional data to the `data` dictionary.
4. Returns the filled-up `data` dictionary.

```python
def load_agent_data(self, **kwargs):
    """This function loads the Agent data and any additional data given to it"""
    self.agent_data = self.functions.load_agent_data(self._agent_name)
    data = {'params': self.agent_data.get('params').copy(), 'prompts': self.agent_data['prompts'].copy()}
    for key in kwargs:
        data[key] = kwargs[key]
    return data
```

---

## Load Main Data

### `load_main_data(data)`

**Purpose**: This method loads the core, non-negotiable data that the agent needs for its tasks.

**Arguments**:
- `data` (`dict`): The existing data dictionary that's about to get the main data added to it.

**Workflow**:
1. Adds an `objective` to `data`, fetched from `self.agent_data.get('objective')`.
2. Adds a `task` to `data`, obtained from `self.functions.get_current_task()['document']`.

```python
def load_main_data(self, data):
    """This function loads the main data for the Agent, by default it's the Objective and Current Task"""
    data['objective'] = self.agent_data.get('objective')
    data['task'] = self.functions.get_current_task()['document'] 
```

---

## Load Additional Data

### `load_additional_data(data)`

**Purpose**: By default, this method is a placeholder waiting for SubAgents to override it. It provides an access point to modify the data going into the agent.

**Arguments**:
- `data` (`dict`): The existing data dictionary that could potentially be enriched or altered by SubAgents.

**Workflow**:
1. Does nothing. Yep, you read that right.

```python
def load_additional_data(self, data):
    """This function does nothing by default, it is meant to be overriden by SubAgents if needed"""
    pass

```

**Note**: This method is designed to be overridden by [SubAgents](SubAgentCreation.md) for loading any additional data depending on their specific requirements.

---

## Process Data

### `process_data(data)`

**Purpose**: This method allows for processing the agent's data, it provides an access point for customization.

**Arguments**:
- `data` (`dict`): The existing data dictionary that's about to get some last-minute adjustments.

**Workflow**:
1. Calls `self.functions.set_task_order(data)` to possibly rearrange the tasks in the data.
2. Invokes `self.functions.show_task(data)` to display the current task's details.

```python
def process_data(self, data):
    """This function is for processing the data before rendering the prompt"""
    self.functions.set_task_order(data)
    self.functions.show_task(data)
```

---

## Generate Prompt

### `generate_prompt(**kwargs)`

**Purpose**: This method generates the prompts required for the LLM to function. It uses predefined templates and variables to construct a list of prompts that will be used in the prompt execution. The prompts come from the persona data, which is loaded from the [Persona JSON File](../Persona/Persona.md).

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
    """This function takes the data previously loaded and processes it to render the prompt"""
    # Load Prompts from Persona Data
    prompts = kwargs['prompts']
    templates = []

    # Handle system prompt
    system_prompt = prompts['System']
    templates.append((system_prompt["template"], system_prompt["vars"]))

    # Remove prompts if there's no corresponding data in kwargs
    self.functions.remove_prompt_if_none(prompts, kwargs)

    # Handle other types of prompts
    other_prompt_types = [prompt_type for prompt_type in prompts.keys() if prompt_type != 'System']
    for prompt_type in other_prompt_types:
        templates.extend(self.functions.handle_prompt_type(prompts, prompt_type))

    # Render Prompts
    prompts = [
        self.functions.render_template(template, variables, data=kwargs)
        for template, variables in templates
    ]

    self.logger.log(f"Prompt:\n{prompts}", 'debug')

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
    """This function sends the rendered prompt to the LLM and returns the model response"""
    model: LLM = self.agent_data['llm']
    params = self.agent_data.get("params", {})
    return model.generate_text(prompt, **params,).strip()
```

---

## Parse Result

### `parse_result(result, **kwargs)`

**Purpose**: This method is designed to be a placeholder for processing the result returned by the Low-Level Module (LLM). By default, it simply returns the result as-is.

**Arguments**:
- `result`: The result obtained from the LLM.
- `**kwargs`: Additional keyword arguments that could potentially be used by SubAgents for custom parsing.

**Workflow**:
1. Returns the unaltered `result`.

```python
def parse_result(self, result, **kwargs):
    """This function simply returns the result by default, it is meant to be overriden by SubAgents if needed"""
    return result
```

**Note**: This method is primarily intended to be overridden by [SubAgents](SubAgentCreation.md) who may require custom parsing of the result.

---

## Save Parsed Result

### `save_parsed_result(parsed_result)`

**Purpose**: This method takes the processed result from the Low-Level Module (LLM) and saves it to memory. It acts as the agent's short-term memory, preserving important results for future reference.

**Arguments**:
- `parsed_result`: The processed result that needs to be saved to memory.

**Workflow**:
1. Constructs a parameter dictionary with `parsed_result` and a collection name 'Results'.
2. Calls `self.storage.save_memory(params)` to save the parsed result to memory.

```python
def save_parsed_result(self, parsed_result):
    """This function saves the LLM Result to memory"""
    params = {'data': [parsed_result], 'collection_name': 'Results'}
    self.storage.save_memory(params)
```

---

## Build Output

### `build_output(parsed_result)`

**Purpose**: This method serves as a placeholder for generating the final output based on the parsed result from the Low-Level Module (LLM). By default, it returns the parsed result without any modification.

**Arguments**:
- `parsed_result`: The processed result that will form the basis for the final output.

**Workflow**:
1. Returns the unmodified `parsed_result`.

```python
def build_output(self, parsed_result):
    """This function returns the parsed_result by default, it is meant to be overriden by SubAgents if needed"""
    return parsed_result
```

**Note**: This method is designed to be overridden by [SubAgents](SubAgentCreation.md) for custom output generation, depending on their specific requirements.

---

## Note: Additional Functions

While the key methods relevant for agent creation have been covered in this section, the `Agent` class imports additional methods from a functions utilities class. For those who want to dive deeper into its functionalities, a complete list and documentation of these extra methods can be found in the [Function Utils](../Utils/FunctionUtils.md) Page.

---