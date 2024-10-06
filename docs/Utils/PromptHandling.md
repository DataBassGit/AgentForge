# PromptHandling Utility Guide

## Introduction

The `PromptHandling` class in **AgentForge** is a utility for managing dynamic prompt templates. It allows you to create flexible and responsive prompts by handling variable substitution within templates. This utility is essential for generating prompts that adapt to different contexts, user inputs, or data states.

>**Note:** The `PromptHandling` utility is primarily used internally by the **AgentForge** framework for rendering prompts. Most developers won't need to interact with it directly, as the **Agent** base class automatically handles prompt rendering. This guide is intended for advanced users who wish to implement custom prompt handling and rendering logic beyond the default framework capabilities.

---

## Overview

The `PromptHandling` class provides methods to:

- **Extract Variables**: Identify variables within prompt templates.
- **Validate Prompts**: Ensure that all required variables are present in the data.
- **Render Prompts**: Substitute variables with actual values to generate final prompts.
- **Validate Rendered Prompts**: Ensure that the rendered prompts are not empty.

---

## Class Definition

```python
class PromptHandling:
    def __init__(self):
        self.logger = Logger(name=self.__class__.__name__)
    
    # Method definitions...
```

---

## Methods

### 1. `extract_prompt_variables(template: str) -> list`

**Purpose**: Extracts variable names from a prompt template.

**Parameters**:

- `template` (str): The prompt template containing variables enclosed in curly braces `{}`.

**Returns**:

- `list`: A list of variable names found in the template.

**Example Usage**:

```python
from agentforge.utils.PromptHandling import PromptHandling

prompt_handler = PromptHandling()
template = "Hello, {user_name}! Today is {day_of_week}."
variables = prompt_handler.extract_prompt_variables(template)
print(variables)  # Output: ['user_name', 'day_of_week']
```

---

### 2. `handle_prompt_template(prompt_template: str, data: dict) -> Optional[str]`

**Purpose**: Checks if all required variables in a prompt template are present and non-empty in the provided data. Returns the template if conditions are met, or `None` otherwise.

**Parameters**:

- `prompt_template` (str): The prompt template to check.
- `data` (dict): A dictionary containing data values for variables.

**Returns**:

- `str` or `None`: The original prompt template if all variables are present and non-empty; `None` otherwise.

**Example Usage**:

```python
data = {'user_name': 'Alice', 'day_of_week': 'Monday'}
template = "Hello, {user_name}! Today is {day_of_week}."

valid_template = prompt_handler.handle_prompt_template(template, data)
if valid_template:
    print("Template is valid.")
else:
    print("Template is missing required variables.")
```

---

### 3. `render_prompt_template(template: str, data: dict) -> str`

**Purpose**: Renders a prompt template by replacing variables with their corresponding values from the provided data.

**Parameters**:

- `template` (str): The prompt template containing variables.
- `data` (dict): A dictionary containing data values for variables.

**Returns**:

- `str`: The rendered prompt with variables substituted.

**Example Usage**:

```python
template = "Hello, {user_name}! Today is {day_of_week}."
data = {'user_name': 'Alice', 'day_of_week': 'Monday'}

rendered_prompt = prompt_handler.render_prompt_template(template, data)
print(rendered_prompt)  # Output: "Hello, Alice! Today is Monday."
```

---

### 4. `render_prompts(prompts: dict, data: dict) -> dict`

**Purpose**: Renders the `System` and `User` prompts by processing all sections and substituting variables.

**Parameters**:

- `prompts` (dict): A dictionary containing `System` and `User` prompts, which can be strings or dictionaries of sub-prompts.
- `data` (dict): A dictionary containing data values for variables.

**Returns**:

- `dict`: A dictionary containing the rendered `System` and `User` prompts.

**Example Usage**:

```python
prompts = {
    'System': {
        'Introduction': "You are a helpful assistant.",
        'Instructions': "Assist the user with any questions."
    },
    'User': {
        'Greeting': "Hello, {user_name}!",
        'Question': "How can I assist you today?"
    }
}

data = {'user_name': 'Alice'}

rendered_prompts = prompt_handler.render_prompts(prompts, data)
print(rendered_prompts['User'])
```

