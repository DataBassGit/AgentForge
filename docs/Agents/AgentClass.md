# `Agent` Class Documentation

Welcome to the documentation of the `Agent` class. This foundational class is central to the **AgentForge** framework, enabling the creation, management, and operation of agents. It provides core functionalities essential for agents, serving as a robust template for both general and specialized implementations.

---

## Overview of the `Agent` Class

The `Agent` class is designed to:

- Serve as the base class for all agents within the **AgentForge** framework.  
- Provide essential attributes and methods for agent operation.  
- Dynamically load and manage agent configurations, prompt templates, personas, and storage.  
- Simplify the creation of custom agents through method overriding.  
- Allow flexible naming of agents by accepting an optional `agent_name` parameter.

By subclassing the `Agent` class (or simply instantiating it with a YAML prompt file), developers can create agents that inherit default behaviors and override methods to implement custom logic.

---

## Class Definition

```python
from .config import Config
from agentforge.apis.base_api import BaseModel
from agentforge.utils.logger import Logger
from agentforge.utils.prompt_processor import PromptProcessor
from typing import Any, Dict, Optional

class Agent:
    def __init__(self, agent_name: Optional[str] = None, log_file: Optional[str] = 'agentforge'):
        """
        Initializes an Agent instance, setting up its name, logger, data attributes, and agent-specific configurations.
        It attempts to load the agent's configuration data and storage settings.

        Args:
            agent_name (Optional[str]): The name of the agent. If not provided, the class name is used.
            log_file (Optional[str]): The name of the log file. Defaults to 'agentforge'.
        """
        self.agent_name = agent_name if agent_name else self.__class__.__name__
        self.logger = Logger(self.agent_name, log_file)
        self.config = Config()
        self.prompt_processor = PromptProcessor()

        self.agent_data: Optional[Dict[str, Any]] = None
        self.persona: Optional[Dict[str, Any]] = None
        self.model: Optional[BaseModel] = None
        self.prompt_template: Optional[Dict[str, Any]] = None
        self.template_data: Dict[str, Any] = {}
        self.prompt: Optional[Dict[str, str]] = None
        self.result: Optional[str] = None
        self.output: Optional[str] = None
        self.images: Optional[list[str]] = []

        # Load and validate agent data during initialization
        self.initialize_agent_config()
```

### Class Attributes

- **`agent_name`**  
  The agent’s name, set by the `agent_name` parameter or defaulting to the class name.

- **`logger`**  
  A `Logger` instance for writing logs to both the console and file.

- **`config`**  
  An instance of `Config` to load the agent’s configuration data (prompts, parameters, personas, etc.).

- **`prompt_processor`**  
  An instance of `PromptProcessor` responsible for rendering and validating the final prompts.

- **`agent_data`**  
  A dictionary holding the agent’s configuration data (loaded from YAML or other sources).

- **`persona`**  
  A dictionary containing persona-related information (if personas are enabled).

- **`model`**  
  A reference to the LLM instance, which must implement the `BaseModel` interface.

- **`prompt_template`**  
  A dictionary with the agent’s prompt structure (usually containing `system` and `user`).

- **`template_data`**  
  A general-purpose dictionary for any runtime data to be substituted into the final prompt.

- **`prompt`**  
  The rendered prompt after merging `prompt_template` with `template_data`.

- **`result`**  
  The raw output from the LLM or a simulated string in debug mode.

- **`output`**  
  The final processed string after any optional post-processing.

- **`images`**  
  An optional list of image references to pass along to the LLM (or to include in the final output).

---

## Agent Workflow

### `run(self, **kwargs) -> Optional[str]`

The `run` method orchestrates the following sequence to produce the final output:

```python
def run(self, **kwargs: Any) -> Optional[str]:
    try:
        self.logger.info(f"{self.agent_name} - Running...")
        self.load_data(**kwargs)
        self.process_data()
        self.render_prompt()
        self.run_llm()
        self.parse_result()
        self.save_to_storage()
        self.build_output()
        self.logger.info(f"{self.agent_name} - Done!")
    except Exception as e:
        self.logger.error(f"Agent execution failed: {e}")
        return None
    return self.output
```

1. **Logging Start**  
   Logs that the agent is beginning its workflow.  
2. **`load_data(**kwargs)`**  
   Gathers all necessary data (configuration, persona data, storage references, etc.) and merges in keyword arguments.  
