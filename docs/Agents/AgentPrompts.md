# Agent Prompts Documentation

---

## Introduction

In the realm of the AgentForge framework, the agent's behavior and interaction are governed by prompts. These prompts serve as a foundation to guide the agent through tasks, ensuring it understands its objectives and can relay information effectively.

---

## Location and Organization of Agent Prompts

All agent prompts are housed within the `.agentforge/agents` folder, which serves as the root directory for these configurations. This centralized structure ensures that the system can effortlessly access and manage the prompts.

For organizational purposes, prompts can be nested inside additional subfolders within the `agents` root folder. This nesting allows for better categorization and management of agent prompts, especially when dealing with a multitude of agents. Regardless of how deep the nesting goes, the system is designed to automatically search for and locate any `YAML` files in the root `agents` folder as well as in its nested subfolders.

**Example Structure**:
```
agents/
│
├── Agent1.yaml
│
├── category1/
│   ├── Agent2.yaml
│   └── Agent3.yaml
│
└── category2/
    ├── subcategory1/
    │   └── Agent4.yaml
    │
    └── Agent5.yaml
```

This structure offers flexibility in organizing agent prompts while ensuring that they remain easily accessible to the system.

---

## How Prompts Work

Every agent in the system is accompanied by a dedicated `YAML` file that dictates its prompt templates. These templates are written in a straightforward manner, using curly braces `{}` to encapsulate variables that need to be dynamically replaced during execution.

For instance, a prompt might look like this:
```
You are a tool priming agent who's been asked to prepare a tool for the following task:

{current_task}
```
Here, `{current_task}` is a placeholder variable, which will be replaced by actual data when the prompt is rendered.

---

## Dynamic Variable Detection

AgentForge brings to the table a seamless variable detection mechanism through its `PromptHandling` class. This savvy class ensures that only strings enclosed within `{}` and conforming to valid Python variable naming conventions are interpreted as variables. Any other occurrence of curly braces, even in intricate structures like JSON, is left undisturbed.

So, if you have prompts with JSON structures or other textual content within curly braces that you don't want interpreted as variables, you're in safe hands. The system discerns between them smartly.

### **Important Note:** 
When designing prompts, always ensure that variables enclosed in curly braces, such as `{current_task}` or `{feedback}`, align with the data you plan to provide to the agent. Only strings adhering to Python's variable naming conventions will be detected as variables. Anything else will be treated as regular text, ensuring it won't be substituted with data.

### Example:

Here's a simple demonstration of how the dynamic variable detection works:

```python
from agentforge.agent import Agent as NewAgent

feedback = "This is feedback"
# The agent's run method is invoked with feedback as an argument. 
# If the agent's prompt has a {feedback} variable, it will be replaced with the provided feedback string.
response = NewAgent().run(feedback=feedback)
```
---

## Crafting Dynamic Prompts: The Power of Sub-Prompts

The AgentForge framework introduces a unique and powerful approach to crafting prompts, making use of 'sub-prompts'. Instead of relying on a fixed, hardcoded set of prompts, the system adopts a dynamic stance, ensuring flexibility and adaptability.


### **The Mechanics of Sub-Prompts**

A typical prompt `YAML` file is structured into various sections, each representing a different subprompt. The beauty of these sub-prompts lies in their optionality and adaptability:

1. **Optionality**: Each sub-prompt is treated as optional. Its rendering depends on the presence of its required variables. If a necessary variable is absent, the sub-prompt won't be rendered, allowing for dynamic adaptability based on available data.

2. **Default Text**: If a sub-prompt contains no variables (i.e., it's static text), it will always be rendered as-is. This ensures flexibility in crafting prompts that have a mix of dynamic and static sections.

### **Common Sub Prompts**

While the prompts can be tailored for specific needs, there are common sub-prompts that frequently appear across various agents:

- **System**: Typically outlines the core objective or task of the agent.
  
- **Summary**: Provides a brief recap or summary of previous actions or events.
  
- **Context**: Offers critique or feedback from previous actions, guiding the agent's subsequent moves.
  
... (and so on for other prompts)

Each of these sub-prompts has its own unique purpose and is rendered based on the data available. By decoupling the sub-prompts from a fixed structure, the AgentForge framework ensures a level of dynamism and adaptability previously unseen, allowing for on-the-fly edits without needing system restarts.

>**Note:** While the name of a sub-prompt can technically be any valid Python variable name, its actual name doesn't influence functionality. Still, choosing a descriptive and relevant name can be a game-changer, offering invaluable context to anyone crafting or modifying the prompt.

---

## Deep Dive into Prompt Handling

For those interested in understanding the intricate workings of how prompts handle dynamic variables, how they're rendered, and the magic behind the `PromptHandling` class, check out our dedicated [**Prompt Handling Documentation**](PromptHandling.md).

---
