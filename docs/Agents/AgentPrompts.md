# Agent Prompts

Prompt templates lie at the core of the **AgentForge** framework, defining how agents interact with users and Large Language Models (LLMs). Written in **YAML**, these files give you fine-grained control over conversations and agent behaviors. Each agent you create—whether by instantiating it with a YAML filename or by subclassing—relies on these prompt files for instructions.

---

## Table of Contents

1. [Organizing Agent Prompt Files](#organizing-agent-prompt-files)
2. [Understanding Prompt Files](#understanding-prompt-files)
3. [Crafting Prompts with System and User Sections](#crafting-prompts-with-system-and-user-sections)
4. [Dynamic Variables in Prompts](#dynamic-variables-in-prompts)
5. [Dynamic Prompt Rendering](#dynamic-prompt-rendering-missing-variables)
6. [Handling Special Cases and Code Snippets](#handling-special-cases-and-code-snippets)
7. [Combining Persona Data](#combining-persona-data)
8. [Important Considerations](#important-considerations)
9. [Best Practices for Prompt Design](#best-practices-for-prompt-design)
10. [Example: Bringing It All Together](#example-bringing-it-all-together)
11. [Conclusion](#conclusion)
12. [Additional Resources](#additional-resources)

---

## Organizing Agent Prompt Files

When you create an agent in **AgentForge**, you can either:

1. Instantiate `Agent` directly by providing a YAML filename (like `Agent("EchoAgent")`) that corresponds to a prompt file, **or**  
2. Subclass `Agent` with the YAML filename as the class name (like `EchoAgent()`)

Either way, you need a YAML file in `.agentforge/prompts/` that lays out how your agent interacts with users and LLMs.

### Naming Convention

- **Match the `agent_name`**  
  The file’s name (e.g., `EchoAgent.yaml`) must match the agent’s `agent_name`. If you call `Agent("EchoAgent")` or `EchoAgent()`, the framework will look for `EchoAgent.yaml` in `.agentforge/prompts/` and any of its subfolder.  
- **Case Sensitivity**  
  The YAML file name is case-sensitive, and so are the keys in the file (`prompts`, `system`, `user` should be lowercase). If you call `Agent("EchoAgent")` or `EchoAgent()`, the framework will look specifically for `EchoAgent.yaml` and not `echoagent.yaml`.

### Directory Structure

You can nest your agent YAML files inside subfolders within `.agentforge/prompts/`. The system will search all subdirectories to find them.

```
.agentforge/
└── prompts/
    ├── EchoAgent.yaml
    ├── advanced_echo/
    │   └── echo_bot.yaml
    └── knowledge/
        └── knowledge_agent.yaml
```
- **Note**: Prompt template YAML files can be named however you like, though we recommend keeping them lowercase for consistency *(Unlike this example which was done for demonstration purposes)*.
---

## Understanding Prompt Files

Prompt files define the text (including placeholders) for **system** and **user** messages. These instructions guide how the agent (and the LLM it’s connected to) processes the user’s input.

### Top-Level Key: `prompts`

Each YAML file begins with a top-level key `prompts`, which contains two main sections:

1. **`system`**: Establishes context, background, or instructions for the LLM’s role.  
2. **`user`**: Represents user inputs, tasks, or questions.

An example in minimal form:

```yaml
prompts:
  system: You are an assistant that echoes the user's input.
  user: {user_input}
```

- **Lowercase Requirement**: The keys `prompts`, `system`, and `user` must be lowercase. Nested keys can be named however you like, though we recommend keeping them lowercase for consistency.

---

## Crafting Prompts with System and User Sections

Most LLM APIs expect a “system” message (for overall context) and a “user” message (for the user’s actual input). In **AgentForge**, those two concepts map directly to `system` and `user` in your `prompts` file.

### Example: Subdividing Sections

You can subdivide your `system` or `user` sections into smaller parts for clarity. Each subsection is concatenated during prompt rendering.

```yaml
prompts:
  system:
    identity: "You are EchoBot, a friendly echoing assistant."
    instructions: "Always reply by echoing back the user’s text."
  user:
    greeting: "User says: {user_input}"
```

At runtime, **AgentForge** combines `identity` and `instructions` into the final system prompt, and similarly combines everything under `user`.

---

## Dynamic Variables in Prompts

Placeholders enclosed in braces, like `{user_input}`, become variables that you can pass at runtime to the agent’s `run()` method. **AgentForge** automatically substitutes these variables when rendering the final prompt.

### Example Variables

```yaml
prompts:
  system: "You are a knowledge agent that specializes in {expertise}."
  user: "Please explain the basics of {subject}."
```

When you call:

```python
agent.run(expertise="quantum computing", subject="quantum entanglement")
```

Those placeholders get filled:

- **system** → `"You are a knowledge agent that specializes in quantum computing."`
- **user** → `"Please explain the basics of quantum entanglement."`

### Invalid Variables

Any placeholder that doesn’t match a valid Python-style identifier remains unchanged. For example, `{123abc}` or `{user input}` will not resolve as a variable and will stay exactly as written.

---

## Dynamic Prompt Rendering (Missing Variables)

In **AgentForge**, if a sub-prompt within either `system` or `user` contains variables that are not provided at runtime, that entire sub-prompt is skipped. This feature allows you to create **optional** sections in your prompt without needing multiple YAML files for slightly different scenarios.

### Why It Matters

Sometimes you want an agent to include extra context or feedback only if that information is available. If a particular variable (e.g., `{feedback}`) is missing, **AgentForge** simply omits the relevant sub-prompt, keeping the rest of the prompt intact.

### Example: Optional Feedback Sub-Prompt

Consider a scenario where an agent receives an initial question, generates a response, and then optionally includes feedback for a subsequent iteration. You can define a single YAML prompt with an extra sub-prompt that’s rendered only when the `feedback` variable is present.

```yaml
prompts:
  system:
    instructions: |
      You are a problem-solving assistant.
      Always provide a concise solution.

    feedback_section: |
      Additional Feedback from the Reviewer:
      {feedback}

  user: |
    Please solve the following problem:
    "{problem}"
```

1. **No Feedback Scenario**  
   If you run:

   ```python
   agent.run(problem="What is 2 + 2?")
   ```

   Only `instructions` and `user` render because `feedback` isn’t provided. The `feedback_section` sub-prompt, which depends on `{feedback}`, is skipped.

   **Rendered System Prompt**:
   ```
   You are a problem-solving assistant.
   Always provide a concise solution.
   ```
   **Rendered User Prompt**:
   ```
   Please solve the following problem:
   "What is 2 + 2?"
   ```

2. **With Feedback**  
   If you run:

   ```python
   agent.run(
       problem="What is 2 + 2?",
       feedback="The previous solution was incorrect. Please try again."
   )
   ```

   The `feedback_section` sub-prompt **is** rendered because `feedback` is available.

   **Rendered System Prompt**:
   ```
   You are a problem-solving assistant.
   Always provide a concise solution.

   Additional Feedback from the Reviewer:
   The previous solution was incorrect. Please try again.
   ```
   **Rendered User Prompt**:
   ```
   Please solve the following problem:
   "What is 2 + 2?"
   ```

This approach lets you handle optional context or instructions within a single prompt file. By selectively including sub-prompts when the required variables are present, you maintain a clean setup and avoid duplicating YAML files for slightly different use cases.

---

## Handling Special Cases and Code Snippets

### Escape Curly Braces

If you need literal curly braces in your text—e.g., for JSON templates—**AgentForge** treats them as variable placeholders. To avoid that, you can escape them by wrapping with `/{ ... /}`:

```yaml
prompts:
  system: |
    Example JSON template:
    {
      "message": "/{message/}",
      "time": "/{time/}"
    }
  user: "Fill in the template above."
```

The text inside `/{ ... /}` remains literal braces in the rendered prompt.

**Rendered System Prompt**:
```
Example JSON template:
{
  "message": "{message}",
  "time": "{time}"
}
```

---

## Combining Persona Data

If personas are enabled in your configuration, any data in `.agentforge/personas/<persona_name>.yaml` can be merged into your prompt. Typically, **AgentForge** will place persona fields into the runtime data so they can be used just like any other variable.

```yaml
# .agentforge/prompts/botty_agent.yaml
prompts:
  system: |
    You are {name}, {description}.
  user: "Hello! Introduce yourself."
```
```yaml
# .agentforge/personas/botty.yaml
name: Botty McBotFace
description: "a friendly bot who loves to chat"
```

When you call `Agent("botty_agent").run()`, the framework sees the matching persona file `botty.yaml` (in the personas folder) and merges those fields into the prompt.

---

## Important Considerations

1. **Agent Name ↔ YAML Filename**  
   The filename in `.agentforge/prompts/` or its nested subfolders must match the agent’s name exactly (including case).  
2. **Lowercase Keys**  
   Use `prompts`, `system`, and `user` in all-lowercase. Nested keys can be freely named, though lowercase is recommended.  
3. **Persona vs. Runtime**  
   If both a persona and a runtime argument define the same variable, the runtime argument takes precedence.

---

## Best Practices for Prompt Design

- **Keep Prompts Clear**  
  Make your `system` instructions concise but explicit.  
- **Use Consistent Formatting**  
  Stick to lowercasing your main keys and keep your sub-prompt keys easy to read.  
- **Be Mindful of Variable Names**  
  Only placeholders matching valid Python identifiers will be replaced.  
- **Test Iteratively**  
  Try your agent with sample inputs to ensure the final rendered prompts look correct.  
- **Leverage Subsections**  
  Subdivide your system and user prompts into logical subsections if it helps your logic (e.g., `identity`, `instructions`, `context`).

---

## Example: Bringing It All Together

Let’s say you have a “knowledge” agent that explains science topics.

### Prompt File: `.agentforge/prompts/knowledge_agent.yaml`

```yaml
prompts:
  system:
    identity: "You are {name}, an expert in {expertise}."
    style: "Use plain language explanations."
  user: |
    The topic is: {topic}
    Please give a concise overview.
```

### Persona File: `.agentforge/personas/knowledge_agent.yaml` (Optional)

```yaml
name: Dr. Know
expertise: Astrophysics
```

### Usage in Code

```python
from agentforge.agent import Agent

knowledge_agent = Agent("knowledge_agent")
response = knowledge_agent.run(topic="Black Holes")
print(response)
```

**Rendered Prompt**:

- **system**:  
  ```
  You are Dr. Know, an expert in Astrophysics.
  Use plain language explanations.
  ```
- **user**:  
  ```
  The topic is: Black Holes
  Please give a concise overview.
  ```

---

## Conclusion

**AgentForge** uses YAML-based prompts to define agent behavior. By splitting the prompt into `system` and `user` sections, employing dynamic variables, and optionally combining persona data, you can craft flexible and contextually aware dialogues. Just remember to keep keys lowercase at the top level, match your YAML file name to your `agent_name`, and test thoroughly.

---

## Additional Resources

- **Prompt Handling Deep Dive**: [Prompt Handling Documentation](../Utils/PromptHandling.md)  
- **Custom Agents**: [Custom Agents Guide](CustomAgents.md)  
- **Personas**: [Personas Guide](../Personas/Personas.md)  

**Need Help?**

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)  
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)
