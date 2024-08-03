# Actions

## Overview

**Actions** within our framework are sequences of one or more tools that are executed in a specific order to perform complex tasks. They offer the capability to combine the functionality of individual tools into cohesive workflows. Actions are flexible and can consist of a single tool or multiple tools, each contributing a step towards the overall objective of the action.

Actions are also defined in YAML files and managed within the `actions` directory in the project, facilitating organized development and straightforward access.

**Actions Directory**: You can find the action definitions in the `your_project_root/.agentforge/actions` directory.

## Defining Actions in YAML

Each action is defined in a YAML file, which includes attributes that detail the steps involved:

- **Name**: The title of the action.
- **Description**: What the action does, explained clearly.
- **Example**: An example command showing how the action could be executed.
- **Instruction**: Step-by-step instructions on how the action should be carried out.
- **Tools**: A list of tools used in the action.

Here's an example of a multi-tool action defined in YAML format:

### Action Example
```yaml
Name: Write File
Description: |-
  The 'Write File' action combines directory examination and file writing operations. 
  It first reads the structure of a specified directory using the 'Read Directory' tool. 
  Then, it utilizes the 'File Writer' tool to write or append text to a specified file within that directory. 
  This action ensures you can check the directory's contents before performing file operations.
Example: |-
  # Example usage of the Write File action:
  directory_structure = read_directory('path/to/folder', max_depth=2)
  print(directory_structure)
  
  selected_file = 'path/to/folder/filename.txt'
  response = write_file(selected_file, 'This is the content', mode='a')
  print(response)
Instruction: |-
  To perform the 'Write File' action, follow these steps:
  1. Use the 'Read Directory' tool to examine the directory structure:
     - Call the `read_directory` function with the directory path and an optional `max_depth` parameter.
     - The function returns a string representing the directory structure.
  2. Review the directory structure output to identify the target directory or file where you want to write or append content.
  3. Select the target path from the directory structure.
  4. Use the 'File Writer' tool to write or append text to the selected file:
     - Call the `write_file` function with the selected file path, content, and an optional `mode` parameter ('a' for append, 'w' for overwrite).
     - The function performs the file operation and returns a response indicating the success or failure of the operation.
  5. Utilize the responses from both tools as needed for your application.
Tools:
  - Read Directory
  - File Writer
```

## Executing Actions

The `Actions` class in our framework has methods designed to select, create, and execute actions. This class orchestrates the flow from loading action-specific tools, executing these tools, to injecting the processed data into the knowledge graph. The `Actions` class also includes utility methods for formatting and parsing actions and tools.

### Action Execution Process

1. **Loading Tools**: The action's tools are loaded and prepared for execution.
2. **Running Tools in Sequence**: Each tool is executed in the order specified, with outputs from one tool being used as inputs for the next where necessary.
3. **Handling Results**: The results are collected and can be used for further processing or saved for future reference.

## Example Action Execution Code

The following example demonstrates a generic use case of executing an action within our framework using the `Actions` class.

### Usage Example

```python
from agentforge.modules.Actions import Actions

objective = 'Stay up to date with current world events'
action = Actions()
result = action.auto_execute(objective=objective)
print(f'\nAction Results: {result}')
```

## Methods in the `Actions` Class

---
### `__init__()`
Initializes the `Actions` class, setting up the logger, storage utilities, and loading necessary components for action processing. This method prepares the class for executing actions by initializing collections of actions and tools.

---
### `parse_actions(action_list)`
Parses and structures the actions fetched from storage for easier handling and processing.

**Parameters:**
- `action_list` (Dict): The list of actions to parse.

**Returns:**
- `Optional[Dict[str, Dict]]`: A dictionary of parsed actions, or `None` if an error occurs.
---
### `format_actions(action_list)`
Formats the actions into a human-readable string and stores it in the agent's data for later use.

**Parameters:**
- `action_list` (Dict): The list of actions to format.

