# ToolUtils Utility Guide

`ToolUtils` supports AgentForge's legacy dynamic tool execution surface. Use it only with trusted project-owned modules and tool definitions.

## Overview

`ToolUtils` dynamically imports a configured Python module, optionally instantiates a class, calls the requested command, and returns a structured success or failure dictionary. It also formats tool and action definitions into readable text for prompts or diagnostics.

## Construction

```python
from agentforge.utils.tool_utils import ToolUtils

tool_utils = ToolUtils()
```

The utility creates an AgentForge logger and uses `ChromaStorage.get_or_create(storage_id="tool_library")` for tool-library storage.

## `dynamic_tool`

```python
result = tool_utils.dynamic_tool(tool, payload)
```

`tool` is a dictionary with these execution fields:

- `Script`: Import path for the module.
- `Class`: Optional class name to instantiate.
- `Command`: Function or method name to call.

`payload` contains `args`, a dictionary of keyword arguments for the command. It may also contain `command`, which overrides the command from the tool definition.

Example:

```python
from agentforge.utils.tool_utils import ToolUtils

tool_utils = ToolUtils()
tool = {
    "Script": "agentforge.tools.brave_search",
    "Class": "BraveSearch",
    "Command": "search",
}
payload = {
    "args": {
        "query": "AgentForge",
        "count": 5,
    }
}

result = tool_utils.dynamic_tool(tool, payload)
```

Successful calls return:

```python
{"status": "success", "data": result}
```

Failures return:

```python
{"status": "failure", "message": error_message, "traceback": traceback_text}
```

## Formatting Helpers

- `format_item(item, order=None)`: Format one tool or action dictionary.
- `format_item_list(items, order=None)`: Format multiple definitions with separators.

These helpers are useful when building prompts that include available tool or action definitions.

## Safety Notes

Dynamic execution imports and calls Python code based on configuration. Keep tool definitions in source control, review the import paths and allowed commands, and never allow untrusted users or raw model output to supply arbitrary `Script`, `Class`, `Command`, or argument values.

## Related Documentation

- [Tools](../tools_and_actions/tools.md)
- [Actions](../tools_and_actions/actions.md)
