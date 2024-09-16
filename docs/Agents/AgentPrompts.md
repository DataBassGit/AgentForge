# Agent Prompts Guide

## Introduction

Prompts are at the heart of the **AgentForge** framework. They define how agents interact with users and Large Language Models (LLMs). Written in **YAML** format, prompts allow you to craft dynamic, context-aware conversations and behaviors for your agents.

---

## Organizing Agent Prompt Files

Each agent requires a corresponding **YAML** prompt file located within the `.agentforge/agents/` directory of your project. This file contains the prompt templates that guide the agent's interactions.

### Naming Convention

- **Consistency is Key**: The **YAML** file **must** have the same name as the agent's class name defined in your code.

  **Example**:

  ```python
  # echo_agent.py
  from agentforge import Agent

  class EchoAgent(Agent):
      pass  # Agent name is 'EchoAgent'
  ```

  - The corresponding prompt file should be named `EchoAgent.yaml` and placed in the `.agentforge/agents/` directory or any of its subdirectories.

### Directory Structure

You can organize your agents and prompt files into subdirectories for better categorization, especially when dealing with multiple agents.

**Example Structure**:

```
.agentforge/
└── agents/
    ├── EchoAgent.yaml
    ├── topic_qanda/
    │   ├── QuestionGeneratorAgent.yaml
    │   └── AnswerAgent.yaml
    └── other/
        └── HelperAgent.yaml
```

- The system automatically searches all subdirectories within `.agentforge/agents/` to find agent prompt files.
- **Tip**: Organize agents by functionality or project modules for easier management.

---

## Understanding Prompt Files

Prompt files define the dialogue structures that agents use when interacting with users and LLMs. They are composed of one or more **sub-prompts**, which can be static or dynamic.

### Basic Structure

A simple prompt file (`EchoAgent.yaml`) might look like this:

```yaml
Prompts:
  System: You are an assistant that echoes the user's input.
  User: |+
    {user_input}
```

- **Prompts**: The root key containing all sub-prompts.
- **Sub-Prompts**: `System` and `User` in this example.
- **Variables**: Placeholders within `{}` that will be dynamically replaced at runtime.

---

## Dynamic Variables in Prompts

Dynamic variables allow prompts to be flexible and context-aware. Any text enclosed in `{}` that matches a valid Python variable name is considered a variable.

### How Variables Work

- **Detection**: The `PromptHandling` class detects variables enclosed in `{}` that conform to Python variable naming conventions (e.g., letters, numbers, and underscores, not starting with a number).
- **Replacement**: At runtime, these variables are replaced with the corresponding values provided to the agent.

**Example**:

```yaml
Prompts:
  System: You are a helpful assistant.
  User: |+
    {greeting}
```

- If you run the agent with `agent.run(greeting="Hello, AgentForge!")`, the `{greeting}` variable will be replaced with "Hello, AgentForge!".

### Important Notes

- **Variable Naming**: Ensure variable names are valid Python identifiers (e.g., `user_input`, `context`, `task_details`). Variables with invalid names (e.g., containing spaces or special characters) are **not** considered variables and will be left untouched.
- **Unused Variables**: If a variable in the prompt is not provided at runtime, the sub-prompt containing it will **not** be rendered.

---

## Crafting Dynamic Prompts with Sub-Prompts

Sub-prompts allow you to create modular and optional sections within your prompts, enhancing flexibility.

### How Sub-Prompts Work

- Each key under `Prompts` is a sub-prompt.
- **Optional Rendering**: A sub-prompt is only rendered if all its variables are provided.
- **Static Text**: Sub-prompts without variables or with invalid variable placeholders are always rendered.

### Example Prompt File (`QuestionGeneratorAgent.yaml`)

```yaml
Prompts:
  System: You are an assistant that generates questions based on a topic.
  Topic: |+
    The topic is: {topic}
  Instruction: Please generate an insightful question about the topic.
```

- **Sub-Prompts**:
  - `System`: Static text, always rendered.
  - `Topic`: Contains `{topic}`, rendered only if `topic` is provided.
  - `Instruction`: Static text, always rendered.

