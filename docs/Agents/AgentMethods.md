# Agent Methods

Welcome to the Agent Methods documentation! In this section, we'll walk you through the key methods within the `Agent` base class which are the most relevant for creating [Custom Agents](CustomAgents.md). Understanding these methods will help you customize and extend the capabilities of your agents effectively.

---

## 📌 Important Note: The Essence of Agents

All the methods outlined in this documentation serve a dual purpose:

1. **Customization & Specialization**: These methods act as access points for specialization. You can override them to implement specific functionalities without changing the entire code base. This allows each subclass to be a specialized version of the base `Agent` class, extending or modifying its behaviors.

2. **Default Behavior & Streamlining**: The methods also serve as the default behavior for any agent, making the creation of new agents incredibly streamlined. Just create a new subclass of the `Agent` class, add its prompts, and you're good to go!

In other words, The `Agent` base class serves as a generic agent, while each subclass is a specialized agent.

For more details on how to create and specialize agents, see [Custom Agents](CustomAgents.md).

---

## Methods
1. [Run](#run)
2. [Status](#status)
3. [Load Data](#load-data)
4. [Load Agent Data](#load-agent-data)
5. [Load Agent Type Data](#load-agent-type-data)
6. [Load Main Data](#load-main-data)
7. [Load Additional Data](#load-additional-data)
8. [Process Data](#process-data)
9. [Generate Prompt](#generate-prompt)
10. [Run LLM](#run-llm)
11. [Parse Result](#parse-result)
12. [Save Result](#save-result)
13. [Build Output](#build-output)
14. [Additional Functions](#note-additional-functions)

---

## Run

### `run(**kwargs)`

**Purpose**: This method is the main orchestrator for the agent's workflow. It sequentially calls other methods to load and process data, generate prompts, run the LLM, parse results, save them, and finally build the output.

**Arguments**:
- `**kwargs`: Additional keyword arguments that may be passed to `load_data`.

**Workflow**:
1. Display the running status.
2. Load data using `self.load_data(**kwargs)`.
3. Process the loaded data using `self.process_data()`.
4. Generate the prompt using `self.generate_prompt()`.
5. Execute the LLM using `self.run_llm()`.
6. Parse the result using `self.parse_result()`.
7. Save the parsed result using `self.save_result()`.
8. Build the final output using `self.build_output()`.
9. Return the built output

```python
def run(self, **kwargs):
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
2. Calls `self.functions.printing.print_message()` to display the formatted message.

```python
def status(self, msg):
    """Prints a formatted status message to the console"""
    self.functions.printing.print_message(f"\n{self.agent_name} - {msg}")
```

---

## Load Data

### `load_data(self, **kwargs)`

**Purpose**: This method orchestrates the data loading process for the agent. It sequentially calls `load_agent_data`, `load_agent_type_data`, `load_main_data`, and `load_additional_data` to comprehensively populate the agent's internal `data` attribute. This structured approach ensures that all necessary data, from the general to the specific, is available for the agent's operations.

**Arguments**:
- `**kwargs`: These are additional keyword arguments provided to the agent. Any data passed through `**kwargs` is directly added to the agent's internal data structure, allowing for the customization of the agent's behavior or state at runtime.

**Workflow**:
1. Calls `self.load_agent_data(**kwargs)` to load data that is inherently tied to the agent. This method not only fetches the agent's inherent data but also takes any additional data provided via `**kwargs` and integrates it into the agent's internal data structure. This approach enables the agent to be dynamically configured with specific data at the time of its invocation.
2. Invokes `self.load_agent_type_data()` to load data specific to the agent's type or subclass. This step is crucial for agents belonging to a specific category or type, like `PersonaAgent`, to load their common data.
3. Executes `self.load_main_data()` to add core data essential for the agent's operation. This data is added to the internal `data` attribute.
4. Calls `self.load_additional_data()` to include any extra, agent-specific data. This step is tailored for the individual 'child' agents to load data unique to their specific functionality.

```python
def load_data(self, **kwargs):
    """Orchestrates the various data loading methods for comprehensive data preparation"""
    self.load_agent_data(**kwargs)
    self.load_agent_type_data()
    self.load_main_data()
    self.load_additional_data()
```

---

## Load Agent Data

### `load_agent_data(self, **kwargs)`

**Purpose**: This method takes charge of loading the agent-specific data. It stores the data directly in the agent's internal `data` attribute.

**Arguments**:
- `**kwargs`: These are additional keyword arguments provided to the method.

**Workflow**:
1. Initialized the agent-specific data `self.agent_data` by calling `self.functions.agent_utils.load_agent_data(self.agent_name)`.
2. Initializes the agent's internal `data` attribute with two keys:
   1. `params`: A copy of the parameters from `self.agent_data`.
   2. `prompts`: A copy of the prompts from `self.agent_data`.
3. Iterates through `kwargs` to add any additional data to the `data` attribute.

```python
def load_agent_data(self, **kwargs):
    """Loads the Agent data and any additional data given to it"""
    self.agent_data = self.functions.agent_utils.load_agent_data(self.agent_name)
    self.data = {'params': self.agent_data.get('params').copy(), 'prompts': self.agent_data['prompts'].copy()}
    for key in kwargs:
        self.data[key] = kwargs[key]
```

---

## Load Agent Type Data

### `load_agent_type_data(self)`

**Purpose**: This method is intended for use in subclasses of the main `Agent` class, providing a structured way to load data specific to a particular subclass (or "type") of agent. It's a powerful tool for creating hierarchies of agents where each subclass inherits the general capabilities of the `Agent` class but also has unique data requirements.

**Example Use Case**: Consider a `PersonaAgent` subclass. This method in `PersonaAgent` could be overridden to load persona-specific data, essential for all agents derived from this class (e.g., `FriendlyAgent`, `ProfessionalAgent`, etc.). Each of these child agents would automatically load data require by persona agents, thanks to this method defined in their parent `PersonaAgent` class.
**Example Use Case**: Consider a `PersonaAgent` subclass. This method in `PersonaAgent` could be overridden to load persona-specific data, essential for all agents derived from this class (e.g., `FriendlyAgent`, `ProfessionalAgent`, etc.). Each of these child agents would automatically load data require by persona agents, thanks to this method defined in their parent `PersonaAgent` class.

**Arguments**: None

**Workflow**:
1. By default, this method does nothing. It serves as a placeholder for subclasses to implement their specific data loading logic.

```python
def load_agent_type_data(self):
    """Designed to be overridden in subclasses to load data specific to the agent's type or category"""
    pass
```

>**Note**: Utilize this method in any subclass of `Agent` to load data that is relevant to all agents of that particular subclass. This approach promotes code reusability and maintains a clean architecture, where each subclass can extend the functionality of the base class without redundancy.

---

## Load Main Data

### `load_main_data(self)`

**Purpose**: This method is responsible for loading the primary, essential data that the agent requires for its operations. It  directly modifies the agent's internal `data` attribute.

**Arguments**: None

**Workflow**:
1. Adds an `objective` to the internal `data` attribute, fetched from `self.agent_data['settings']['directives'].get('Objective', None)`.


```python
def load_main_data(self):
    """Loads the main data for the Agent, by default it's the Objective"""
    self.data['objective'] = self.agent_data['settings']['directives'].get('Objective', None)
```

---

## Load Additional Data

### `load_additional_data(self)`

**Purpose**: This method is specifically designed for the final, specialized agent classes — the "children" in the agent hierarchy. It allows these agents to load data that is unique to their specific functionality or role. This method is where you can tailor data loading for each individual agent, ensuring they have all the unique information they need to perform their tasks effectively.

**Example Use Case**: If you have a `WeatherReportingAgent` that requires specific weather data, or a `StockAnalysisAgent` needing financial data, this method in each of these agents can be overridden to load that specialized data.

**Arguments**: None

**Workflow**:
1. This method does nothing by default, providing a template for final agent classes to implement their own data loading logic.

```python
def load_additional_data(self):
    """Intended to be overridden in the final, specialized agent classes to load data unique to each agent's specific role or functionality"""
    pass
```

>**Note**: This method is a critical part of designing specialized, task-specific agents. By overriding `load_additional_data`, you can ensure that each agent is equipped with all the unique information it needs, differentiating it from other agents in the hierarchy and enabling it to execute its specific tasks.

---

## Process Data

### `process_data(data)`

**Purpose**: This method serves as a placeholder for processing agent data before being rendered. By default, it does nothing.

**Arguments**: None


```python
def process_data(self):
    """Does nothing by default, it is meant to be overriden by Custom Agents if needed"""
    pass
```

>**Note**: This method is designed to be overriden by [Custom Agents](CustomAgents.md) for custom data processing depending on their specific requirements.

---

## Generate Prompt

### `generate_prompt(self)`

**Purpose**: This method is responsible for generating the prompts required for the LLM to operate. It constructs the prompts based on predefined templates and the available data. The generated prompts are stored directly in the agent's internal `prompt` attribute.

**Workflow**:
1. Initialize an empty list named `rendered_prompts` for storing the generated prompts.
2. Iterate over each `prompt_template` in the agent's internal `data['prompts']` attribute.
3. Handle each prompt template by fetching it and validating it using the `handle_prompt_template` function.
4. If the returned template is valid, render the template using the agent's data.
5. Add the rendered prompt to the `rendered_prompts` list.
6. Store the `rendered_prompts` directly in the agent's internal `prompt` attribute.

```python
def generate_prompt(self):
    """Takes the data previously loaded and processes it to render the prompt being fed to the LLM."""
    rendered_prompts = []

    for prompt_template in self.data['prompts'].values():
        template = self.functions.prompt_handling.handle_prompt_template(prompt_template, self.data)
        if template:  # If the template is valid (i.e., not None)
            rendered_prompt = self.functions.prompt_handling.render_prompt_template(template, self.data)
            rendered_prompts.append(rendered_prompt)

    self.prompt = rendered_prompts
```

> **Note**: The prompt templates for each agent come from a corresponding `YAML` file found in the `.agentforge/agents/` folder. The `YAML` file name must match the custom agent class name.
> 
> **Example**: If you have a custom agent class named `NewAgent`, the corresponding `YAML` file should be named `NewAgent.yaml`.

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
    self.result = model.generate_text(self.prompt, **params).strip()
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
    """Does nothing by default, it is meant to be overriden by Custom Agents if needed"""
    pass
```

>**Note**: This method is intended to be overriden by [Custom Agents](CustomAgents.md) who may require custom parsing of the result.

---

## Save Result

### `save_result(self)`

**Purpose**: This method takes the generated result from the LLM and saves it to memory. Think of it as the agent's memory, holding on to important results for future use.

**Arguments**: None

**Workflow**:
1. Constructs a parameter dictionary with the LLM-generated `self.result` and a collection name `Results`.
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

>**Note**: Like other methods in this class, `build_output` is ripe for an override by [Custom Agents](CustomAgents.md) who might want to customize the final output.

---

## Note: Additional Functions

While the key methods relevant for [Custom Agent](CustomAgents.md) creation have been covered in this section, the `Agent` class imports additional methods from a `Functions` utilities class. For those who want to dive deeper into its functionalities, a complete list and documentation of these extra methods can be found in the [Functions](../Utils/FunctionUtils.md) Page.

---