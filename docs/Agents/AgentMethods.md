# Agent Methods

Welcome to the Agent Methods documentation! In this section, we'll walk you through the key methods within the `Agent` class which are the most relevant for creating SubAgents. Understanding these methods will help you customize and extend the capabilities of your SubAgents effectively.

---

## 📌 Important Note: Dual Purpose of Methods

All the methods outlined in this documentation are designed with two primary objectives:

1. **SubAgent Customization**: These methods serve as access points for customizing SubAgents. You can override them to implement specific functionalities without changing the entire code base.

2. **Default Behavior**: The methods also act as the default behavior for agents. Creating a new SubAgent can be as simple as defining a new SubAgent class and its prompts, without necessarily modifying the default behavior inherited from the agent super class.

For more details on how to create and customize SubAgents, see [SubAgents Documentation](SubAgentCreation.md).

---

## Methods
1. [Run](#run)
2. [Status](#status)
3. [Load Data](#load-data)
4. [Load Agent Data](#load-agent-data)
5. [Load Main Data](#load-main-data)
6. [Load Additional Data](#load-additional-data)
7. [Process Data](#process-data)
8. [Generate Prompt](#generate-prompt)
9. [Run LLM](#run-llm)
10. [Parse Result](#parse-result)
11. [Save Result](#save-result)
12. [Build Output](#build-output)
13. [Additional Functions](#note-additional-functions)

---

## Run

### `run(bot_id=None, **kwargs)`

**Purpose**: This method is the main orchestrator for the agent's workflow. It sequentially calls other methods to load and process data, generate prompts, run the LLM, parse results, save them, and finally build the output.

**Arguments**:
- `bot_id`: An optional identifier for the bot. Defaults to `None`. (Note: There is no implementation for this variable yet)
- `**kwargs`: Additional keyword arguments that may be passed to `load_data`.

**Workflow**:
1. Display the running status.
2. Load data using `self.load_data()`.
3. Process the loaded data using `self.process_data()`.
4. Generate the prompt using `self.generate_prompt()`.
5. Execute the LLM using `self.run_llm()`.
6. Parse the result using `self.parse_result()`.
7. Save the parsed result using `self.save_result()`.
8. Build the final output using `self.build_output()`.

```python
def run(self, bot_id=None, **kwargs):
    """This is the heart of all Agents, orchestrating the entire workflow from data loading to output generation."""
    self.status("Running ...")
    self.load_data(**kwargs)
    self.process_data()
    self.generate_prompt()
    self.run_llm()
    self.parse_result()
    self.save_result()
    self.build_output()
    
    return self.output
```
---

## Status

### `status(self, msg)`

**Purpose**: This method is used for displaying status messages during the agent's workflow. It leverages the `print_message` function from `Functions` to print formatted status messages to the console.

**Arguments**:
- `msg` (`str`): The message that needs to be displayed as the status.

**Workflow**:
1. Formats the message by appending the `agent_name` and the provided `msg`.
2. Calls `self.functions.print_message()` to display the formatted message.

```python
def status(self, msg):
	"""Prints a formatted status message to the console"""
	self.functions.print_message(f"\n{self.agent_name} - {msg}")
```

---

## Load Data

### `load_data(self, **kwargs)`

**Purpose**: This method coordinates the data loading process. It sequentially calls `load_agent_data`, `load_main_data`, and `load_additional_data` to populate the agent's internal `data` attribute.

**Arguments**:
- `**kwargs`: Additional keyword arguments that may be used by `load_agent_data` for fetching the agent-specific data.

**Workflow**:
1. Calls `self.load_agent_data(**kwargs)` to populate agent-specific data. The data is stored internally.
2. Invokes `self.load_main_data()` to add core data required for the agent's operation. The data is added to the internal `data` attribute.
3. Executes `self.load_additional_data()` to include any extra data. Again, this is added to the internal `data` attribute.

```python
def load_data(self, **kwargs):
    """This method is in charge of calling all the relevant load data methods"""
    self.load_agent_data(**kwargs)
    self.load_main_data()
    self.load_additional_data()
```

---

## Load Agent Data

### `load_agent_data(self, **kwargs)`

**Purpose**: This method takes charge of loading the agent-specific data. It stores the data directly in the agent's internal `data` attribute.

**Arguments**:
- `**kwargs`: Additional keyword arguments that can be used to supplement the agent's data.

**Workflow**:
1. Initialized the agent-specific data `self.agent_data` by calling `self.functions.load_agent_data(self.agent_name)`.
2. Initializes the agent's internal `data` attribute with two keys:
  - `params`: A copy of the parameters from `self.agent_data`.
  - `prompts`: A copy of the prompts from `self.agent_data`.
3. Iterates through `kwargs` to add any additional data to the `data` attribute.

```python
def load_agent_data(self, **kwargs):
    """Loads the Agent data and any additional data given to it"""
    self.agent_data = self.functions.load_agent_data(self.agent_name)
    self.data = {'params': self.agent_data.get('params').copy(), 'prompts': self.agent_data['prompts'].copy()}
    for key in kwargs:
        self.data[key] = kwargs[key]
```

---

## Load Main Data

### `load_main_data(self)`

**Purpose**: This method is responsible for loading the primary, essential data that the agent requires for its operations. It  directly modifies the agent's internal `data` attribute.

**Arguments**: None

**Workflow**:
1. Adds an `objective` to the internal `data` attribute, fetched from `self.agent_data.get('objective')`.
2. Adds a `task` to the internal `data` attribute, obtained from `self.functions.get_current_task()['document']`.

```python
def load_main_data(self):
    """Loads the main data for the Agent, by default it's the Objective and Current Task"""
    self.data['objective'] = self.agent_data.get('objective')
    self.data['task'] = self.functions.get_current_task()['document']
```

---

## Load Additional Data

### `load_additional_data(data)`

**Purpose**: By default, this method is a placeholder waiting for SubAgents to override it. It provides an access point to modify the data going into the agent.

**Arguments**: None

**Workflow**:
1. Does nothing. Yep, you read that right.

```python
def load_additional_data(self):
    """This method does nothing by default, it is meant to be overridden by SubAgents if needed"""
    pass

```

**Note**: This method is designed to be overridden by [SubAgents](SubAgentCreation.md) for loading any additional data depending on their specific requirements.

---

## Process Data

### `process_data(data)`

**Purpose**: This method serves as a placeholder for processing agent data before being rendered. By default, it does nothing.

**Arguments**: None


```python
def process_data(self):
    """This method does nothing by default, it is meant to be overriden by SubAgents if needed"""
    pass
```

**Note**: This method is designed to be overridden by [SubAgents](SubAgentCreation.md) for custom data processing depending on their specific requirements.

---

## Generate Prompt

### `generate_prompt(self, **kwargs)`

**Purpose**: This method is in charge of generating the prompts needed for the LLM to operate. It constructs a list of prompts based on predefined templates and variables. These prompts are stored directly in the agent's internal `prompt` attribute.

**Arguments**:
- `**kwargs`: Additional keyword arguments that can be used to provide extra data or override existing prompt data.

**Workflow**:
1. Initialize an empty list named `templates` for storing prompt templates.
2. Handle the system prompt by fetching it from the internal `data['prompts']['System']` and add it to `templates`.
3. Remove any prompts for which there's no corresponding data in the internal `data` attribute by calling `self.functions.remove_prompt_if_none`.
4. Handle other types of prompts that are not the system prompt. Extend `templates` with these other types.
5. Render the prompts using the templates and variables. Store the rendered prompts directly in the agent's internal `prompt` attribute.

```python
def generate_prompt(self, **kwargs):
    """Takes the data previously loaded and processes it to render the prompt being fed to the LLM"""
    templates = []
    system_prompt = self.data['prompts']['System']
    templates.append((system_prompt["template"], system_prompt["vars"]))

    self.functions.remove_prompt_if_none(self.data['prompts'], self.data)

    other_prompt_types = [prompt_type for prompt_type in self.data['prompts'].keys() if prompt_type != 'System']
    for prompt_type in other_prompt_types:
        templates.extend(self.functions.handle_prompt_type(self.data['prompts'], prompt_type))

    self.prompt = [
        self.functions.render_template(template, variables, data=self.data)
        for template, variables in templates
    ]
```

**Note**: The prompt templates come from the persona data, which is loaded from the [Persona JSON File](../Persona/Persona.md).

---

## Run LLM

### `run_llm(self)`

**Purpose**: This method executes the LLM (Large Language Model) to generate text based on the previously generated prompt which is stored in the agent's internal `prompt` attribute. The generated text is then stored directly in the agent's internal `result` attribute.

**Arguments**: None

**Workflow**:
1. Retrieve the LLM instance from the internal `self.agent_data['llm']`.
2. Fetch any additional parameters for the LLM from `self.agent_data.get("params", {})`.
3. Execute the `generate_text` method of the LLM instance using the internal `prompt` and any additional parameters.
4. Strip any leading or trailing whitespace from the generated text and store it in the internal `result` attribute.

```python
def run_llm(self):
    """Sends the rendered prompt to the LLM and stores the response in the internal result attribute"""
    model: LLM = self.agent_data['llm']
    params = self.agent_data.get("params", {})
    self.result = model.generate_text(self.prompt, **params,).strip()
```

---

## Parse Result

### `parse_result(self)`

**Purpose**: This method is designed as a placeholder for parsing the results returned by the LLM. By default, it does nothing.

**Arguments**: None

**Workflow**:
1. The method exists but performs no action, effectively serving as a placeholder.

```python
def parse_result(self):
    """This method does nothing by default, it is meant to be overridden by SubAgents if needed"""
    pass
```

**Note**: This method is intended to be overridden by [SubAgents](SubAgentCreation.md) who may require custom parsing of the result.

---

## Save Result

### `save_result(self)`

**Purpose**: This method takes the generated result from the LLM and saves it to memory. Think of it as the agent's memory, holding on to important results for future use.

**Arguments**: None

**Workflow**:
1. Constructs a parameter dictionary with the LLM-generated `self.result` and a collection name 'Results'.
2. Calls `self.storage.save_memory(params)` to save the result to memory.

```python
def save_result(self):
    """This method saves the LLM Result to memory"""
    params = {'data': [self.result], 'collection_name': 'Results'}
    self.storage.save_memory(params)
```

---

## Build Output

### `build_output(self)`

**Purpose**: This method sets the final output based on the result generated by the LLM. By default, it simply sets the `self.output` to be the `self.result` generated by the LLM. Think of it as the agent's final say before it exits the stage.

**Arguments**: None

**Workflow**:
1. Sets `self.output` to the value of `self.result`.

```python
def build_output(self):
    """Sets the internal 'output' attribute as the internal 'result' attribute by default"""
    self.output = self.result
```

**Note**: Like other methods in this class, `build_output` is ripe for an override by [SubAgents](SubAgentCreation.md) who might want to customize the final output.

---

## Note: Additional Functions

While the key methods relevant for agent creation have been covered in this section, the `Agent` class imports additional methods from a `Functions` utilities class. For those who want to dive deeper into its functionalities, a complete list and documentation of these extra methods can be found in the [Function Utils](../Utils/FunctionUtils.md) Page.

---