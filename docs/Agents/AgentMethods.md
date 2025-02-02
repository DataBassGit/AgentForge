# Agent Methods Guide

Welcome to the **Agent Methods** guide! This section provides an in-depth look at the key methods within the `Agent` base class of **AgentForge**. Understanding these methods is crucial for creating custom agents by subclassing the `Agent` class, allowing you to extend and customize agent behaviors effectively.

---

## Introduction

The `Agent` base class provides a robust template for building agents in **AgentForge**. By subclassing `Agent`, you inherit default functionalities and can override methods to tailor agent behaviors to your specific needs.

**Why Override Methods?**

- **Customization**: Adapt agent behaviors to perform specific tasks.
- **Specialization**: Implement unique processing logic or data handling.
- **Extensibility**: Add new functionalities without altering the base class.

---

## Method Categories

For better understanding, we've grouped the methods into the following categories:

1. [Core Workflow Method](#1-core-workflow-method)
2. [Data Loading Methods](#2-data-loading-methods)
3. [Data Processing Method](#3-data-processing-method)
4. [Prompt Generation Method](#4-prompt-generation-method)
5. [LLM Interaction Method](#5-llm-interaction-method)
6. [Result Handling Methods](#6-result-handling-methods)
7. [Storage Methods](#7-storage-methods)
8. [Customization Hooks](#8-customization-hooks)

---

## 1. Core Workflow Method

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
8. **Cleanup**: Clears `self.data` to free up memory.

**Usage**:

- Call `run()` with any necessary keyword arguments.
- The method handles error logging and returns the final output or `None` if an error occurs.

**Example**:

```python
from agentforge.agent import Agent

agent = Agent(agent_name="ExampleAgent")
output = agent.run(user_input="Hello, AgentForge!")
print(output)
```

>**Note**: In this case we are assuming we have a `ExampleAgent.yaml` prompt template file in the `.agentforge/prompts/` directory for the agent to use.

---

## 2. Data Loading Methods

These methods handle loading various types of data into the agent.

### `load_data(self, **kwargs)`

**Purpose**: Centralizes the data loading process, orchestrating the loading of agent configurations, persona data, storage initialization, and any additional data.

**What It Does**:

- **Loads Agent Configuration Data**: `self.load_agent_data()`
- **Loads Persona Data**: `self.load_persona_data()`
- **Resolves Storage**: `self.resolve_storage()`
- **Loads Data from Storage**: `self.load_from_storage()`
- **Loads Additional Data**: `self.load_additional_data()`
- **Loads Keyword Arguments**: `self.load_kwargs(**kwargs)`

**When to Override**:

- Typically, you don't need to override this method. Instead, override the specific data loading methods as needed.

---

### `load_agent_data(self)`

**Purpose**: Loads the agent's configuration data, including parameters and prompts, and updates `self.data` accordingly.

**What It Does**:

- Retrieves agent data using the `Config` class.
- Updates `self.data` with parameters (`params`) and prompt templates (`prompts`).

**Usage**:

- Automatically called by `load_data()`.

---

### `load_persona_data(self)`

**Purpose**: Loads persona-specific data, enriching the agent's context.

**What It Does**:

- Checks if personas are enabled in the system settings.
- If enabled, loads persona data and updates `self.data` with persona attributes.

**Usage**:

- Automatically called by `load_data()`.

---

### `resolve_storage(self)`

**Purpose**: Initializes the storage system for the agent if storage is enabled in the system settings.

**What It Does**:

- Checks if storage is enabled.
- If enabled, initializes the storage instance and stores it in `self.agent_data['storage']`.

**Usage**:

- Automatically called by `load_data()`.

---

### `load_from_storage(self)`

**Purpose**: Placeholder for loading data from storage systems.

**Usage**:

- **Override this method** if your agent needs to load data from a database or file system.

**Example Override**:

```python
def load_from_storage(self):
    collection_name = 'Memories'  # Name of the collection in the vector database
    query = 'User is thinking about planning a trip'  # A text query to search the specified collection
    self.template_data['stored_values'] = self.agent_data['storage'].query_memory(collection_name, query)
```

---

### `load_additional_data(self)`

**Purpose**: Placeholder for loading any additional data required by the agent.

**Usage**:

- **Override this method** to load custom data necessary for your agent's operation.

**Example Override**:

```python
def load_additional_data(self):
    self.template_data['timestamp'] = datetime.now().isoformat()
```

---

### `load_kwargs(self, **kwargs)`

**Purpose**: Loads variables passed as keyword arguments into `self.data`.

**What It Does**:

- Iterates over `**kwargs` and updates `self.data` with the provided key-value pairs.

**Usage**:

- Automatically called by `load_data()`.

**Example**:

```python
def load_kwargs(self, **kwargs):
    self.template_data.update(kwargs)
```

---

## 3. Data Processing Method

### `process_data(self)`

**Purpose**: Processes the loaded data before it's used in prompt generation.

**Default Behavior**: Does nothing by default.

**Usage**:

- **Override this method** to implement custom data processing logic.

**Example Override**:

```python
def process_data(self):
    # Convert user input to uppercase
    self.template_data['user_input'] = self.template_data['user_input'].upper()
```

---

## 4. Prompt Generation Method

### `generate_prompt(self)`

**Purpose**: Renders the prompt templates using the variables loaded in `self.data`.

**What It Does**:

- Retrieves prompt templates from `self.data['prompts']`.
- Uses `PromptHandling` to:
  - Check the format of the prompts.
  - Render the prompts with current data.
  - Validate the rendered prompts.
- Stores the rendered prompts in `self.prompt`.

**Usage**:

- Automatically called by `run()`.

**When to Override**:

- Typically, you don't need to override this method. Only override it if you need custom prompt rendering logic.

---

## 5. LLM Interaction Method

### `run_llm(self)`

**Purpose**: Executes the language model using the generated prompts.

**What It Does**:

- Retrieves the LLM instance from `self.agent_data['llm']`.
- Retrieves parameters from `self.agent_data.get('params', {})`.
- Adds `agent_name` to the parameters.
- Calls `generate_text` on the LLM with the prompts and parameters.
- Stores the result in `self.result`.

**Usage**:

- Automatically called by `run()`.

**When to Override**:

- Typically, you don't need to override this method. Only override it if you need simulate an LLM response.

**Example Override**:

```python
def run_llm(self):
    # Custom LLM execution
    self.result = "Simulated LLM output"
```

---

## 6. Result Handling Methods

### `parse_result(self)`

**Purpose**: Parses the raw result from the LLM.

**Default Behavior**: Does nothing by default.

**Usage**:

- **Override this method** to implement custom parsing logic.

**Example Override**:

```python
def parse_result(self):
    self.result = json.loads(self.result)
```

---

### `build_output(self)`

**Purpose**: Constructs the final output from the processed data.

**Default Behavior**:

- Sets `self.output = self.result`

**Usage**:

- Automatically called by `run()`.

**When to Override**:

- To customize the final output format.

**Example Override**:

```python
def build_output(self):
    self.output = f"Processed Output: {self.result}"
```

---

## 7. Storage Methods

### `save_to_storage(self)`

**Purpose**: Placeholder for saving data to storage.

**Default Behavior**: Does nothing by default.

**Usage**:

- **Override this method** if your agent needs to save data persistently.

**Notes**:

- The storage instance is available at `self.agent_data['storage']`.
- Ensure that storage is enabled in the system settings (`StorageEnabled: true`).

**Example Override**:

```python
def save_to_storage(self):
    data = self.result
    metadata = {'timestamp': datetime.now().isoformat()}
    self.agent_data['storage'].save_memory(collection_name='Results', data=data, metadata=metadata)
```

---

## 8. Customization Hooks

These methods are designed to be overridden to customize agent behavior:

- **`load_from_storage()`**
- **`load_additional_data()`**
- **`process_data()`**
- **`parse_result()`**
- **`save_to_storage()`**
- **`build_output()`**

By overriding these methods, you can inject custom logic at various points in the agent's workflow.

---

## Putting It All Together: Custom Agent Example

Let's create a custom agent that performs sentiment analysis on user input using an LLM. This example shows how to override methods to customize agent behavior.

### Step 1: Define the Custom Agent

```python
# sentiment_agent.py
from agentforge.agent import Agent


class SentimentAgent(Agent):
    def process_data(self):
        # Clean the user input by stripping leading/trailing whitespace
        self.template_data['cleaned_input'] = self.template_data['user_input'].strip()

    def parse_result(self):
        # Simplify the LLM's response to extract the sentiment
        response = self.result.lower()
        if 'positive' in response:
            sentiment = 'Positive'
        elif 'negative' in response:
            sentiment = 'Negative'
        elif 'neutral' in response:
            sentiment = 'Neutral'
        else:
            sentiment = 'Undetermined'
        self.result = sentiment

    def build_output(self):
        # Build the final output message
        self.output = f"Sentiment Analysis Result: {self.result}"
```

### Step 2: Create the Prompt Template (`SentimentAgent.yaml`)

Place this YAML file in the `.agentforge/prompts/` directory.

```yaml
Prompts:
  System: You are a sentiment analysis assistant.
  User: |+
    Determine if the sentiment of the following text is Positive, Negative, or Neutral.

    Text: "{cleaned_input}"
```

### Step 3: Run the Agent

```python
# run_sentiment_agent.py
from sentiment_agent import SentimentAgent

# Initialize the agent
agent = SentimentAgent()  # The agent name will default to the class name `SentimentAgent` which will load the corresponding prompt template file

# User input
user_input = "  I absolutely love using AgentForge!  "

# Run the agent with the user input
response = agent.run(user_input=user_input)

# Print the output
print(response)
```

### Expected Output

```
Sentiment Analysis Result: Positive
```

---

### Explanation

**Overridden Methods:**

1. **`process_data(self)`**

   - **Purpose**: Cleans the user input before it's used in the prompt.
   - **What It Does**: Strips any leading or trailing whitespace from `self.data['user_input']` and stores it in `self.data['cleaned_input']`.

2. **`parse_result(self)`**

   - **Purpose**: Parses the LLM's response to extract the sentiment.
   - **What It Does**: Checks the LLM's response for keywords 'positive', 'negative', or 'neutral' and assigns the corresponding sentiment to `self.result`.

3. **`build_output(self)`**

   - **Purpose**: Constructs the final output to present to the user.
   - **What It Does**: Formats the output message using the parsed sentiment.

**Key Points:**

- **Custom Data Processing**: By cleaning the user input in `process_data`, we ensure the prompt receives properly formatted text.
- **Prompt Template**: Uses `{cleaned_input}` to insert the processed input into the prompt.
- **Output Construction**: Presents a clear and concise result to the user.

---

## Tips and Best Practices

- **Start Simple**: Begin by subclassing `Agent` without overriding any methods. Ensure your basic agent works before adding complexity.
- **Override as Needed**: Only override methods that require custom logic for your agent's purpose.
- **Test Each Step**: After overriding a method, test your agent to ensure it behaves as expected.
- **Use Descriptive Names**: Name your agents and variables clearly to enhance readability.
- **Leverage Inheritance**: Remember that your custom agent inherits all methods from `Agent`. You can call `super()` to utilize base class functionality.

---

## Additional Functions and Utilities

The `Agent` class utilizes additional utilities that assist with tasks such as:

- **Prompt Handling**: Managed by `self.prompt_handling`.
- **Logging**: Managed by `self.logger`.
- **Configuration Management**: Managed by `self.config`.
- **Data Storage**: Available via `self.agent_data['storage']` if storage is enabled.

For more details, refer to the respective documentation:

- [Prompt Handling Guide](../Utils/PromptHandling.md)
- [Configuration Guide](../Settings/System.md)

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