# Prompt Handling Utility Guide

In **AgentForge**, the `PromptProcessor` class coordinates how prompt templates are read, validated, and dynamically populated with data. While most users won’t need to alter these methods directly, understanding them can be helpful if you want to override or deeply customize prompt logic in your own classes.

---

## Overview

**Key Responsibilities**:

1. **Format Validation**: Ensures that any loaded prompt dictionary has proper keys (`system`, `user`) and that each prompt section is a string or dictionary of sub-sections.  
2. **Variable Extraction**: Identifies placeholders like `{variable_name}` in prompt templates.  
3. **Data Checking**: Validates that required placeholders actually exist and have non-empty values in your agent’s data.  
4. **Rendering**: Substitutes placeholders with actual values and optionally unescapes braces (`/{.../}` → `{...}`).

**Typical Flow**  
When you run an agent, **AgentForge**:

1. Loads the prompt YAML into a dictionary.  
2. Passes it to `PromptProcessor` for structure checks.  
3. Renders each section (`system` and `user`) by substituting placeholders with your agent’s `data`.  
4. Validates the final result so it isn’t empty.

---

## Class Definition

```python
class PromptProcessor:
    """
    A utility class for handling dynamic prompt templates. It supports extracting variables from templates,
    checking for required variables, and rendering templates with provided data.
    """

    pattern = r\"\\{([a-zA-Z_][a-zA-Z0-9_]*)\\}\"

    def __init__(self):
        self.logger = Logger(name=self.__class__.__name__)
```

- **`pattern`**: A regex (`{variable_name}`) for detecting placeholders in your prompt strings.  
- **`logger`**: An instance of **AgentForge**’s logger, used for warnings, errors, and debug messages.

---

## Main Methods

### 1. `check_prompt_format(prompts: dict)`

**Purpose**: Confirms that `prompts` is a dictionary with exactly two keys: `system` and `user`. Also checks if those entries are either strings or dictionaries (sub-sections).

```python
def check_prompt_format(self, prompts):
    # Raises ValueError if format is incorrect
```

**Usage**  
Called internally by **AgentForge** to ensure your prompt YAML is valid. If you define multi-section prompts, they must be nested under `system` or `user`.

---

### 2. `extract_prompt_variables(template: str) -> list`

**Purpose**: Returns a list of placeholder variable names from a single string template.

```python
def extract_prompt_variables(self, template: str) -> list:
    ...
```

**Example**:
```python
variables = processor.extract_prompt_variables("Hello, {user_name}. Today is {day_of_week}.")
# variables = ["user_name", "day_of_week"]
```

---

### 3. `handle_prompt_template(prompt_template: str, data: dict) -> str | None`

**Purpose**: Checks if all required placeholders in `prompt_template` are present and not empty in `data`. Returns `prompt_template` if valid, `None` otherwise.

```python
def handle_prompt_template(self, prompt_template: str, data: dict) -> str | None:
    ...
```

**Behavior**  
1. Grabs placeholders with `extract_prompt_variables`.  
2. If each placeholder in `data` is non-empty, returns `prompt_template`.  
3. Otherwise returns `None`, indicating a missing or empty variable.

---

### 4. `render_prompt_template(template: str, data: dict) -> str`

**Purpose**: Performs the actual substitution of placeholders with data, then unescapes braces.

```python
def render_prompt_template(self, template: str, data: dict) -> str:
    ...
```

**Process**  
1. **Regex Substitution**: For each `{variable}`, replace with `data[variable]` if it exists, or leave the placeholder if it doesn’t.  
2. **Unescape Braces**: Replaces `/{.../}` patterns with `{...}`, letting you embed literal braces in your prompt.

**Example**:
```python
template = "Hello, {user_name}. Your ID is /{id/}."
data = {"user_name": "Alice", "id": 1234}
rendered = processor.render_prompt_template(template, data)
# "Hello, Alice. Your ID is {id}."
```
*(Here, the user intentionally kept `{id}` unrendered by escaping braces.)*

---

### 5. `render_prompts(prompts: dict, data: dict) -> dict`

**Purpose**: Renders both `system` and `user` sections of a prompt dictionary, supporting multi-section sub-prompts.

```python
def render_prompts(self, prompts, data):
    ...
```

**Behavior**  
- If `system` or `user` is a string, treat it as one “Main” sub-prompt.  
- If it’s a dictionary, each key is a named sub-section.  
- For each sub-section, first calls `handle_prompt_template`; if valid, calls `render_prompt_template`. Otherwise logs a message indicating a missing variable.  
- Joins sub-sections with newlines.

