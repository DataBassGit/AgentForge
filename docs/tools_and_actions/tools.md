# Tools

Tools are the legacy Python execution units used by AgentForge's dynamic tool surface. A tool definition is a YAML file under `.agentforge/tools/` that describes a trusted Python function or class method.

Tool execution dynamically imports Python modules and calls the configured command. Only use this surface with project-owned code and reviewed YAML definitions.

## Tool YAML

Each tool YAML file describes how AgentForge should present and execute the tool:

- **Name**: Human-readable tool name.
- **Args**: Arguments the command accepts.
- **Command**: Function or method name to call.
- **Description**: What the tool does.
- **Instruction**: How an agent should prepare and use the tool.
- **Example**: Example usage or expected call shape.
- **Script**: Import path for the Python module.
- **Class**: Optional class name when the command is a method.

Example:

```yaml
Name: Brave Search
Args:
  - query (str)
  - count (int, optional)
Command: search
Description: |
  Performs a Brave Search API query and returns search results.
Instruction: |
  Call the `search` method with a query string and optional result count.
Example: |
  brave_search = BraveSearch()
  results = brave_search.search(query="AgentForge", count=5)
Script: agentforge.tools.brave_search
Class: BraveSearch
```

Built-in tool definitions are scaffolded into `.agentforge/tools/` when you run:

```shell
python -m agentforge.init_agentforge
```

The corresponding Python implementations live under `agentforge.tools`.

## Dynamic Execution

Use `ToolUtils.dynamic_tool()` to execute a configured tool:

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

The result is a dictionary with `status` set to `success` or `failure`. Successful calls include returned data; failures include an error message and traceback.

## Custom Tools

Project-owned custom tools can live in any importable Python module. Put the YAML definition in `.agentforge/tools/` and set `Script`, `Class`, and `Command` to the import path and callable you want AgentForge to execute.

Keep tool definitions specific and reviewable. Avoid exposing broad filesystem, network, shell, or import behavior through model-selected tool calls.

## Related Documentation

- [Actions](actions.md)
- [ToolUtils](../utils/tool_utils.md)
