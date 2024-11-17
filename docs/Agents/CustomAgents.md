# Custom Agents Guide

## Introduction

Creating custom agents in **AgentForge** allows you to tailor agent behaviors to your specific needs. By subclassing the `Agent` base class, you inherit default functionalities and can override methods to customize behaviors. Additionally, you can assign custom names to agents when instantiating them, enabling the same agent class to use different configurations or prompt templates. This guide will walk you through the process of creating and customizing your own agents, as well as how to organize your project for scalability.

---

## Table of Contents

1. [Creating a Basic Custom Agent](#1-creating-a-basic-custom-agent)
2. [Creating Agent Prompt Templates](#2-creating-agent-prompt-templates)
3. [Using Custom Agent Names](#3-using-custom-agent-names)
4. [Organizing Agents and Project Structure](#4-organizing-agents-and-project-structure)
5. [Using Persona Files](#5-using-persona-files)
6. [Overriding Agent Methods](#6-overriding-agent-methods)
7. [Custom Agent Example](#7-custom-agent-example)
8. [Best Practices](#8-best-practices)
9. [Next Steps](#9-next-steps)

---

# 1. Creating Agents in AgentForge

In AgentForge, you can create agents in two primary ways:

1. **By Instantiating the `Agent` Class (or subclass) with a Custom Name**: This method allows you to create agents by simply specifying a name that matches a prompt template **YAML** file, without writing any additional code.
2. **By Subclassing the `Agent` Class**: Use this method when you need to override or extend the agent's behavior through code by creating a subclass of `Agent`.

## Method 1: Instantiating the `Agent` Class with a Custom Name

This is the simplest and most direct way to create an agent. You provide a custom name when instantiating the `Agent` class, and the agent will use the prompt template **YAML** file that matches this name. No additional code is required.

### Step-by-Step Guide

**Step 1: Create the Prompt Template**

In the `.agentforge/prompts/` directory, create a **YAML** file named `HelpfulAssistant.yaml`:

```yaml
Prompts:
  System: You are a helpful assistant.
  User: |
    {user_input}
```

- The **YAML** file name must match the given `agent_name` exactly and is case-sensitive.

**Step 2: Instantiate the Agent with the Custom Name**

Create a script to run your agent (e.g., `run_agent.py`):

```python
from agentforge.agent import Agent

agent = Agent(agent_name="HelpfulAssistant")
response = agent.run(user_input="Hello, AgentForge!")
print(response)
```

- By specifying `agent_name="HelpfulAssistant"`, the agent will use the `HelpfulAssistant.yaml` prompt template.

**Step 3: Execute the Script**

Ensure your virtual environment is activated and run the script:

```bash
python run_agent.py
```

**Example Output:**

```
Hello! How can I assist you today?
```

>***Note:** The actual output depends on the LLM configuration.*

### Benefits

- **No Code Required**: Create new agents by simply providing a name that matches a prompt template.
- **Flexibility**: Easily switch between different agents by changing the `name` parameter.
- **Efficiency**: Avoids the need to create new subclasses for agents that only differ in their prompt templates.

### Using Multiple Prompt Templates with the Same Agent Class

You can create multiple prompt templates and use them with the same `Agent` class by changing the `name` parameter.

**Example:**

Create another prompt template named `FriendlyBot.yaml`:

```yaml
Prompts:
  System: You are a friendly chatbot named {bot_name}.
  User: |
    {user_input}
```

Use it in your script:

```python
from agentforge.agent import Agent

agent = Agent(name="FriendlyBot")
response = agent.run(user_input="What's the weather today?", bot_name="WeatherBot")
print(response)
```

---

## Method 2: Subclassing the `Agent` Class to Override Behavior

When you need to customize the agent's behavior by overriding methods or adding new functionality, you should create a subclass of the `Agent` class.

### Step-by-Step Guide

**Step 1: Define Your Agent Subclass**

Create a Python file for your agent (e.g., `my_custom_agent.py`):

```python
from agentforge.agent import Agent

class MyCustomAgent(Agent):
    def process_data(self):
        # Custom data processing logic
        pass

    def build_output(self):
        # Custom output construction
        pass
```

- The `agent_name` defaults to the class name (`MyCustomAgent`) if no `name` is provided during initialization.
- Override methods to customize the agent's behavior.

**Step 2: Create the Prompt Template**

Create a **YAML** file named `MyCustomAgent.yaml` in the `.agentforge/prompts/` directory:

```yaml
Prompts:
  System: You are a specialized assistant.
  User: |
    {user_input}
```

**Step 3: Use Your Custom Agent**

Create a script to run your agent (e.g., `run_my_custom_agent.py`):

```python
from my_custom_agent import MyCustomAgent

agent = MyCustomAgent()
response = agent.run(user_input="Tell me about AI.")
print(response)
```

Since `MyCustomAgent` inherits from the base `Agent` class, you can still provide a custom `name` when initializing it. This allows you to point to a different prompt template, combining the benefits of both methods. By specifying a custom `name`, you can use the overridden methods in your subclass while also utilizing different prompt templates without creating additional subclasses.

```python
from my_custom_agent import MyCustomAgent

# Instantiate with a custom name to use a different prompt template
agent = MyCustomAgent(name="SpecializedAssistant")
response = agent.run(user_input="Tell me about AI.")
print(response)
```

In this example, `MyCustomAgent` will use the prompt template file `SpecializedAssistant.yaml` instead of `MyCustomAgent.yaml`. This approach allows you to:

- **Customize Behavior**: Override methods in your subclass to change or extend functionality.
- **Flexible Prompt Templates**: Specify different prompt templates by providing a custom `name` during initialization.
- **Reuse Code**: Avoid duplicating code by not creating additional subclasses for each new prompt template.

This means you can have a single subclass with custom behavior and easily switch between different prompt templates as needed.

**Step 4: Execute the Script**

```bash
python run_my_custom_agent.py
```

### When to Use Subclassing

- **Custom Behavior**: When you need to override or extend the agent's functionality by modifying methods.
- **Complex Logic**: For agents requiring additional processing, data handling, or integration with other systems.
- **Code Reuse**: When building a hierarchy of agents with shared behaviors.

### Nested Subclassing Example

You can create nested subclasses to build upon existing behaviors.

```python
class ParentAgent(Agent):
    def process_data(self):
        # Parent processing logic
        pass

class ChildAgent(ParentAgent):
    def process_data(self):
        super().process_data()
        # Additional child processing logic
        pass

class GrandchildAgent(ChildAgent):
    def process_data(self):
        super().process_data()
        # Additional grandchild processing logic
        pass
```

---

## Summary of Agent Creation Methods

### Choosing the Right Method

- **Instantiating with a Custom Name**: Use this method when you want to create agents that differ only in their prompt templates. It's ideal when no code changes are needed.
- **Subclassing the `Agent` Class**: Use this method when you need to change or extend the agent's behavior through code by overriding methods.

### Key Points

- The agent name is determined by the `agent_name` parameter when instantiating the agent. If `agent_name` is not provided, it defaults to the class name.
- The prompt template **YAML** file must match the `agent_name` parameter.
- Avoid creating subclasses solely to use different prompt templates; instead, instantiate the `Agent` class with a custom name.
- Subclassing should be reserved for when you need to override or add methods to change the agent's behavior.

---

## 4. Organizing Agents and Project Structure

Proper organization of your agent prompt templates and Python scripts is crucial for **AgentForge** to function correctly.

### Directory Structure

- **Agent Prompt Templates**:
  - Stored in the `.agentforge/prompts/` directory.
  - You can organize prompt templates into subdirectories within this directory.
  - **AgentForge** automatically discovers all prompt **YAML** files within `.agentforge/prompts/` and its subdirectories.

### Agent Python Scripts

- **Location**: Python scripts (the files containing your agent classes) can be located anywhere within your project's root directory or its subdirectories.
- **Naming Convention**:
  - The **class name** of your agent does not have to match the prompt template file name if you specify a custom `agent_name` when instantiating the agent.
  - If no `agent_name` is provided,  it defaults to the class name, and the prompt template file must match the class name.

### Example Structure

```
your_project/
│
├── .agentforge/
│   └── prompts/
│       ├── MyCustomAgent.yaml
│       ├── CustomAgentName.yaml
│       └── subdirectory/
│           └── AnotherAgent.yaml
├── custom_agents/
│   └── my_custom_agent.py
├── another_agent.py
└── run_agents.py
```

### Running Scripts

- It is recommended to run your main script (the one that imports and runs your agents) from the project's root directory to avoid path issues.

---

## 5. Using Persona Files

Personas provide additional context and information to agents. They are defined in **YAML** files within the `.agentforge/personas/` directory.

### Creating a Persona File

**Example Persona File (`MyCustomAgent.yaml`)**:

```yaml
Name: Expert Assistant
Specialty: artificial intelligence
Background: You have a Ph.D. in computer science and specialize in AI.
```

- **Variables**: `Name`, `Specialty`, and `Background` can be referenced in your prompts.

### Linking Persona to Agent

In your agent's prompt file (`MyCustomAgent.yaml`), reference the persona:

```yaml
Prompts:
  System: |
    You are {Name}, specializing in {Specialty}.
    {Background}
  User: |
    {user_input}

Persona: MyCustomAgent
```

- The agent will replace `{Name}`, `{Specialty}`, and `{Background}` with values from the persona file.

**Note**: If no persona file is specified, the system will default to using the `default.yaml` persona file unless personas are disabled in the system settings.

---

## 6. Overriding Agent Methods

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
from agentforge.agent import Agent

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
    def run(self, **kwargs):
        # Initial Logic
        super().run(**kwargs)
        # Additional processing
```

---

## 7. Custom Agent Example

Let's create a custom agent that summarizes a given text and allows for different summarization styles by using custom agent names.

### Step 1: Define the Custom Agent

```python
from agentforge.agent import Agent
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

### Step 2: Create Different Prompt Templates

**General Summary (`SummarizeAgent.yaml`):**

```yaml
Prompts:
  System: You are an assistant that summarizes text concisely.
  User: |
    Please provide a brief summary of the following text in JSON format with the key "summary":

    {text}
```

**Detailed Summary (`DetailedSummarizer.yaml`):**

```yaml
Prompts:
  System: You are an assistant that provides detailed summaries.
  User: |
    Provide an in-depth summary of the following text, highlighting key points and insights. Return the summary in JSON format with the key "summary":

    {text}
```

### Step 3: Run the Agent with Different Names

```python
# run_summarize_agent.py
from summarize_agent import SummarizeAgent

text_to_summarize = """
AgentForge is a powerful framework that allows developers to create agents that interact with Large Language Models in a flexible and customizable way. It simplifies the process of building, managing, and deploying AI agents.
"""

# Using the general summarizer
agent = SummarizeAgent()
response = agent.run(text=text_to_summarize)
print("General Summary:")
print(response)

# Using a detailed summarizer by specifying a custom agent name
detailed_agent = SummarizeAgent(name="DetailedSummarizer")
detailed_response = detailed_agent.run(text=text_to_summarize)
print("\nDetailed Summary:")
print(detailed_response)
```

### Output

Assuming the LLM returns appropriate responses:

```
General Summary:
Summary:
AgentForge simplifies the creation and deployment of AI agents by providing a flexible framework for interacting with Large Language Models.

Detailed Summary:
Summary:
AgentForge is a comprehensive framework designed to assist developers in building, managing, and deploying AI agents. It offers flexibility and customization, streamlining the interaction with Large Language Models and simplifying complex AI development processes.
```

---

## 8. Best Practices

- **Consistent Naming**: Ensure your `agent_name`, class name, and **YAML** prompt file names match appropriately.
  - If you provide a custom `agent_name`, make sure the prompt template file matches this name.
- **Use Valid Variable Names**: Variables in prompts and personas should be valid Python identifiers.
- **Avoid Name Conflicts**: Be cautious of variable names overlapping between personas and runtime data.
- **Test Incrementally**: Test your agent after each change to identify issues early.
- **Leverage Custom Names**: Use the `name` parameter to create flexible agents without redundant subclasses.
- **Document Your Agent**: Keep notes on custom behaviors and overridden methods for future reference.

---

## 9. Next Steps

- **Explore Agent Methods**: Dive deeper into customizing agents by reading the [Agent Methods Guide](AgentMethods.md).
- **Learn About Prompts**: Enhance your prompts by reviewing the [Agent Prompts Guide](AgentPrompts.md).
- **Utilize Utilities**: Understand utility functions in the [Utilities Overview](../Utils/UtilsOverview.md).

---

### **Conclusion**

By following this guide, you can create custom agents tailored to your specific needs. The **AgentForge** framework provides the flexibility to build simple or complex agents, leveraging the power of LLMs with ease. Utilizing the ability to specify custom agent names enhances flexibility and reduces the need for multiple subclasses.

---

**Need Help?**

If you have questions or need assistance, feel free to reach out:

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)

---