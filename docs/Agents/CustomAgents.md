# Custom Agents Guide

## Introduction

Creating custom agents in **AgentForge** allows you to tailor agent behaviors to your specific needs. By subclassing the `Agent` base class, you inherit default functionalities and can override methods to customize behaviors. This guide will walk you through the process of creating and customizing your own agents.

---

## Table of Contents

1. [Creating a Basic Custom Agent](#1-creating-a-basic-custom-agent)
2. [Creating Agent Prompt Templates](#2-creating-agent-prompt-templates)
3. [Using Persona Files](#3-using-persona-files)
4. [Overriding Agent Methods](#4-overriding-agent-methods)
5. [Best Practices](#5-best-practices)
6. [Next Steps](#6-next-steps)

---

## 1. Creating a Basic Custom Agent

To create a custom agent, you simply need to define a new Python class that inherits from the `Agent` base class.

### Step-by-Step Guide

**Step 1: Define Your Agent Class**

Create a Python file for your agent (e.g., `my_custom_agent.py`):

```python
from agentforge.agent import Agent

class MyCustomAgent(Agent):
    pass  # The agent_name is automatically set to 'MyCustomAgent'
```

- By default, `MyCustomAgent` inherits all methods from `Agent`.

**Step 2: Create the Prompt Template**

In the `.agentforge/agents/` directory, create a YAML file named `MyCustomAgent.yaml`:

```yaml
Prompts:
  System: You are a helpful assistant.
  User: |+
    {user_input}
```

- The **YAML** file name must exactly match the class name (`MyCustomAgent`) and is case-sensitive.

**Step 3: Use Your Custom Agent**

Create a script to run your agent (e.g., `run_my_custom_agent.py`):

```python
from my_custom_agent import MyCustomAgent

agent = MyCustomAgent()
response = agent.run(user_input="Hello, AgentForge!")
print(response)
```

**Step 4: Execute the Script**

Ensure your virtual environment is activated and run the script:

```bash
python run_my_custom_agent.py
```

**Example Output:**

```
Hello! How can I assist you today?
```

*Note: The actual output depends on the LLM configuration.*

---

## 2. Creating Agent Prompt Templates

Prompt templates define how your agent interacts with users and the LLM. They are stored in **YAML** files within the `.agentforge/agents/` directory.

### Naming Convention

- The **YAML** file name must match the agent class name exactly (case-sensitive).
- For `MyCustomAgent`, the prompt file is `MyCustomAgent.yaml`.

### Example Prompt Template

```yaml
Prompts:
  System: You are a knowledgeable assistant specializing in {specialty}.
  User: |+
    {user_input}
```

- **Variables**: `{specialty}` and `{user_input}` are placeholders that will be replaced at runtime.
- **Sub-Prompts**: `System` and `User` are sub-prompts that structure the conversation.

---

## 3. Using Persona Files

Personas provide additional context and information to agents. They are defined in YAML files within the `.agentforge/personas/` directory.

### Creating a Persona File

**Example Persona File (`MyCustomAgent.yaml`):**

```yaml
Name: Expert Assistant
Specialty: artificial intelligence
Background: |+
  You have a Ph.D. in computer science and specialize in AI.
```

- **Variables**: `Name`, `Specialty`, and `Background` can be referenced in your prompts.

### Linking Persona to Agent

In your agent's prompt file (`MyCustomAgent.yaml`), reference the persona:

```yaml
Prompts:
  System: |+
    You are {Name}, specializing in {Specialty}.
    {Background}
  User: |+
    {user_input}
```

- The agent will replace `{Name}`, `{Specialty}`, and `{Background}` with values from the persona file.

**Note:** Ensure that the persona file name matches the agent class name unless specified otherwise in the agent configuration.

---

## 4. Overriding Agent Methods

To customize agent behavior, you can override methods inherited from the `Agent` base class.

### Common Methods to Override

- **`load_from_storage()`**
- **`load_additional_data()`**
- **`process_data()`**
- **`parse_result()`**
- **`save_to_storage()`**
- **`build_output()`**

### Example: Overriding Methods

```python
from agentforge import Agent

class MyCustomAgent(Agent):

    def process_data(self):
        # Custom data processing
        self.data['user_input'] = self.data['user_input'].lower()

    def build_output(self):
        # Custom output formatting
        self.output = f"Response: {self.result}"
```

- **Calling Base Methods**: Use `super()` to retain base class functionality.

```python
    def run(self):
        # Initial Logic
        super().run()
        # Additional processing
```

---

## 5. Putting It All Together: Custom Agent Example

Let's create a custom agent that summarizes a given text and returns the summary.

### Step 1: Define the Custom Agent

```python
from agentforge import Agent
import json

class SummarizeAgent(Agent):
    def parse_result(self):
        # Parse the LLM's response as JSON
        try:
            self.data['parsed_result'] = json.loads(self.result)
        except json.JSONDecodeError:
            self.data['parsed_result'] = {'summary': self.result}

    def build_output(self):
        summary = self.data['parsed_result'].get('summary', 'No summary found.')
        self.output = f"Summary:\n{summary}"
```

### Step 2: Create the Prompt Template (`SummarizeAgent.yaml`)

```yaml
Prompts:
  System: You are an assistant that summarizes text.
  User: |+
    Please summarize the following text and return the summary in JSON format with the key "summary":

    {text}
```

### Step 3: Run the Agent

```python
# run_summarize_agent.py
from summarize_agent import SummarizeAgent

agent = SummarizeAgent()
text_to_summarize = """
AgentForge is a powerful framework that allows developers to create agents that interact with Large Language Models in a flexible and customizable way. It simplifies the process of building, managing, and deploying AI agents.
"""

response = agent.run(text=text_to_summarize)
print(response)
```

### Output

Assuming the LLM returns a response in JSON format:

```
Summary:
AgentForge simplifies building and deploying AI agents by providing a flexible framework for interacting with Large Language Models.
```

---

## 6. Best Practices

- **Consistent Naming**: Ensure your class name, **YAML** prompt file, and persona file names match exactly.
- **Use Valid Variable Names**: Variables in prompts and personas should be valid Python identifiers.
- **Avoid Name Conflicts**: Be cautious of variable names overlapping between personas and runtime data.
- **Test Incrementally**: Test your agent after each change to identify issues early.
- **Leverage Personas**: Use personas to enrich your agent with background information and context.
- **Document Your Agent**: Keep notes on custom behaviors and overridden methods for future reference.

---

## 7. Next Steps

- **Explore Agent Methods**: Dive deeper into customizing agents by reading the [Agent Methods Guide](AgentMethods.md).
- **Learn About Prompts**: Enhance your prompts by reviewing the [Agent Prompts Guide](AgentPrompts.md).
- **Utilize Utilities**: Understand utility functions in the [Utilities Overview](../Utils/UtilsOverview.md).

---

### **Conclusion**

By following this guide, you can create custom agents tailored to your specific needs. The **AgentForge** framework provides the flexibility to build simple or complex agents, leveraging the power of LLMs with ease.

---

**Need Help?**

If you have questions or need assistance, feel free to reach out:

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)

---