3. **`process_data()`**  
   A hook to transform or validate data before prompt rendering.  
4. **`render_prompt()`**  
   Uses `prompt_processor` to substitute placeholders in the YAML-defined prompt (`system` and `user`).  
5. **`run_llm()`**  
   Passes the compiled prompts and any additional parameters to the LLM, saving its output in `self.result`.  
6. **`parse_result()`**  
   An optional method for post-processing the LLM’s raw text.  
7. **`save_to_storage()`**  
   If storage is enabled, saves relevant data.  
8. **`build_output()`**  
   Sets `self.output` as the final user-facing result.  
9. **Completion**  
   Logs a message indicating the run is complete and returns `self.output`.

---

## Configuration Loading

### `initialize_agent_config()`

This method is called at initialization (and optionally re-called if “on_the_fly” updates are enabled).

```python
def initialize_agent_config(self) -> None:
    self.load_agent_data()
    self.load_prompt_template()
    self.load_persona_data()
    self.load_model()
    self.resolve_storage()
```

1. **`load_agent_data()`**  
   Loads configuration details like `params`, `prompts`, `settings`.  
2. **`load_prompt_template()`**  
   Ensures valid prompt structures (commonly `system` and `user` keys in lowercase).  
3. **`load_persona_data()`**  
   If personas are enabled, loads persona info and merges it into `template_data`.  
4. **`load_model()`**  
   References the LLM assigned to this agent.  
5. **`resolve_storage()`**  
   Sets up the storage instance if `storage.enabled` is `True`.

---

## Data Methods

### `load_data(**kwargs)`

```python
def load_data(self, **kwargs: Any) -> None:
    if self.agent_data['settings']['system']['misc'].get('on_the_fly', False):
        self.initialize_agent_config()

    self.load_from_storage()
    self.load_additional_data()
    self.template_data.update(kwargs)
```

- **On-the-Fly Reloading**  
  Re-invokes `initialize_agent_config()` if `on_the_fly` is enabled.  
- **`load_from_storage()`**  
  Placeholder method for reading from a DB or other storage systems.  
- **`load_additional_data()`**  
  Placeholder for agent-specific data fetch logic.  
- **Merging Keyword Arguments**  
  Any `**kwargs` passed into `run()` are appended to `template_data`.

### `load_from_storage()`

A placeholder for reading from persistent storage. Override if you need custom queries:

```python
def load_from_storage(self) -> None:
    pass
```

### `load_additional_data()`

A placeholder for loading extra data your agent may need:

```python
def load_additional_data(self) -> None:
    pass
```

---

## Processing & Prompt Rendering

### `process_data()`

```python
def process_data(self) -> None:
    pass
```

Override to transform or validate `template_data` before prompt rendering. For example, cleaning user input or adding timestamps.

### `render_prompt()`

```python
def render_prompt(self) -> None:
    self.prompt = self.prompt_processor.render_prompts(self.prompt_template, self.template_data)
    self.prompt_processor.validate_rendered_prompts(self.prompt)
```

- **Rendering**: Substitutes placeholders in the `system` and `user` YAML blocks with values from `template_data`.  
- **Validation**: Ensures the final prompt is well-structured (commonly `{ "system": "...", "user": "..." }`).

---

## LLM Interaction

### `run_llm()`

```python
def run_llm(self) -> None:
    if self.agent_data['settings']['system']['debug'].get('mode', False):
        self.result = self.agent_data['simulated_response']
        return

    params: Dict[str, Any] = self.agent_data.get("params", {})
    params['agent_name'] = self.agent_name
    if self.images:
        params['images'] = self.images

    self.result = self.model.generate(self.prompt, **params).strip()
```

1. **Debug Mode**  
   Uses a simulated response if `debug.mode` is `True`.  
2. **Params**  
   Loads generation parameters (e.g., `temperature`, `max_tokens`) from the agent config.  
3. **Image Support**  
   Optionally appends image references to the model call if your agent works with images.  
4. **Generation**  
   Invokes `self.model.generate(...)` and stores the result in `self.result`.

---

## Result Handling

### `parse_result()`

```python
def parse_result(self) -> None:
    pass
```

Override to apply additional logic—e.g., parsing JSON, extracting structured data, or filtering out unwanted text.

### `build_output()`

```python
def build_output(self) -> None:
    self.output = self.result
```