**Output**:

```
Hello, Alice!
How can I assist you today?
```

---

### 5. `check_prompt_format(prompts: dict) -> None`

**Purpose**: Validates the format of the prompts dictionary to ensure it contains **ONLY** `System` and `User` keys and that their values are either strings or dictionaries.

**Parameters**:

- `prompts` (dict): The dictionary containing the prompts.

**Raises**:

- `ValueError`: If the prompts dictionary is incorrectly formatted.

**Example Usage**:

```python
prompts = {
    'System': "You are an assistant.",
    'User': "Hello, {user_name}!"
}

prompt_handler.check_prompt_format(prompts)
```

>**Note**: If the check fails it will trigger an error asking the user to check their prompt templates or the data being passed to the agent.

---

### 6. `validate_rendered_prompts(rendered_prompts: dict) -> None`

**Purpose**: Validates that the rendered prompts are not empty after variable substitution.

**Parameters**:

- `rendered_prompts` (dict): A dictionary containing the rendered prompts.

**Raises**:

- `ValueError`: If any of the rendered prompts are empty.

**Example Usage**:

```python
rendered_prompts = {
    'System': "You are an assistant.",
    'User': ""
}

prompt_handler.validate_rendered_prompts(rendered_prompts)
# Raises ValueError because 'User' prompt is empty
```

---

### 7. `unescape_braces(template: str) -> str`

**Purpose**: Replaces escaped braces `/{ ... /}` with actual braces `{ ... }` in the template.

**Parameters**:

- `template` (str): The prompt template containing escaped braces.

**Returns**:

- `str`: The template with escaped braces unescaped.

**Example Usage**:

```python
template = "Display the set: /{1, 2, 3/}"
unescaped_template = prompt_handler.unescape_braces(template)
print(unescaped_template)  # Output: "Display the set: {1, 2, 3}"
```

---

## Practical Application

The `PromptHandling` utility is particularly useful when:

- **Creating Dynamic Prompts**: Generate prompts that adapt based on user input or other dynamic data.
- **Managing Complex Prompts**: Handle prompts with multiple sections and variables.
- **Ensuring Prompt Integrity**: Validate that all necessary data is present before rendering prompts.

---

## Integration with Agents

While you can use `PromptHandling` methods directly, the **Agent** base class in **AgentForge** already integrates these functionalities. When you run an agent, it automatically:

1. Loads the prompt templates.
2. Uses `PromptHandling` to render prompts with the data in `self.data`.
3. Validates the rendered prompts.

**Example in Agent Context**:

```python
class MyAgent(Agent):
    def load_additional_data(self):
        self.data['user_name'] = 'Alice'
```

In this example, the agent will use `self.data['user_name']` when rendering prompts that contain `{user_name}`.

---

## Example: Using PromptHandling in an Agent

Suppose you have a prompt template:

```yaml
# .agentforge/prompts/GreetingAgent.yaml
Prompts:
  System: You are a helpful assistant.
  User: {user_name} has arrived at {platform_name}. Please welcome them.
```

And an agent:

```python
from agentforge import Agent

class GreetingAgent(Agent):
    def load_additional_data(self):
        self.data['user_name'] = 'Alice'
        self.data['platform_name'] = 'AgentForge'

# Running the agent
agent = GreetingAgent()
output = agent.run()
print(output)
```

**Rendered System Prompt**:
```text
You are a helpful assistant.
```

**Rendered User Prompt**:
```text
Alice has arrived at AgentForge. Please welcome them.
```

**Expected Output**:

```
Hello, Alice! Welcome to AgentForge.
```

---

## Best Practices

- **Provide All Required Data**: Ensure that all variables used in your prompt templates are present in `data` before rendering.
- **Validate Prompts**: Use `validate_rendered_prompts` to catch any empty prompts early.
- **Handle Missing Data**: Implement logic to handle cases where data might be missing to prevent runtime errors.

---

## Conclusion

The `PromptHandling` utility is a powerful tool for managing dynamic prompts in **AgentForge**. By understanding and utilizing its methods, you can create agents that interact more effectively and responsively with users or other systems.

---

**Need Help?**

If you have questions or need assistance, feel free to reach out:

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)

---