# Tool Priming Agent

## Introduction

`ToolPrimingAgent` is a specialized agent that extends the base `Agent` class. This agent is specifically designed for priming tools based on a defined action.

Each agent, including the `ToolPrimingAgent`, is associated with a specific prompt `YAML` file which determines its interactions. This file contains a set of pre-defined prompts templates that guide the agent's behavior during its execution. For a detailed understanding of how these prompts are structured and utilized, you can refer to our [Prompts Documentation](../../Agents/AgentPrompts.md). To view the specific prompts associated with the `ToolPrimingAgent`, see its [YAML File](../../../src/agentforge/setup_files/agents/ModuleAgents/ToolPrimingAgent.yaml).

---

## Class Definition

```python
from agentforge.agent import Agent


class ToolPrimingAgent(Agent):
    pass
```

The `ToolPrimingAgent` is an agent that inherits its core functionalities from the base `Agent` class. This allows it to utilize the foundational features and methods provided by the `Agent` class as it does not require any custom methods to perform its task.

---

## How to Use

### Running the Agent

To utilize the `ToolPrimingAgent`, you first need to initialize it. You can then invoke it to perform its specific tasks by calling the `run` method. This method requires certain parameters:

- `objective`: The core objective that the tool needs to achieve.
- `action`: The specific action selected to achieve the objective.
- `tool_name`: The name of the tool that needs to be primed.
- `tool_info`: Instructions explaining how to use the tool.
- `path`: Working directories relevant to the task. - `(optional)`
- `previous_results`: Contains the results returned by the previous execution of the same or different tool. - `(optional)`
- `tool_context`: Context and sequence of tools within the action. - `(optional)`

The `previous_results` parameter is particularly versatile. In the context of an action sequence, it holds the results from the previous tool execution, whether that's from the same tool or a different one. If this agent is priming the first tool in a sequence, or if the action consists of a single tool, `previous_results` can be set to `None`.

Here's how you would call the agent:

```python
from agentforge.agents.ToolPrimingAgent import ToolPrimingAgent

tool_priming_agent = ToolPrimingAgent()

payload = tool_priming_agent.run(objective=objective,
                                 action=action,
                                 tool_name=tool.get('Name'),
                                 tool_info=formatted_tool,
                                 path=work_paths,
                                 previous_results=previous_results,
                                 tool_context=tool_context)
```

In this example, the `ToolPrimingAgent` receives an objective, action, tool name, tool information, working paths, previous tool results, and tool context. It will then return a `payload` which contains the tool in its primed state ready to be executed.

> **Note**: For a more detailed explanation on how we use actions to string tools together in a sequence, please refer to our [Actions Documentation](../../ToolsAndActions/Overview.md)

---

## Prompts

The `ToolPrimingAgent` utilizes a set of predefined prompts to guide its behavior. These prompts are structured as follows:

```yaml
Prompts:
  System: |-
    You are a tool priming agent tasked with preparing a tool for the following core objective:
    {objective}
    
    To achieve this objective, the following action has been selected:
    ```
    {action}
    ```

  Tool: |+
    Your task is to prime the '{tool_name}' tool in the context of the selected action. Instructions explaining how to use the tool are as follows:
    
    {tool_info}

  Path: |+
    Your working directories are: 
    
    {path}

  Results: |+
    Use the following data from the previous tool result in order to prime the '{tool_name}' tool:
    
    {previous_results}

  Context: |+
    Consider the following context and the sequence of tools within the action:
    
    {tool_context}

  Instruction: |+
    Review the sequence of tools and understand how each tool feeds into the next to accomplish the overall objective. You must prime the '{tool_name}' tool using the data from the previous tool results if any and the provided context if given.
    
    Prime the tool to prepare it for execution, ensuring that it correctly receives and processes the input from the previous tool in the sequence. Do not attempt to achieve the objective directly; focus on priming the tool as a step toward the overarching goal.
    
    If there is a next tool in the sequence, provide the necessary context for the next tool to understand how it should be primed and used based on the results of the current tool.
    
    You must prime the '{tool_name}' tool using ONLY the YAML RESPONSE FORMAT provided below.
    
    RESPONSE FORMAT:
    ```yaml
    args:
      for each argument name: <argument value>
    thoughts:
      reasoning: <your reasoning>
      speak: <any feedback for the user>
      next_tool_context: <context for the next tool, if applicable>
    ```
```

The agent uses these prompts to systematically prepare the tool for its intended action within the overall sequence.