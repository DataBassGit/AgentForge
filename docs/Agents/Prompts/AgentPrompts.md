# Agent Prompts Documentation

---

## Overview

Each agent in the system possesses its own dedicated `JSON` file, guiding its prompt templates. These files reside under the `/.agentforge/agents/` directory. Crucially, the `JSON` file's name should directly align with the agent's class name and is case-sensitive. For instance, a class named `ExecutionAgent` would have its prompt configurations stored in `ExecutionAgent.json`.

---

## `Prompts` Attribute

The `Prompts` attribute encapsulates all the prompt templates available for an agent to utilize.

### **System Prompt**

The `System` attribute within `Prompts` is a mandatory inclusion. It defines the foundational behavior and primary purpose of the agent. Without this attribute, the agent won't operate. 

Example:
```json
"System": {
  "vars": [
    "objective"
  ],
  "template": "You are an AI who performs one task based on the following objective: {objective}\n\n"
}
```

---

### **Optional Prompts**

Prompts aside from the `System` prompt are deemed optional. However, their optionality doesn't just stem from the ability of users to omit them. Instead, it's because each prompt template encompasses two aspects: 

1. **The actual template**.
2. **A `vars` attribute**, which houses the variables essential for rendering the template.

If a template lacks a required variable or encounters an empty variable, the agent won't render that particular template. Instead, it'll try rendering the subsequent template.

Example:
```json
"Summary": {
  "vars": [
    "summary"
  ],
  "template": "Take into account this summary of your previous actions:\n\n{summary}\n\n---\n\n"
}
```

>**Note**: The content of the variable at the time of rendering will be directly placed within the template. For instance, if the `objective` for the agent is `Build a web scraping script`, the rendered prompt, when passed to the agent, will be: `You are an AI who performs one task based on the following objective: Build a web scraping script\n\n`.

---

## Complete Prompt Example: `ExecutionAgent.json`

```json
{
  "Prompts": {
    "System": {
      "vars": [
        "objective"
      ],
      "template": "You are an AI who performs one task based on the following objective: {objective}\n\n"
    },
    "Summary": {
      "vars": [
        "summary"
      ],
      "template": "Take into account this summary of your previous actions:\n\n{summary}\n\n---\n\n"
    },
    "Context": {
      "vars": [
        "context"
      ],
      "template": "Take into consideration the following critique from the last action taken:\n\n{context}\n\n---\n\n"
    },
    "Feedback": {
      "vars": [
        "feedback"
      ],
      "template": "Take into consideration the following feedback from the user:\n\n{feedback}\n\n---\n\n"
    },
    "Instruction": {
      "vars": [
        "task"
      ],
      "template": "Please complete the following task: {task}\n\nResponse: {{your response}}"
    }
  }
}
```

Remember to always ensure that the JSON file is correctly formatted and that the required variables for each prompt template are present to guarantee the agent's smooth operation.

---