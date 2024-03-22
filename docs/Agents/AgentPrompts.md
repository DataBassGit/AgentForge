# Agent Prompts Guide

## Overview

The engine that drives our AI-based agents are the prompts created for them. Prompts are specific dialog structures, defined in YAML format, that guide the agent's interactions with users.

---

## Location and Organization of Agent Prompts

Each agent needs a corresponding YAML prompt file nested somewhere within the `agents` directory.
You can find this directory at `your_project_root/.agentforge/agents`

The naming convention is crucial here. The YAML file must match the name of the Agent class defined in your code. For instance, if you've created a custom agent as below:

```python
from agentforge import Agent

class ExampleAgent(Agent):
    # ... class code ...
```

Then there should be a corresponding prompt YAML file called `ExampleAgent.yaml` within the `.agentforge/agents` directory or one of its subdirectories.

For organizational purposes, prompts files can be nested inside additional sub-folders within the `agents` root folder. This nesting allows for better categorization and management of agent prompts, especially when dealing with a multitude of agents. Regardless of how deep the nesting goes, the system is designed to automatically search for and locate any `YAML` files in the root `agents` folder as well as in its nested sub-folders.

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

## How Prompt Files Work

Every agent in the system needs to be accompanied by a dedicated `YAML` file that contains its prompt templates. These templates are written in a straightforward manner, using curly braces `{}` to encapsulate variables that need to be dynamically injected during execution.

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

>**Important Note:** 
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

The AgentForge framework introduces a seamless and powerful approach to crafting prompts, making use of "sub-prompts". Instead of relying on a fixed, hardcoded set of prompts, the system adopts a dynamic stance, ensuring flexibility and adaptability.


### **The Mechanics of Sub-Prompts**

A typical prompt `YAML` file is structured into various sections, each representing a different sub-prompt. The beauty of these sub-prompts lies in their optionality and adaptability:

1. **Optionality**: Each sub-prompt is treated as optional. Its rendering depends on the presence of its required variables. If a necessary variable is absent, the sub-prompt won't be rendered, allowing for dynamic adaptability based on available data.

2. **Default Text**: If a sub-prompt contains no variables (i.e., it's static text), it will always be rendered as-is. This ensures flexibility in crafting prompts that have a mix of dynamic and static sections.

>**Note:** While the name of a sub-prompt can technically be any valid Python variable name, its actual name doesn't influence functionality. Still, choosing a descriptive and relevant name can be a game-changer, offering invaluable context to anyone crafting or modifying the prompt.

### Prompt File Example (`ActionPrimingAgent.yaml`):

```yaml
Prompts:
  System: |+
    You are a tool priming agent who's been asked to prepare a tool for the following task:
    
    ```
    {task}
    ```
    
    The task outlined above has been curated to achieve the following core objective: 
    
    ```
    {objective}
    ```

  Tool: |+
    Instructions breaking down the tool you are required to prime are as follows:
    
    ```
    {tool}
    ```

  Path: |+
    Your working directories are: 
    
    ```
    {path}
    ```

  Results: |+
    Use the following data in order to prime the tool outlined above:
    
    ```
    {results}
    ```

  Context: |+
    Take into consideration the following critique from the last action taken:
    
    ```
    {context}
    ```

  Instruction: |+
    Your job requires you to prime the tool you've been provided by taking into consideration the context you've been given.
    
    You must prime the above given tool using ONLY the YAML RESPONSE FORMAT provided below.
    
    IMPORTANT!!!: DO NOT PROVIDE ANY COMMENTARY OUTSIDE OF THE RESPONSE FORMAT REQUESTED!!!
    
    RESPONSE FORMAT:
    ```yaml
    args:
      for each argument name: <argument value>
    thoughts:
      reasoning: <your reasoning>
      speak: <any feedback for the user>
    ```
```

In this case, `System`, `Tool`, `Path`, `Results`, `Context`, and `Instruction` are considered agent **Sub-Prompts**. The sub-prompts will be rendered only when all the required information is available to the agent. For example, the `System` sub-prompt will only be rendered when both the "task" and "objective" information are available to inject. 

Similarly, the `Tool`, `Path`, `Results`, and `Context` sub-prompts require the corresponding information to be available either in the agent's persona file or be expressly provided when calling the agent, unless derived by the agent's internal logic. If any piece of information is missing, that sub-prompt won't be rendered. The `Instruction` sub-prompt is an exception to this rule. It doesn't need any specific information to be available and, hence, will always be rendered.

---

## Conclusion

The power of this system lies in its dynamism and flexibility. By using variable placeholders inside Sub-Prompts, the system can adapt the conversation flow based on the provided persona file or information available. This dynamic rendering of prompts allows for rich, context-aware interactions that are tailored to the agent's knowledge at any given moment.

At the same time, the system also accommodates static prompts that don't require any particular set of information to render, like the `Instruction` sub-prompt in the above example. This enables you to provide constant elements or instructions in the prompt, irrespective of other variables.

In a nutshell, this combination of dynamic and static prompts gives you a powerful and flexible tool in creating  agents that can both adapt to changing contexts and maintain a stable set of interactions.

## Deep Dive into Prompt Handling

For those interested in understanding the intricate workings of how prompts handle dynamic variables, how they're rendered, and the magic behind the `PromptHandling` class, check out our dedicated [**Prompt Handling Documentation**](../Utils/PromptHandling.md).

---
