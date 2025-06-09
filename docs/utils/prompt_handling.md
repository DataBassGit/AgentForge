# Prompt Handling Utility Guide

In **AgentForge**, the `PromptProcessor` class manages prompt templates: extracting variables, validating required data, and rendering prompts with dynamic content. This utility is essential for building agents that use flexible, data-driven prompts.

> **Note:** In AgentForge, prompt template YAML files are loaded automatically by the framework. You should define your prompts in these YAML files rather than hardcoding them in your code unlike the examples below which do so solely for demostration purposed. For more details on prompt file structure and usage, see [AgentPrompts.md](../agents/agent_prompts.md).

---

## Overview

**Key Responsibilities:**

1. **Variable Extraction**: Identifies placeholders like `{variable_name}` or `{nested.key}` in prompt templates.
2. **Data Checking**: Validates that required placeholders exist and have non-empty values in your agent's data.
3. **Rendering**: Substitutes placeholders with actual values and unescapes braces (`/{.../}` → `{...}`).
4. **Persona Markdown**: Renders persona static content as Markdown for system prompts.

---

## Class Definition

```python
class PromptProcessor:
    """
    Handles dynamic prompt templates: extracting variables, checking for required data, and rendering with provided values.
    """
    pattern = r"\{([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\}"
    def __init__(self):
        self.logger = Logger(name=self.__class__.__name__, default_logger=self.__class__.__name__.lower())
```

- **`pattern`**: Regex for detecting placeholders, supporting dot notation for nested keys (e.g., `{foo.bar}`).
- **`logger`**: An instance of AgentForge's logger for warnings, errors, and debug messages.

---

## Main Methods

### 1. `extract_prompt_variables(template: str) -> list`

**Purpose**: Returns a list of placeholder variable names (including nested, e.g., `foo.bar`) from a template string.

**Example**:
~~~python
processor = PromptProcessor()
variables = processor.extract_prompt_variables("Hello, {user.name}. Today is {day}.")
print(variables)  # ["user.name", "day"]
~~~

---

### 2. `handle_prompt_template(prompt_template: str, data: dict) -> str | None`

**Purpose**: Checks if all required placeholders in `prompt_template` are present and not empty in `data`. Returns the template if valid, `None` otherwise.

**Example**:
~~~python
data = {"user": {"name": "Alice"}, "day": "Monday"}
template = "Hello, {user.name}. Today is {day}."
result = processor.handle_prompt_template(template, data)
print(result)  # "Hello, {user.name}. Today is {day}."
~~~

---

### 3. `render_prompt_template(template: str, data: dict) -> str`

**Purpose**: Substitutes placeholders in the template with values from `data`, supporting nested keys. Unescapes braces (`/{.../}` → `{...}`).

**Example**:
~~~python
data = {"user": {"name": "Alice"}, "id": 1234}
template = "Hello, {user.name}. Your ID is /{id/}."
rendered = processor.render_prompt_template(template, data)
print(rendered)  # "Hello, Alice. Your ID is {id}."
~~~

---

### 4. `render_prompts(prompts: dict, data: dict) -> dict`

**Purpose**: Renders both `system` and `user` sections of a prompt dictionary, supporting multi-section sub-prompts. Returns a dictionary with rendered `system` and `user` prompts.

**Example**:
~~~python
prompts = {
  "system": {
    "Intro": "You are an assistant.",
    "Rules": "Please be concise."
  },
  "user": "Hello, {user.name}!"
}
data = {"user": {"name": "Alice"}}
rendered = processor.render_prompts(prompts, data)
print(rendered["system"])
# "You are an assistant.\nPlease be concise."
print(rendered["user"])
# "Hello, Alice!"
~~~

---

### 5. `build_persona_markdown(static_content: dict, persona_settings: dict) -> str`

**Purpose**: Builds a Markdown representation of persona static content for system prompt injection, truncating if it exceeds a character cap.

---

### 6. `value_to_markdown(val: Any, indent: int = 0) -> str`

**Purpose**: Renders a dict, list, or scalar into minimalist Markdown, with optional indentation.

---

### 7. `unescape_braces(template: str) -> str`

**Purpose**: Converts `/{.../}` to `{...}` so you can keep literal braces in your final text.

---

## Nested Placeholders

- Placeholders support dot notation for nested dictionary lookups (e.g., `{user.name}` will look for `data["user"]["name"]`).

---

## Error Handling

- If required variables are missing or empty, the prompt section is skipped or `None` is returned. If a rendered prompt is empty, a `ValueError` is raised.

---

## Usage Example

~~~python
from agentforge.utils.prompt_processor import PromptProcessor

processor = PromptProcessor()
prompts = {
  "system": "You are a helpful assistant.",
  "user": {
    "Greet": "Hello, {user.name}.",
    "Ask": "How are you doing today, {user.name}?"
  }
}
data = {"user": {"name": "Alice"}}
rendered = processor.render_prompts(prompts, data)
print(rendered["system"])
# "You are a helpful assistant."
print(rendered["user"])
# "Hello, Alice.\nHow are you doing today, Alice?"
~~~
