# Agent Methods Guide

Welcome to the **Agent Methods** guide! This section provides an in-depth look at the key methods within the `Agent` base class. Understanding these methods is crucial for creating custom agents by subclassing the `Agent` class, allowing you to extend and customize agent behaviors effectively.

---

## Introduction

The `Agent` base class provides a robust template for building agents in **AgentForge**. By subclassing `Agent`, you can create new agents quickly and customize their behaviors by overriding specific methods.

**Why Override Methods?**

- **Customization**: Tailor agent behaviors to fit specific tasks.
- **Specialization**: Implement unique processing logic or data handling.
- **Extensibility**: Add new functionalities without altering the base class.

---

## Method Categories

For better understanding, we've grouped the methods into the following categories:

1. [Core Workflow Methods](#1-core-workflow-methods)
2. [Data Loading Methods](#2-data-loading-methods)
3. [Data Processing Methods](#3-data-processing-methods)
4. [LLM Interaction Methods](#4-llm-interaction-methods)
5. [Result Handling Methods](#5-result-handling-methods)
6. [Customization Hooks](#6-customization-hooks)

---

## 1. Core Workflow Methods

### `run(self, **kwargs)`

**Purpose**: The central method that orchestrates the agent's workflow, executing a sequence of steps to generate the final output.

**Workflow Steps**:

1. **Load Data**: `self.load_data(**kwargs)`
2. **Process Data**: `self.process_data()`
3. **Generate Prompt**: `self.generate_prompt()`
4. **Run LLM**: `self.run_llm()`
5. **Parse Result**: `self.parse_result()`
6. **Save to Storage**: `self.save_to_storage()`
7. **Build Output**: `self.build_output()`

**Usage**:

- Call `run()` with any necessary keyword arguments.
- The method handles error logging and returns the final output or `None` if an error occurs.

**Example**:

```python
class CustomAgent(Agent):
    pass

agent = CustomAgent()
output = agent.run(user_input="Hello, AgentForge!")
print(output)
```

---

## 2. Data Loading Methods

These methods handle loading various types of data into the agent.

### `load_data(self, **kwargs)`

**Purpose**: Centralizes the data loading process.

**What It Does**:

- Loads keyword arguments.
- Loads agent configuration data.
- Loads persona data.
- Loads data from storage.
- Loads any additional data.

**When to Override**:

- Typically, you don't need to override this method. Instead, override the specific data loading methods as needed.

### `load_kwargs(self, **kwargs)`

**Purpose**: Loads variables passed as keyword arguments into `self.data`.

**Usage**:

- Automatically called by `load_data()`.

**Example**:

```python
def load_kwargs(self, **kwargs):
    self.data.update(kwargs)
```

---

### `load_agent_data(self)`

**Purpose**: Loads the agent's configuration data, including parameters and prompts.

**Usage**:

- Automatically called by `load_data()`.

---

### `load_persona_data(self)`

**Purpose**: Loads persona-specific data, enriching the agent's context.

**Usage**:

- Automatically called by `load_data()`.
- Integrates data from the persona **YAML** file into `self.data`.

---

### `load_from_storage(self)`

**Purpose**: Placeholder for loading data from storage systems.

**Usage**:

- **Override this method** if your agent needs to load data from a database or file system.

**Example Override**:

```python
def load_from_storage(self):
    self.data['stored_value'] = self.agent_data['storage'].load('key')
```

---

### `load_additional_data(self)`

**Purpose**: Placeholder for loading any additional data.

**Usage**:

- **Override this method** to load custom data required by your agent.

**Example Override**:

```python
def load_additional_data(self):
    self.data['timestamp'] = datetime.now().isoformat()
```

---

## 3. Data Processing Methods

### `process_data(self)`

**Purpose**: Placeholder for processing the loaded data before it's used in prompt generation.

**Default Behavior**: None

**Usage**:

- **Override this method** to implement custom data processing logic.

**Example Override**:

```python
def process_data(self):
    self.data['user_input'] = self.data['user_input'].upper()
```

---

## 4. LLM Interaction Methods

### `generate_prompt(self)`

**Purpose**: Renders the prompt templates using `self.data`.

**Workflow**:

- Iterates over prompt templates.
- Renders each template with current data.
- Stores the rendered prompts in `self.prompt`.

**When to Override**:

- Typically, you don't need to override this method. Only override this method if you need custom prompt rendering logic.

---

### `run_llm(self)`

**Purpose**: Executes the language model using the generated prompts.

**Workflow**:

- Uses the LLM instance from `self.agent_data['llm']`.
- Passes in `self.prompt` and parameters.
- Stores the result in `self.result`.

**When to Override**:

- If you need to modify how the LLM is called.

**Example Override**:

```python
def run_llm(self):
    # Custom LLM execution
    self.result = "Simulated LLM output"
```

---

## 5. Result Handling Methods

### `parse_result(self)`

**Purpose**: Placeholder for parsing raw result from the LLM.

**Usage**:

- **Override this method** to implement custom parsing logic.

**Example Override**:

```python
def parse_result(self):
    self.data['parsed_result'] = json.loads(self.result)
```

---

### `save_to_storage(self)`

**Purpose**: Placeholder for saving data to storage.

**Usage**:

- **Override this method** if your agent needs to save data persistently.

**Example Override**:

```python
def save_to_storage(self):
    data = # logic for data to be saved
    metadata = # metadata for the data being saved
    self.agent_data['storage'].save_memory(collection_name='Results', data=data, metadata=metadata)
```

---

### `build_output(self)`

**Purpose**: Constructs the final output from the processed data.

**Default Behavior**:

- Sets `self.output = self.result`

**When to Override**:

- To customize the final output format.

**Example Override**:

```python
def build_output(self):
    self.output = f"Processed Output: {self.data['parsed_result']}"
```

---

## 6. Customization Hooks

These methods are designed to be overridden to customize agent behavior.

- **`load_from_storage()`**
- **`load_additional_data()`**
- **`process_data()`**
- **`parse_result()`**
- **`save_to_storage()`**
- **`build_output()`**

---

## Tips and Best Practices

- **Start Simple**: Begin by subclassing `Agent` without overriding any methods. Ensure your basic agent works before adding complexity.
- **Override as Needed**: Only override methods that require custom logic for your agent's purpose.
- **Test Each Step**: After overriding a method, test your agent to ensure it behaves as expected.
- **Use Descriptive Names**: Name your agents and variables clearly to enhance readability.
- **Leverage Inheritance**: Remember that your custom agent inherits all methods from `Agent`. You can call `super()` to utilize base class functionality.

---

## Additional Functions and Utilities

The `Agent` class utilizes additional methods from the `Functions` utilities class. These utilities assist with tasks such as:

- **Prompt Handling**
- **Logging**
- **Data Storage**

For more details, refer to the [Utilities Overview](../Utils/UtilsOverview.md).

---

## Conclusion

By understanding and utilizing these methods, you can create powerful custom agents tailored to your specific needs. The `Agent` base class provides a flexible foundation, and by selectively overriding methods, you can extend and customize agent behaviors efficiently.

---

## Next Steps

- **Explore More**: Check out the [Custom Agents Guide](CustomAgents.md) for further insights into creating specialized agents.
- **Dive into Utilities**: Learn about the utility classes and functions in the [Utilities Overview](../Utils/UtilsOverview.md).
- **Understand Prompts**: Review the [Agent Prompts Guide](AgentPrompts.md) to master crafting effective prompts.

---

**Need Help?**

If you have questions or need assistance, feel free to reach out:

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)

---
