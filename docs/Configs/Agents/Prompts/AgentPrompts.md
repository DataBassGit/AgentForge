# Agent Prompts Documentation

---

## Introduction

In the realm of the AgentForge framework, the agent's behavior and interaction are governed by prompts. These prompts serve as a foundation to guide the agent through tasks, ensuring it understands its objectives and can relay information effectively.

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

The AgentForge framework now boasts a dynamic variable detection mechanism, courtesy of the `PromptHandling` class. This class ensures that only valid Python variable names enclosed within `{}` are treated as variables. Any other usage of curly braces, especially in nested structures like JSON, remains unaffected.

This means that if your prompt contains JSON structures or other text within curly braces that shouldn't be treated as variables, there's no need to worry; the system will handle it smartly.

>**Important Note:** When crafting prompts, it's essential to ensure that any variable wrapped in curly braces—like `{current_task}` or `{feedback}`—matches the data you're feeding to the agent. Remember, only valid Python variable names pass muster. Anything that doesn't conform to Python's variable naming rules won't be recognized by the system, and thus, won't be replaced with the intended data.

---

## Crafting Dynamic Prompts: The Power of Sub-Prompts

The AgentForge framework introduces a unique and powerful approach to crafting prompts, making use of 'sub-prompts'. Instead of relying on a fixed, hardcoded set of prompts, the system adopts a dynamic stance, ensuring flexibility and adaptability.


### **The Mechanics of Sub-Prompts**

A typical prompt `YAML` file is structured into various sections, each representing a different subprompt. The beauty of these sub-prompts lies in their optionality and adaptability:

1. **Optionality**: Each subprompt is treated as optional. Its rendering depends on the presence of its required variables. If a necessary variable is absent, the sub-prompt won't be rendered, allowing for dynamic adaptability based on available data.

2. **Default Text**: If a subprompt contains no variables (i.e., it's static text), it will always be rendered as-is. This ensures flexibility in crafting prompts that have a mix of dynamic and static sections.

### **Common Sub Prompts**

While the prompts can be tailored for specific needs, there are common sub-prompts that frequently appear across various agents:

- **System**: Typically outlines the core objective or task of the agent.
  
- **Summary**: Provides a brief recap or summary of previous actions or events.
  
- **Context**: Offers critique or feedback from previous actions, guiding the agent's subsequent moves.
  
... (and so on for other prompts)

Each of these sub-prompts has its own unique purpose and is rendered based on the data available. By decoupling the sub-prompts from a fixed structure, the AgentForge framework ensures a level of dynamism and adaptability previously unseen, allowing for on-the-fly edits without needing system restarts.

---

## Deep Dive into Prompt Handling

For those interested in understanding the intricate workings of how prompts handle dynamic variables, how they're rendered, and the magic behind the `PromptHandling` class, check out our dedicated [**Prompt Handling Documentation**](PromptHandling.md).

---
