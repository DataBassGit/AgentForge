# Persona File (default.json)

## Overview

The `default.json` is a crucial configuration file that sets the behavior of agents in the system. It defines the objective, tasks, and other settings for each agent type.

---

## Structure

The file is a JSON structure with the following keys:

### `Name`

The name of the persona, in this case, "AF".

### `Objective`

The main goal that the agent is trying to achieve. For example: "Write a program design for my business in applied behavioral analysis, and identify a task analysis process."

### `Tasks`

An array of tasks that outline what needs to be done to achieve the objective. Each task is a string detailing a specific action.

---

## Example Snippet

```json
{
    "Name": "AF",
    "Objective": "Write a program design for my business in applied behavioral analysis...",
    "Tasks": [
        "Identify programming languages and frameworks...",
        "Design a development environment..."
    ],
```

---

### `Memories`

A collection of key-value pairs where each key represents a memory entity and the corresponding value contains its attributes. These memories could be anything from tasks, tools, or other data that the agent needs to remember. In other words any memory defined in this key will be created for the agent.

Example:

```json
{
    "Memories": {
        "Tasks" : "",
        "Results": "",
        "Tools": "",
        "Actions": ""
    }
}
```

---

### `Defaults`

This section provides default settings that can be applied to any agent unless explicitly overridden. It contains the following sub-keys:

#### `API`

The API used for the LLM (Language Logic Model). For example: `"claude_api"`.

#### `Model`

Specifies the LLM model to be used. For example: `"claude"`.

#### `Params`

A dictionary of parameters that control the behavior of the LLM. These parameters depend on the API being used so for a deeper breakdown of the parameters please refer to the documentation for the API being used:

#### Example:

```json
"Defaults": {
    "API": "claude_api",
    "Model": "claude",
    "Params": {
        "max_new_tokens": 2000,
        "temperature": 0.5,
        // ... (other params)
    }
}
```

---

### `SubAgent Prompts`

Let's use the Execution Agent as an example. The `ExecutionAgent` key defines the behavior of a specific SubAgent. Notice that it had its own `Prompts` and `type` fields. 

#### `Prompts`

A dictionary containing various types of prompts (`System`, `Summary`, `Context`, `Feedback`, `Instruction`) that the agent uses. Each prompt type has its own `vars` and `template`:

- `vars`: A list of variables to include in the prompt.
- `template`: The string template for the prompt, containing placeholders for the variables.

**IMPORTANT:** The `System` prompt is required for all SubAgents, all other prompts are optional.

#### `type`

Defines the type of the agent, in this case, `"agent"`.

#### Example:

```json
"ExecutionAgent": {
    "Prompts": {
        "System": {
            "vars": ["objective"],
            "template": "You are an AI who performs one task based on the following objective: {objective}\\n\\n"
        },
        // ... (other prompts)
    },
    "type": "agent"
}
```

---

## How to Use

Place this file in the `.agentforge/` directory and make sure it's named `default.json`.