### Usage Example

```python
from question_generator_agent import QuestionGeneratorAgent

agent = QuestionGeneratorAgent()
response = agent.run(topic="artificial intelligence")
print(response)
```

- If `topic` is provided, the `Topic` sub-prompt is included.
- If `topic` is not provided, the `Topic` sub-prompt is omitted.

**Rendered Prompt** (with `topic` provided):

```
You are an assistant that generates questions based on a topic.

The topic is: artificial intelligence

Please generate an insightful question about the topic.
```

---

## Handling JSON and Special Characters

When crafting prompts that include code snippets, JSON structures, or specific response formats, it's important to understand how variable detection works to ensure placeholders are not unintentionally replaced.

### Variable Detection Rules

- **Valid Variables**: Only text within `{}` that matches a valid Python variable name is considered a variable and is replaced if a corresponding value is provided.
  - Valid variable names consist of letters, numbers, and underscores, and cannot start with a number.
- **Invalid Variables**: Placeholders within `{}` that do **not** match valid Python variable names are left untouched. This allows you to include templates or placeholders in your prompts without interference.

### Example: Response Format with Placeholders

Suppose you want the agent to provide a response in a specific format:

```yaml
Prompts:
  System: You are a helpful assistant.
  Instruction: |+
    Please respond in the following format:

    Thoughts: {your thoughts goes here}
    Response: {your response goes here, keep it short}
```

- **Explanation**:
  - `{your thoughts go here}` and `{your response goes here, keep it short}` are **not** valid Python variable names because they contain spaces and/or special characters. 
  - These placeholders will be left as-is in the rendered prompt, allowing the LLM to fill in the appropriate content.

### Complete Example with System and Instruction Prompts

**Prompt File (`StructuredResponseAgent.yaml`):**

```yaml
Prompts:
  System: You are a helpful assistant.
  Instruction: |+
    Please perform the following task:

    {task_description}

    Please respond in the following format:

    Thoughts: {your thoughts go here}
    Response: {your response goes here, keep it short, keep it short}
```

- **Variables**:
  - `{task_description}` is a valid variable and will be replaced if provided.
  - `{your thoughts go here}` and `{your response goes here, keep it short}` are invalid variable names and will remain in the prompt.

**Usage Example:**

```python
from structured_response_agent import StructuredResponseAgent

agent = StructuredResponseAgent()
response = agent.run(task_description="Explain the significance of the Turing Test.")
print(response)
```

**Rendered Prompt:**

```
You are a helpful assistant.

Please perform the following task:

Explain the significance of the Turing Test.

Please respond in the following format:

Thoughts: {your thoughts go here}
Response: {your response goes here, keep it short}
```

- The LLM will see `{your thoughts go here}` and `{your response goes here, keep it short}` as part of the response format and can fill in these sections accordingly.

### Handling Code Snippets

When including code or JSON structures in your prompts, ensure that any curly braces within them do not contain valid variable names unless you intend for them to be replaced.

**Example:**

```yaml
Prompts:
  CodeExample: |+
    Here's a Python function:

    def greet(name):
        return f"Hello, {name}!"
```

- **Explanation**:
  - `{name}` inside the code snippet is a valid variable name.
  - If `name` is not provided when running the agent, the entire `CodeExample` sub-prompt will **not** be rendered.
  - To prevent `{name}` from being interpreted as a variable, you can modify it to an invalid variable name or escape it.

**Solution:**

- **Option 1: Modify the Placeholder**

  ```yaml
  CodeExample: |+
    Here's a Python function:

    def greet(name):
        return f"Hello, {{name}}!"
  ```

  - `{{name}}` is not a valid variable name and will be left untouched.

- **Option 2: Escape the Curly Braces**

  - Unfortunately, **YAML** does not support escaping curly braces directly, but you can change the placeholder in the code snippet to avoid variable detection.

---

## Combining Persona Data

