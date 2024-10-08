# ToolUtils Utility Guide

## Introduction

The `ToolUtils` class in **AgentForge** is a utility for dynamically managing and executing tools within the system. It allows agents to load and run tools at runtime, facilitating flexibility and extensibility in performing various tasks.

---

## Overview

`ToolUtils` provides methods to:

- **Dynamically Execute Tools**: Load and execute functions or methods from specified modules dynamically.
- **Format Items**: Convert tools or actions into human-readable strings for display or logging.

---

## Class Definition

```python
class ToolUtils:
    def __init__(self):
        self.logger = Logger(name=self.__class__.__name__)
        self.storage = ChromaUtils('default')
    
    # Method definitions...
```

---

## Key Methods

### 1. `dynamic_tool(self, tool: Dict[str, str], payload: Dict[str, Any]) -> Dict[str, Any]`

**Purpose**: Dynamically loads a tool module and executes a specified command within it, using arguments provided in the payload.

**Parameters**:

- `tool` (dict): A dictionary containing information about the tool to be executed, typically with keys like `'Script'` and `'Command'`.
- `payload` (dict): Contains the `'args'` for the command execution.

**Returns**:

- `dict`: A dictionary with the execution result or an error message.

**Example Usage**:

```python
from agentforge.utils.ToolUtils import ToolUtils

tool_utils = ToolUtils()

# Define the tool and payload
tool = {
    'Script': 'tools.my_tool',    # Module path to the tool
    'Command': 'execute'          # Function or method to call
}

payload = {
    'args': {
        'param1': 'value1',
        'param2': 'value2'
    }
}

# Execute the tool
result = tool_utils.dynamic_tool(tool, payload)

if result['status'] == 'success':
    print("Tool executed successfully:", result['data'])
else:
    print("Tool execution failed:", result['message'])
```

---

### 2. `_execute_tool(self, tool_module: str, tool_class: str, command: str, args: Dict[str, Any]) -> Any`

**Purpose**: Executes the specified command within the tool module.

**Parameters**:

- `tool_module` (str): The module path to the tool (e.g., `'tools.my_tool'`).
- `tool_class` (str): The class name within the module (if applicable).
- `command` (str): The command (function or method) to execute.
- `args` (dict): Arguments to pass to the command.

**Note**: This is an internal method used by `dynamic_tool`. Typically, you won't call this method directly.

---

### 3. `_handle_error(self, e: Exception, tool_module: str, tool_class: str, command: str) -> Dict[str, Any]`

**Purpose**: Handles errors that occur during tool execution, logging them and preparing an error response.

**Parameters**:

- `e` (Exception): The exception that was raised.
- `tool_module` (str): The module path to the tool.
- `tool_class` (str): The class name within the module.
- `command` (str): The command that was attempted.

**Note**: This is an internal method used by `dynamic_tool` to handle exceptions.

---

### 4. `format_item(self, item: Dict[str, Union[str, List[str]]], order: Optional[List[str]] = None) -> str`

**Purpose**: Formats an item (such as a tool or action) into a human-readable string.

**Parameters**:

- `item` (dict): The item to format.
- `order` (list, optional): The order in which to display the item's keys.

**Returns**:

- `str`: The formatted string.

**Example Usage**:

```python
item = {
    'Name': 'SampleTool',
    'Description': 'A tool for demonstration purposes.',
    'Parameters': ['param1', 'param2']
}

formatted_item = tool_utils.format_item(item)
print(formatted_item)
```

**Output**:

```
Name: SampleTool
Description: A tool for demonstration purposes.
Parameters:
- param1
- param2
```

---

### 5. `format_item_list(self, items: Dict, order: Optional[List[str]] = None) -> Optional[str]`

**Purpose**: Formats a list of items into a human-readable string, useful for displaying multiple tools or actions.

**Parameters**:

- `items` (dict): A dictionary of items to format.
- `order` (list, optional): The order in which to display the keys of each item.

**Returns**:

- `str` or `None`: The formatted string of items, or `None` if an error occurs.

**Example Usage**:

```python
items = {
    'Tool1': {
        'Name': 'SampleTool1',
        'Description': 'First sample tool.'
    },
    'Tool2': {
        'Name': 'SampleTool2',
        'Description': 'Second sample tool.'
    }
}

formatted_items = tool_utils.format_item_list(items)
print(formatted_items)
```

**Output**:

```
---
Name: SampleTool1
Description: First sample tool.
---
Name: SampleTool2
Description: Second sample tool.
---
```

---

## Practical Application

### Dynamically Executing Tools

The `dynamic_tool` method allows agents to execute tools whose modules and commands are specified at runtime. This is particularly useful when agents need to perform actions that are determined dynamically based on user input or other factors.

**Example in Agent Context**:

```python
class MyAgent(Agent):
    def perform_action(self):
        tool = {
            'Script': 'tools.my_tool',
            'Command': 'execute'
        }
        payload = {
            'args': {
                'param1': 'value1',
                'param2': 'value2'
            }
        }
        result = self.tool_utils.dynamic_tool(tool, payload)
        if result['status'] == 'success':
            self.logger.log("Tool executed successfully.", level='info')
        else:
            self.logger.log(f"Tool execution failed: {result['message']}", level='error')
```

---

## Best Practices

- **Ensure Correct Module Paths**: When specifying the `Script` in the tool dictionary, make sure the module path is correct and accessible.
- **Handle Errors Gracefully**: Always check the `status` of the result returned by `dynamic_tool` and handle failures appropriately.
- **Secure Tool Execution**: Be cautious when executing tools dynamically to avoid running untrusted code. Validate inputs and control accessible modules.

---

## Conclusion

The `ToolUtils` utility in **AgentForge** empowers developers to extend agent capabilities dynamically. By leveraging its methods, you can create agents that adapt to various tasks and integrate new functionalities seamlessly.

---

**Need Help?**

If you have questions or need assistance, feel free to reach out:

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)

---