Sets the final user-facing string. By default, it’s simply the raw LLM output. Override to add formatting, user-friendly messages, or combined data.

---

## Storage Handling

### `resolve_storage()`

```python
def resolve_storage(self) -> None:
    storage_enabled = self.agent_data['settings']['storage']['options'].get('enabled', False)
    if not storage_enabled:
        self.agent_data['storage'] = None
        return

    # Future logic for storage adapters
```

### `save_to_storage()`

```python
def save_to_storage(self) -> None:
    pass
```

A placeholder for storing data (such as conversation history or final results). Override to interact with a DB or vector store when `storage_enabled` is `True`.

---

## Putting It All Together: A Custom Agent Example

The following example shows how to override select methods for specialized behavior—here, simple sentiment analysis.

### Step 1: Define the Custom Agent

```python
# sentiment_agent.py
from agentforge.agent import Agent
import json

class SentimentAgent(Agent):
    def process_data(self):
        # Strip leading/trailing whitespace from user input
        if 'user_input' in self.template_data:
            self.template_data['cleaned_input'] = self.template_data['user_input'].strip()

    def parse_result(self):
        # Interpret the LLM's response to classify sentiment
        lower_resp = self.result.lower()
        if 'positive' in lower_resp:
            sentiment = 'Positive'
        elif 'negative' in lower_resp:
            sentiment = 'Negative'
        elif 'neutral' in lower_resp:
            sentiment = 'Neutral'
        else:
            sentiment = 'Undetermined'
        self.result = sentiment

    def build_output(self):
        # Construct a final human-readable message
        self.output = f"Sentiment Analysis Result: {self.result}"
```

### Step 2: Create the Prompt Template (`sentimentagent.yaml`)

Place this in `.agentforge/prompts/`:

```yaml
prompts:
  system: | 
    You are a sentiment analysis assistant.
  user: | 
    Determine if the sentiment of the following text is Positive, Negative, or Neutral.
    Text: "{cleaned_input}"
```

> **Note**: Keys are lowercase (`prompts`, `system`, `user`) for consistency.

### Step 3: Run the Agent

```python
# run_sentiment_agent.py
from sentiment_agent import SentimentAgent

agent = SentimentAgent()

user_input = "  I absolutely love using AgentForge!  "
response = agent.run(user_input=user_input)

print(response)
# Expected: "Sentiment Analysis Result: Positive"
```

**Why It Works**:

1. **`process_data`**  
   Trims whitespace from `user_input` and stores the result in `cleaned_input`.  
2. **Prompt Rendering**  
   `{cleaned_input}` is substituted into the `user` section of the prompt.  
3. **LLM Call**  
   The LLM receives a question about sentiment analysis on the provided text.  
4. **`parse_result`**  
   Simplifies the LLM’s response to a single word: `Positive`, `Negative`, `Neutral`, or `Undetermined`.  
5. **`build_output`**  
   Wraps that sentiment in a user-friendly message.

---

## Tips and Best Practices

- **Start Simple**: Begin by instantiating `Agent` with a YAML file to confirm basic functionality.  
- **Override as Needed**: Only override methods that are relevant to your custom logic.  
- **Use Descriptive Names**: Name your agent classes and YAML files clearly (e.g., `SentimentAgent` ↔ `sentimentagent.yaml`).  
- **Debug Mode**: Leverage `debug.mode` and `simulated_response` to rapidly test your agent’s workflow without incurring API calls.  
- **Storage**: If you need to store or retrieve data persistently, implement custom logic in `load_from_storage` and `save_to_storage`.

---

## Conclusion and Next Steps

By understanding and utilizing these methods and attributes, you can create powerful agents tailored to your specific needs. The `Agent` class is at the core of **AgentForge**, offering a coherent, extensible framework for loading configurations, rendering prompts, calling an LLM, handling results, and optionally using storage.

- **Prompt Crafting**: Learn more about structuring `.agentforge/prompts/` files in [Agent Prompts](AgentPrompts.md).  
- **Advanced Customization**: If you need deeper control—like advanced persona logic or specialized result parsing—consider building a custom agent as shown above. You can find additional guidance in [Custom Agents](CustomAgents.md).  
- **Utilities**: Explore time-saving utilities and helper functions in [Utils Overview](../Utils/UtilsOverview.md).

**Need Help?**

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)  
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)  

---