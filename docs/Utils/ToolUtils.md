# Tool Utils Documentation

## Overview

`ToolUtils` in **AgentForge** is a utility class that manages the execution of tools defined within the system. It offers functions to dynamically load and execute tools from specified Python modules, streamlining the automation process.

## Key Methods and Examples

### dynamic_tool

Dynamically executes a tool based on its module path and provided arguments.

#### Usage Example:

```python
tool_utils = ToolUtils()
payload = {
  "command": "tool_function_name",
  "args": {
    "arg1": value1,
    "arg2": value2
  }
}
result = tool_utils.dynamic_tool("path.to.tool_module", payload)
# Executes the specified tool and returns the result
```

### show_primed_tool

Displays formatted information about a tool, its arguments, and reasoning, aiding in debugging and understanding tool operations.

#### Usage Example:

```python
tool_utils = ToolUtils()
tool_name = "SampleTool"
payload = {
  "thoughts": {
    "speak": "Running SampleTool",
    "reasoning": "To achieve X"
  },
  "args": {
    "arg1": value1,
    "arg2": value2
  }
}
tool_utils.show_primed_tool(tool_name, payload)
# Outputs formatted information about the SampleTool
```

## How ToolUtils Works

- **Dynamic Module Import**: Using `importlib`, `ToolUtils` dynamically imports the Python module specified for a tool.
- **Command Execution**: The specific command (function or method) within the tool is executed with the arguments provided in the payload.
- **Result Handling**: The output or result of the tool's execution is returned and can be utilized in subsequent processes or for reporting.

## Practical Application

`ToolUtils` is particularly useful for automating tasks using a variety of tools. Its dynamic nature allows for flexibility and adaptability, enabling the system to incorporate new tools or modify existing ones with minimal changes to the overall framework.

## Note

- **Module and Script Name Consistency**: Ensure that the module name specified in the payload matches exactly with the Python script name containing the tool.
- **Flexibility**: `ToolUtils` can handle both standalone functions and class methods within a tool module, offering versatility in tool implementation.

---

For a usage and integration example of `ToolUtils` with other components in the **AgentForge** framework,
refer to the [Action Execution Documentation,](../Modules/ActionExecution.md) and it's respective [code](../../src/agentforge/modules/ActionExecution.py).

---