**Example**:
```python
prompts = {
  "system": {
    "Intro": "You are an assistant.",
    "Rules": "Please be concise."
  },
  "user": "Hello, {user_name}!"
}

data = {"user_name": "Alice"}
rendered = processor.render_prompts(prompts, data)
print(rendered["system"])
# "You are an assistant.\nPlease be concise."
print(rendered["user"])
# "Hello, Alice!"
```

---

### 6. `validate_rendered_prompts(rendered_prompts: dict)`

**Purpose**: Ensures the final `system` and `user` strings aren’t empty after rendering.

```python
def validate_rendered_prompts(self, rendered_prompts):
    ...
```

- Raises a `ValueError` if either is blank (`""` or whitespace).

---

### 7. `unescape_braces(template: str) -> str`

**Purpose**: Converts `/{.../}` → `{...}` so you can deliberately keep braces in your final text without them being interpreted as placeholders.

```python
def unescape_braces(template: str) -> str:
    ...
```

---

## Usage Within Agents

While you can call these methods directly if you’re building something unusual, **AgentForge** typically calls them automatically when an agent runs. Under the hood:

1. **Check Prompt Format** (from loaded YAML).  
2. **Render** each prompt section.  
3. **Validate** that the final prompt is not empty.

**Example**:

```python
from agentforge.agent import Agent

class GreetingAgent(Agent):
    def load_additional_data(self):
        self.template_data["user_name"] = "Alice"

# Prompt file might say:
#   system: "You are a greeting agent."
#   user: "Hello, {user_name}!"
```

When `agent.run()` is called, **AgentForge** uses `PromptProcessor` to fill in `{user_name}` automatically.

---

## When to Override

1. **Custom Placeholders**: If you want a different placeholder style (e.g., `<<var>>`), you might subclass and change `pattern`.  
2. **Conditional Rendering**: If you need advanced logic for “sub-prompts,” e.g., only show certain text if `data["is_vip"]` is true.  
3. **Multi-Language**: If you prefer different code fences or advanced ways of escaping braces.

> **IMPORTANT NOTE**: Overriding prompt logic can break backward compatibility with existing YAML files. Tread carefully!!!

---

## Example Walkthrough

Suppose you have a prompt dictionary:

```python
prompts = {
  "system": "You are a helpful assistant.",
  "user": {
    "Greet": "Hello, {user_name}.",
    "Ask": "How are you doing today, {user_name}?"
  }
}
```

And data:

```python
data = { "user_name": "Alice" }
```

1. `check_prompt_format(prompts)`: Confirms keys = `system`, `user`.  
2. `render_prompts(prompts, data)`:  
   - For `system`: It's a string → "Main" sub-prompt = `"You are a helpful assistant."`.  
     - `handle_prompt_template("You are a helpful assistant.", data)` → returns same string since no placeholders.  
     - `render_prompt_template(...)` → `"You are a helpful assistant."`.  
   - For `user`: It's a dict with sub-sections `Greet`, `Ask`.  
     - `handle_prompt_template("Hello, {user_name}.", data)` → placeholders = `[user_name]`, found in data, so returns the template.  
     - `render_prompt_template("Hello, {user_name}.", data)` → `"Hello, Alice."`  
     - Same for `Ask` → `"How are you doing today, Alice?"`  
   - Joins sub-sections with newlines: `User` prompt = `"Hello, Alice.\nHow are you doing today, Alice?"`  
3. `validate_rendered_prompts(...)`: Both `system` and `user` are non-empty.  
4. Final results are:

```
{
  "system": "You are a helpful assistant.",
  "user": "Hello, Alice.\nHow are you doing today, Alice?"
}
```

---

## Best Practices

1. **Use Consistent Variable Names**: Stick to `[a-zA-Z_][a-zA-Z0-9_]*` to avoid unexpected parse failures.  
2. **Be Mindful of Escaped Braces**: `/{something/}` will not be replaced with data. If you see these patterns, they’ll remain as literal braces in the final output.  
3. **Keep Sub-Prompts Manageable**: Large YAML with too many sub-sections can become confusing. Possibly break them into smaller agent files or keep them well-documented.

---

## Conclusion

The `PromptProcessor` in **AgentForge** underpins how prompts are rendered and validated. Most developers will benefit from letting the framework handle prompt substitution. However, if you need deeper customization—like unique placeholder styles or conditional logic—understanding this utility is key. Proceed carefully, as changing the prompt flow can break existing templates.

**Need Help?**  
- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)  
- **Discord**: [Join our Discord Server](https://discord.gg/ttpXHUtCW6)
