# ⚠️ DEPRECATION WARNING

**The Tools system is DEPRECATED.**

Do NOT use in production or with untrusted input. This system will be replaced in a future version with a secure implementation based on the MCP standard.

See: https://github.com/DataBassGit/AgentForge/issues/116 for details.

# ToolUtils Utility Guide

In **AgentForge**, the `ToolUtils` class provides a mechanism for dynamically loading and executing tool modules, along with formatting these tools for logging or user display. This allows agents to expand or modify their capabilities at runtime by referencing tools in external or user-defined modules.

---

## Overview

**Key Responsibilities**:

1. **Dynamic Tool Execution**  
   - Load a Python module based on a string path (e.g., `"tools.my_tool"`).  
   - Optionally instantiate a class or directly call a function within that module.  
   - Pass arguments at runtime.

2. **Error Handling**  
   - Catches and logs exceptions with helpful messages.  
   - Returns structured responses, including success/failure and optional traceback.

3. **Formatting**  
   - Convert tool/action definitions into human-readable text.  
   - Format a dictionary of items (e.g., multiple tools) for easy display.

Most developers won't need to modify `ToolUtils` directly if they're just defining new tools; references to the utility typically occur inside advanced agent code that decides which tool to execute on the fly.

---

## Class Definition

```python
class ToolUtils:
    """
    A utility class for dynamically interacting with tools. It supports importing tool modules,
    executing specified commands within those modules, and formatting tool data for display.
    """

    def __init__(self):
        self.logger = Logger(name=self.__class__.__name__)
        self.storage = ChromaStorage('default')
    
    # See below for method descriptions...
```

**Attributes**:

- **`logger`**: A **AgentForge** `Logger` instance for capturing logs about tool usage or errors.  
- **`storage`**: A `ChromaStorage` object for advanced memory usage, if needed (e.g., storing tool results).

---

## Key Methods

### 1. `dynamic_tool(tool: Dict[str, str], payload: Dict[str, Any]) -> Dict[str, Any]`

**Purpose**  
Dynamically loads a specified tool and executes a command within it, passing arguments from `payload`.

**Parameters**  
- **`tool`** (`dict`): Typically includes keys like `Script` (a module path) and `Command` (the function or method to call), plus an optional `Class`.  
- **`payload`** (`dict`): Contains `'args'` to be passed to the tool's command.

**Returns**  
- A dictionary with either `{'status': 'success', 'data': <result>}` or `{'status': 'failure', 'message': <error>, 'traceback': <trace>}`.

**Usage Example**:
```python
from agentforge.utils.functions.tool_utils import ToolUtils

tool_utils = ToolUtils()

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
result = tool_utils.dynamic_tool(tool, payload)

if result['status'] == 'success':
    print("Execution success:", result['data'])
else:
    print("Execution failed:", result['message'])
```

---

### 2. `_execute_tool(tool_module: str, tool_class: str, command: str, args: Dict[str, Any]) -> Any`

**Purpose**  
Internally called by `dynamic_tool` to handle the actual import and call. It:

1. Checks if `tool_module` is a built-in function (if it matches `BUILTIN_FUNCTIONS` keys).  
2. Otherwise imports the module, optionally instantiates a class, and calls the specified `command`.

**Note**  
This method is not typically invoked directly. If you need to modify the import or instantiation logic, you'd override or alter this method.

---

### 3. `_handle_error(e: Exception, tool_module: str, tool_class: str, command: str) -> Dict[str, Any]`

**Purpose**  
Catches exceptions from `_execute_tool` or `dynamic_tool`, logs them, and returns a structured error response.

**Response Structure**  
- **`status`**: `"failure"`  
- **`message`**: A string describing the error or missing command/class.  
- **`traceback`**: The formatted Python traceback.

---

### 4. `format_item(item: Dict[str, Union[str, List[str]]], order: Optional[List[str]] = None) -> str`

**Purpose**  
Creates a user-friendly string representation of a single tool or action dictionary. If the dictionary has lists, they're converted to bullet points. If it has multi-line strings, they're displayed with extra spacing.

**Example**:
```python
tool_info = {
  'Name': 'SampleTool',
  'Description': 'Demonstrates usage',
  'Parameters': ['param1', 'param2']
}
formatted = tool_utils.format_item(tool_info)
print(formatted)
# Output:
# Name: SampleTool
# Description: Demonstrates usage
# Parameters:
# - param1
# - param2
```

---

### 5. `format_item_list(items: Dict, order: Optional[List[str]] = None) -> Optional[str]`

**Purpose**  
Formats multiple items (for instance, multiple tool definitions) by calling `format_item` on each and joining them with `---` as a separator.

**Example**:
```python
tools = {
  'ToolA': {'Name': 'ToolA', 'Description': 'The first tool'},
  'ToolB': {'Name': 'ToolB', 'Description': 'The second tool'}
}

formatted_tools = tool_utils.format_item_list(tools)
print(formatted_tools)
# ---
# Name: ToolA
# Description: The first tool.
# ---
# Name: ToolB
# Description: The second tool.
# ---
```

---

## Practical Usage: Dynamic Execution in an Agent

Here's a more complete example of how an agent might dynamically call a tool:

```python
from agentforge.agent import Agent

class DynamicToolAgent(Agent):
    def execute_dynamic_action(self):
        tool_info = {
            'Script': 'tools.my_custom_tool',
            'Class': 'MyCustomTool',   # optional
            'Command': 'run_action'
        }
        payload = {'args': {'key1': 'value1'}}
        result = self.tool_utils.dynamic_tool(tool_info, payload)

        if result['status'] == 'success':
            self.logger.info(f"Tool ran with data: {result['data']}")
        else:
            self.logger.error(f"Tool failed: {result['message']}")
```

**Flow**  
1. `execute_dynamic_action` defines the tool's `Script` (a module path) and the `Command`.  
2. `dynamic_tool` imports and executes the tool function/class with `args = {'key1': 'value1'}`.  
3. Logs results or errors accordingly.

---

## Best Practices

1. **Valid Module Paths**  
   Ensure the `'Script'` path (like `'tools.my_custom_tool'`) is a valid, importable module.  
2. **Security**  
   Be mindful of letting user input define module paths or commands. Only allow references to safe or sandboxed code.  
3. **Error Checking**  
   Always check the returned `status`. If it's `"failure"`, investigate `message` and `traceback`.  
4. **Use Logging**  
   `tool_utils.logger` helps trace usage and debug issues.  
5. **Formatting**  
   If you want to list out many tools or actions, use `format_item_list` to produce neat text output.

---

## Conclusion

**AgentForge**'s `ToolUtils` streamlines the process of dynamically importing modules, running their commands, and formatting tool definitions for display or logging. For agent developers seeking to create flexible, pluggable functionalities—such as custom domain tools or user-defined scripts—this utility is essential.

**Need Help?**

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)  
- **Discord**: [Join our Discord Server](https://discord.gg/ttpXHUtCW6)