Agents can utilize data from persona files stored in `.agentforge/personas/`. This allows you to define agent-specific information separately from your code and reuse personas across different agents.

**Example Persona File (`Botty.yaml`):**

```yaml
Name: Botty McBotFace
Description: |+
  a generic bot

Location: Dinner Table
Purpose: Pass the butter
```

**Example Prompt File (`BottyAgent.yaml`):**

```yaml
Prompts:
  System: |+
    You are {Name}, {Description}.
    Your location: {Location}.
    Your purpose: {Purpose}.
```

When you run the agent, the variables in the prompt `{Name}`, `{Description}`, `{Location}`, and `{Purpose}` are replaced with the corresponding values from the persona file.

**Usage Example:**

```python
from botty_agent import BottyAgent

agent = BottyAgent()
response = agent.run()
print(response)
```

**Rendered Prompt:**

```
You are Botty McBotFace, a generic bot.
Your location: Dinner Table.
Your purpose: Pass the butter.
```

## Important Considerations

### Variable Overlap and Precedence

- **Variable Precedence**: If a variable exists in both the persona file and is provided at runtime via the `run()` method, the **persona value will override the runtime value** for that variable.
  
- **Avoid Overlapping Variable Names**: To prevent unintended overrides, ensure that variable names in your persona files do not conflict with variable names you intend to provide at runtime unless overriding is desired.

**Example of Variable Overlap:**

Suppose you have a prompt that uses the variable `{topic}`, and both the persona file and the runtime arguments provide a value for `topic`.

**Persona File (`QuestionGeneratorAgent.yaml`):**

```yaml
Name: Question Generator
Topic: Default Topic
```

**Prompt File (`QuestionGeneratorAgent.yaml`):**

```yaml
Prompts:
  System: |+
    You are {Name}.
  Topic: |+
    The topic is: {topic}
  Instruction: Please generate an insightful question about the topic.
```

**Usage Example:**

```python
from question_generator_agent import QuestionGeneratorAgent

agent = QuestionGeneratorAgent()
response = agent.run(topic="artificial intelligence")
print(response)
```

**Rendered Prompt:**

```
You are Question Generator.

The topic is: Default Topic

Please generate an insightful question about the topic.
```

In this example:

- The `topic` variable is defined in both the persona file (`"Default Topic"`) and provided at runtime (`"artificial intelligence"`).
- The persona value `"Default Topic"` overrides the runtime value `"artificial intelligence"` in the rendered prompt.
 ---
## Best Practices for Prompt Design

- **Use Valid Variable Names**: Ensure that variables you intend to replace are valid Python identifiers.
- **Unique Variable Names**: Use unique variable names in your persona files and when passing data at runtime to avoid unintended overrides.
- **Avoid Overlapping Variable Names**: To prevent unintended overrides, ensure that variable names in your persona files do not conflict with variable names you intend to provide at runtime unless overriding is desired.
- **Avoid Unintended Variable Replacement**: Be cautious with curly braces in code snippets or response formats.
  - Modify placeholders in code to prevent them from being interpreted as variables.
- **Descriptive Sub-Prompt Names**: Use meaningful names for sub-prompts to enhance readability.
- **Consistent Formatting**: Maintain consistent indentation and formatting in your **YAML** files.
- **Testing**: Regularly test your prompts to ensure variables are correctly replaced and the agent behaves as expected.
---

## Conclusion

By leveraging persona data, you can enrich your agents with detailed backgrounds and characteristics, enhancing their interactions. Understanding how variable precedence works between persona files and runtime data is crucial to avoid unexpected behavior.

---

## Additional Resources

- **Prompt Handling Deep Dive**: For a detailed exploration of how prompts are processed, check out the [Prompt Handling Documentation](../Utils/PromptHandling.md).
- **Agents Documentation**: Learn more about creating and customizing agents in the [Agents Guide](Agents.md).
- **Personas**: Understand how to define and use personas in the [Personas Guide](../Personas/Personas.md).

---

**Need Help?**

If you have questions or need assistance, feel free to reach out:

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)

---