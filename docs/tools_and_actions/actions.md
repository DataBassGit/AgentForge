# Actions

Actions are the legacy workflow layer built on top of AgentForge tools. An action is a YAML definition under `.agentforge/actions/` that describes a task and the tools used to perform it.

Actions use model calls to select, prepare, and sequence tools. Use them only with trusted project-owned action and tool definitions.

## Action YAML

Each action YAML file describes the workflow at a high level:

- **Name**: Human-readable action name.
- **Description**: What the action does.
- **Example**: Example usage or expected behavior.
- **Instruction**: Steps the model should follow.
- **Tools**: Tool names used by the action.

Example:

```yaml
Name: Write File
Description: |
  Reads a directory structure and writes content to a selected file.
Instruction: |
  1. Use the Read Directory tool to inspect the target folder.
  2. Choose the file or folder to write to.
  3. Use the File Writer tool with the selected path and text.
Tools:
  - Read Directory
  - File Writer
```

## `Actions` Class

The `Actions` class in `agentforge.modules.actions` loads action and tool definitions into storage, searches for relevant items, primes tools, and runs tool sequences.

Typical setup:

```python
from agentforge.modules.actions import Actions
from agentforge.storage.chroma_storage import ChromaStorage

storage = ChromaStorage.get_or_create(storage_id="project_tools")
actions = Actions(chroma_instance=storage)
```

## Core Methods

- **`initialize_collection(collection_name)`**: Load action or tool definitions into storage.
- **`auto_execute(objective, context=None, threshold=0.8)`**: Select and run an action for an objective.
- **`get_relevant_actions_for_objective(objective, threshold=0.8, num_results=1)`**: Search for relevant actions.
- **`select_action_for_objective(objective, action_list, context=None)`**: Choose an action from candidate definitions.
- **`craft_action_for_objective(objective, tool_list, context=None)`**: Generate an action definition from available tools.
- **`prime_tool_for_action(objective, action, tool, previous_results=None, tool_context=None)`**: Produce a payload for a tool call.
- **`run_tools_in_sequence(objective, action)`**: Prime and execute the tools listed in an action.

## Example

```python
from agentforge.modules.actions import Actions
from agentforge.storage.chroma_storage import ChromaStorage

storage = ChromaStorage.get_or_create(storage_id="project_tools")
actions = Actions(chroma_instance=storage)

actions.initialize_collection("actions")
actions.initialize_collection("tools")

result = actions.auto_execute(
    objective="Summarize a trusted local text file",
    context="Use only tools defined by this project.",
)
```

## Safety Notes

Actions can cause AgentForge to dynamically select and execute Python tools. Keep action definitions and tool definitions in source control, review their import paths and allowed arguments, and do not expose this surface to untrusted model-generated module names, paths, or commands.

## Related Documentation

- [Tools](tools.md)
- [ToolUtils](../utils/tool_utils.md)