**Returns:**
- `Optional[str]`: The formatted string of actions, or `None` if an error occurs.
---
### `initialize_collection(collection_name)`
Initializes a specified collection with preloaded data.

**Parameters:**
- `collection_name` (str): The name of the collection to initialize.

**Returns:**
- `None`
---
### `get_relevant_actions_for_objective(objective, threshold=None, num_results=1)`
Loads actions based on the current objective and specified criteria from the storage system.

**Parameters:**
- `objective` (str): The objective to find relevant actions for.
- `threshold` (Optional[float]): The threshold for relevance.
- `num_results` (int): The number of results to return.

**Returns:**
- `Union[str, Dict]`: The formatted actions or an empty dictionary if no actions are found.
---
### `get_tool_list(num_results=20)`
Retrieves the list of tools from storage.

**Parameters:**
- `num_results` (int): The number of tools to return.

**Returns:**
- `Optional[Dict[str, Union[List[str], None, List[Dict]]]]`: A dictionary containing all tool information, or `None` if there are no tools.
---
### `select_action_for_objective(objective, action_list, context=None, format_result=False)`
Selects an action for the given objective from the provided action list.

**Parameters:**
- `objective` (str): The objective to select an action for.
- `action_list` (str): The list of actions to select from.
- `context` (Optional[str]): The context for action selection.
- `format_result` (bool): Whether to format the result. Default is `False`.

**Returns:**
- `Union[str, Dict]`: The selected action or formatted result.
---
### `craft_action_for_objective(objective, context=None, format_result=False)`
Crafts a new action for the given objective.

**Parameters:**
- `objective` (str): The objective to craft an action for.
- `context` (Optional[str]): The context for action crafting.
- `format_result` (bool): Whether to format the result. Default is `False`.

**Returns:**
- `Union[str, Dict]`: The crafted action or formatted result.
---
### `load_tool_from_storage(tool)`
Loads configuration and data for a specified tool from the storage.

**Parameters:**
- `tool` (str): The name of the tool to load.

**Returns:**
- `Optional[Dict]`: The loaded tool data, or `None` if an error occurs.
---
### `parse_action_tools(action)`
Loads the tools specified in the action's configuration.

**Parameters:**
- `action` (Dict): The action containing the tools to load.

**Returns:**
- `List[Dict] | None`: A list with the loaded tools or `None`.
---
### `prime_tool(objective, action, tool, previous_results, tool_context)`
Prepares the tool for execution by running the `ToolPrimingAgent`.

**Parameters:**
- `objective` (str): The objective for tool priming.
- `action` (str): The action to prime the tool for.
- `tool` (Dict): The tool to be primed.
- `previous_results` (Optional[str]): The results from previous tool executions.
- `tool_context` (Optional[str]): The context for the tool.

**Returns:**
- `Dict`: The formatted payload for the tool.
---
### `execute_tool(tool, payload)`
Executes the tool using the dynamic tool utility with the prepared payload.

**Parameters:**
- `tool` (Dict): The tool to be executed.
- `payload` (Dict): The payload to execute the tool with.

**Returns:**
- `Union[Dict, None]`: The result of the tool execution or an error dictionary.
---
### `run_tools_in_sequence(objective, action, tools)`
Runs the specified tools in sequence for the given objective and action.

**Parameters:**
- `objective` (str): The objective for running the tools.
- `action` (Dict): The action containing the tools to run.
- `tools` (List[Dict]): The list of tools to run.

**Returns:**
- `Union[Dict, None]`: The final result of the tool execution or an error dictionary.
---
### `auto_execute(objective, context=None)`
Automatically executes the actions for the given objective and context.

**Parameters:**
- `objective` (str): The objective for the execution.
- `context` (Optional[str]): The context for the execution.

**Returns:**
- `Union[Dict, None]`: The result of the execution or an error dictionary.
---
By using the `Actions` class, developers can efficiently manage and execute complex sequences of tools, leveraging the modular and flexible nature of the framework to automate intricate workflows.