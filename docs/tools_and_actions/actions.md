# ⚠️ DEPRECATION WARNING

**The Actions system is DEPRECATED.**

Do NOT use in production or with untrusted input. This system will be replaced in a future version with a secure implementation based on the MCP standard.

See: https://github.com/DataBassGit/AgentForge/issues/116 for details.

# Actions

## Overview

The **Actions** class provides a comprehensive suite of methods for managing and executing **actions** within the framework. It is designed to offer flexibility and modularity, allowing developers to create custom solutions or use generic examples. **Actions** within this framework are sequences of steps executed in a specified order to perform complex tasks. They combine the functionality of individual components into cohesive workflows.

**Actions** are defined in **YAML** files and managed within the `actions` directory in the project, facilitating organized development and straightforward access.

**Actions Directory**: You can find the action definitions in the `your_project_root/.agentforge/actions` directory.

## Defining Actions in YAML

Each action is defined in a **YAML** file, which includes attributes detailing the steps involved:

- **Name**: The title of the action.
- **Description**: A clear explanation of what the action does.
- **Example**: An example command showing how the action could be executed.
- **Instruction**: Step-by-step instructions on how the action should be carried out.
- **Tools**: A list of tools used in the action.

### Action Example

```yaml
Name: Write File
Description: |
  The 'Write File' action combines directory examination and file writing operations. 
  It first reads the structure of a specified directory using the 'Read Directory' tool. 
  Then, it utilizes the 'File Writer' tool to write or append text to a specified file within that directory. 
  This action ensures you can check the directory's contents before performing file operations.
Example: |
  # Example usage of the Write File action:
  directory_structure = read_directory('path/to/folder', max_depth=2)
  print(directory_structure)
  
  selected_file = 'path/to/folder/filename.txt'
  response = write_file(selected_file, 'This is the content', mode='a')
  print(response)
Instruction: |
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

---

## Class Overview

The **Actions** class consists of several methods that work together to manage and execute complex workflows. Below is a brief overview of the key methods provided by the class:

- **Initialization**
  - **[`__init__`](#__init__-method)**: Sets up the **Actions** class, initializing essential components such as logging, storage, and agents used for action processing.

- **Collection Management**
  - **[`initialize_collection`](#initialize_collection-method)**: Loads and initializes a specified collection (e.g., **Actions** or **Tools**) into the vector database, enabling efficient search and retrieval.

- **Automatic Action Execution**
  - **[`auto_execute`](#auto_execute-method)**: Provides a straightforward example of how to use the other methods in the class to select or craft an appropriate action and execute it based on a given objective. This method is not intended as a comprehensive or final solution but rather as a starting point. Developers are encouraged to build and customize their own workflows using the more granular methods provided by the class.

- **Action Retrieval and Selection**
  - **[`get_relevant_actions_for_objective`](#get_relevant_actions_for_objective-method)**: Searches the database for actions relevant to a specific objective, filtering results based on a relevance threshold.
  - **[`select_action_for_objective`](#select_action_for_objective-method)**: Chooses the most suitable action from a list of possible actions for a given objective, optionally considering additional context.

- **Action Creation**
  - **[`craft_action_for_objective`](#craft_action_for_objective-method)**: Creates a new action tailored to an objective, using a specified list of tools. This is useful when no existing actions fully meet the objective.

- **Tool Priming and Sequence Execution**
  - **[`prime_tool_for_action`](#prime_tool_for_action-method)**: Prepares a tool for execution by customizing it according to the current action and objective, ensuring that each tool is used optimally in the workflow.
  - **[`run_tools_in_sequence`](#run_tools_in_sequence-method)**: Executes a series of tools in a defined sequence, where each tool builds upon the output of the previous one. This method is central to completing complex tasks that require multiple steps.

>**Important Note:** Most of these methods utilize one or more large language model (LLM) agents to function. Therefore, the underlying model must be capable of handling the cognitive load required to respond accurately and effectively. Ensure that your model is sufficiently robust to support the operations described in this class.

---

### **Understanding `action_info_order` and `tool_info_order` Parameters**

Several methods in the **Actions** class, such as [`prime_tool_for_action`](#prime_tool_for_action-method) and [`run_tools_in_sequence`](#run_tools_in_sequence-method), use the `action_info_order` and `tool_info_order` parameters. These parameters are lists that define the order of attributes from the action or tool YAML files to be included in the agent prompt during execution.

For example, you might specify the `action_info_order` as:

```python
action_info_order = ["Name", "Description"]
```

And the `tool_info_order` as:

```python
tool_info_order = ["Name", "Description", "Args", "Instruction", "Example"]
```

When these orders are applied, the following is rendered for the action:

```text
Name: Write File
Description:
  The 'Write File' action combines directory examination and file writing operations. 
  It first reads the structure of a specified directory using the 'Read Directory' tool. 
  Then, it utilizes the 'File Writer' tool to write or append text to a specified file within that directory. 
  This action ensures you can check the directory's contents before performing file operations.
```

And the following is rendered for a tool:

```
Name: File Writer
Description:
  The File Writer tool writes the provided text to a specified file within a given folder.
  It ensures the target folder exists or creates it if it doesn't.
  Key features:
  - Writes content to files in specified folders
  - Creates folders if they don't exist
  - Supports both write ('w') and append ('a') modes
  - Provides detailed error messages and success confirmations
  - Generates a preview of the written content
  
Args:
  - folder (str)
  - file (str)
  - text (str)
  - mode (str, optional)
  
Instruction:
  To use the File Writer tool, follow these steps:
  1. Import the WriteFile class from agentforge.tools.WriteFile
  2. Create an instance of the WriteFile class
  3. Call the `write_file` method with the following arguments:
     - folder: A string representing the path to the folder where the file should be written
     - file: A string representing the name of the file to write to
     - text: A string containing the content to write to the file
     - mode: (Optional) A string specifying the write mode ('w' for write, 'a' for append). Defaults to 'a'
  4. The method will return a message indicating the result of the operation, including a preview of the written content
  5. Handle any potential errors or exceptions that may be raised during the process
  
Example:
  # Example usage of the File Writer tool:
  from agentforge.tools.WriteFile import WriteFile

  writer = WriteFile()
  
  # Example with all arguments
  result = writer.write_file(folder='/path/to/folder', file='example.txt', text='Hello, World!', mode='a')
  print(result)

  # Example with default mode (append)
  result = writer.write_file(folder='/path/to/folder', file='example.txt', text='Appended text')
  print(result)
```

These parameters allow developers to control the information included in the prompts, 
ensuring that only the necessary details are provided to the agents.

---

## Detailed Methods

### **`__init__` Method**

Initializes the **Actions** class, setting up logging, storage utilities, and loading necessary components for action processing.

- **Parameters:** None
- **Returns:** None

**Example:**

```python
from agentforge.modules.actions import Actions

actions = Actions()
```

---

### **`initialize_collection` Method**

Initializes a specified collection in the vector database with preloaded data.

- **Parameters:**
  - `collection_name` (str): The name of the collection to initialize.
- **Returns:** None

**Example:**

```python
from agentforge.modules.actions import Actions

actions = Actions()
actions.initialize_collection('actions')
actions.initialize_collection('tools')
```

---

### **`auto_execute` Method**

Automatically executes actions for the given objective and context.

- **Parameters:**
  - `objective` (str): The objective for the execution.
  - `context` (Optional[str]): The context for the execution.
  - `threshold` (Optional[float]): The threshold for action relevance (default is 0.8).
- **Returns:** Union[Dict, str, None]: The result of the execution or an error dictionary.

**Example:**

```python
from agentforge.modules.actions import Actions

objective = 'Stay up to date with current world events'

actions = Actions()
result = actions.auto_execute(objective)
```

**Expected Output:**

```python
result = 'Here are the most recent events ...'
```

---

### **`get_relevant_actions_for_objective` Method**

Loads actions based on the current objective and specified criteria.

- **Parameters:**
  - `objective` (str): The objective to find relevant actions for.
  - `threshold` (Optional[float]): The threshold for action relevance.
  - `num_results` (int): The number of results to return (default is 1).
  - `parse_result` (bool): Whether to parse the result (default is True).
- **Returns:** Dict: The parsed actions or an empty dictionary if no actions are found.

**Example:**

```python
from agentforge.modules.actions import Actions

objective = 'Stay up to date with current world events'

actions = Actions()
actions_list = actions.get_relevant_actions_for_objective(objective=objective, threshold=0.9, num_results=5)
```

**Expected Output:**

```python
action_list = {
  "Web Search": {
    "Description": "The 'Web Search' action combines a Google search, web scraping, and text chunking operations...",
    "Example": "# Example usage of the Web Search action:\nquery = \"OpenAI GPT-4\"\n...",
    "Instruction": "To perform the 'Web Search' action, follow these steps:\n1. Use the 'Google Search' tool...",
    "Name": "Web Search",
    "Tools": "Google Search, Web Scrape, Intelligent Chunk",
  },
  "Write File": {
    "Description": "The 'Write File' action combines directory examination and file writing operations...",
    "Example": "# Example usage of the Write File action:\ndirectory_structure = read_directory('path/to/folder'...",
    "Instruction": "To perform the 'Write File' action, follow these steps:\n1. Use the 'Read Directory' tool...",
    "Name": "Write File",
    "Tools": "Read Directory, File Writer",
  },
}
```

---

### **`select_action_for_objective` Method**

Selects an action for the given objective from the provided action list.

- **Parameters:**
  - `objective` (str): The objective to select an action for.
  - `action_list` (Union[str, Dict]): The list of actions to select from. If given a Dict, the method will automatically attempt to convert it into a string.
  - `context` (Optional[str]): The context for action selection.
  - `parse_result` (bool): Whether to parse the result (default is True).

- **Returns:** Union[str, Dict]: The selected action or formatted result.

**Example:**

```python
from agentforge.modules.actions import Actions

objective = 'Stay up to date with current world events'
context = 'Focus on technology'

action_list = {
    "Web Search": {
        "Description": "The 'Web Search' action combines a Google search, web scraping, and text chunking operations...",
        "Example": "# Example usage of the Web Search action:\nquery = \"OpenAI GPT-4\"\n...",
        "Instruction": "To perform the 'Web Search' action, follow these steps:\n1. Use the 'Google Search' tool...",
        "Name": "Web Search",
        "Tools": "Google Search, Web Scrape, Intelligent Chunk",
    },
    "Write File": {
        "Description": "The 'Write File' action combines directory examination and file writing operations...",
        "Example": "# Example usage of the Write File action:\ndirectory_structure = read_directory('path/to/folder'...",
        "Instruction": "To perform the 'Write File' action, follow these steps:\n1. Use the 'Read Directory' tool...",
        "Name": "Write File",
        "Tools": "Read Directory, File Writer",
    },
}

actions = Actions()
selected_action = actions.select_action_for_objective(objective=objective, action_list=action_list, context=context)
```

**Expected Output when `parse_result` is `True`:**

```python
selected_action = {
    "action": "Web Search",
    "reasoning": "The objective is to 'Stay up to date with current world events'. Performing a web search can help achieve this by retrieving relevant and timely information. The provided actions are not explicitly tailored to this goal, but the 'Web Search' action comes closest in terms of functionality. It allows for a Google search, which can be used to find news articles or updates on global issues. Although it's not a perfect match, I recommend using the 'Web Search' action as it offers the most relevant capabilities to address the objective.",
}
```

---

### **`craft_action_for_objective` Method**

Crafts a new action for the given objective.

- **Parameters:**
  - `objective` (str): The objective to craft an action for.
  - `tool_list` (Union[str, Dict]): The list of tools to be used. Will convert to a string for the agent prompt if given a Dict.
  - `context` (Optional[str]): The context for action crafting.
  - `parse_result` (bool): Whether to parse the result (default is True).
  - `info_order` (Optional[List[str]]): Tool information to include in the formatted tool list.

- **Returns:** Union[str, Dict]: The crafted action or formatted result.

**Example:**

```python
from agentforge.modules.actions import Actions

objective = 'Automate file backup'
tool_list = {
    "File Writer": {
        "Args": "folder (str), file (str), text (str), mode (str='a')",
        "Command": "write_file",
        "Description": "The 'File Writer' tool writes the provided text to a specified file within ...",
        "Example": "write_file(folder='/path/to/folder', file='example.txt', text='Hello, World!', mode='a') ...",
        "Instruction": "To use the 'File Writer' tool, follow these steps:\n1. Call the `write_file` function ...",
        "Name": "File Writer",
    },
    # ... more tools ...
}

actions = Actions()
crafted_action = actions.craft_action_for_objective(objective=objective, tool_list=tool_list, context=None)
```

**Expected Output:**

```python
crafted_action = {
    "Name": "Automated File Backup",
    "Description": "This action automates the process of backing up files from a specified directory...",
    "Example": "To back up all files from the 'documents' directory to a backup file in the 'backup' ...",
    "Instruction": "1. Use the 'Read Directory' tool to list all files in the source directory...",
    "Tools": ["Read Directory", "Read File", "File Writer"],
}
```

---

### **`prime_tool_for_action` Method**

Prepares the tool for execution by running the ToolPrimingAgent.

- **Parameters:**
  - `objective` (str): The objective for tool priming.
  - `action` (Union[str, Dict]): The action to prime the tool for. If a dictionary, it will be formatted using `tool_info_order`.
  - `tool` (Dict): The tool to be primed.
  - `previous_results` (Optional[str]): The results from previous tool executions.
  - `tool_context` (Optional[str]): The context for the tool.
  - `action_info_order` (Optional[List[str]]): The order of action information to include in the Agent prompt.
  - `tool_info_order` (Optional[List[str]]): The order of tool information to include in the Agent prompt.

- **Returns:** Dict: The formatted payload for the tool.

**Example:**

```python
from agentforge.modules.actions import Actions

objective = 'Automate file backup'
action = {
    "Name": "Automated File Backup",
    "Description": "This action automates the process of backing up files from a specified directory...",
    "Example": "To back up all files from the 'documents' directory to a backup file in the 'backup' ...",
    "Instruction": "1. Use the 'Read Directory' tool to list all files in the source directory...",
    "Tools": ["Read Directory", "Read File", "File Writer"],
}
tool = {
    "Args": "directory_paths (str or list of str), max_depth (int)",
    "Command": "read_directory",
    "Description": "The 'Read Directory' tool generates and prints the structure of a directory ...",
    "Example": "directory_path = '/path/to/directory'\nmax_depth = 3\ndirectory_structure = ...",
    "Instruction": "To use the 'Read Directory' tool, follow these steps:\n1. Call the `read_directory` function ...",
    "Name": "Read Directory",
}

actions = Actions()
payload = actions.prime_tool_for_action(objective=objective, action=action, tool=tool)
```

**Expected Output:**

```python
payload = {
    "args": {"directory_paths": "./Files", "max_depth": 3},
    "thoughts": {
        "reasoning": "The 'Read Directory' tool needs to be primed to read the structure of the './Files' ...",
        "speak": "The 'Read Directory' tool is primed to read the structure of the './Files' directory up ...",
        "next_tool_context": "The next tool in the sequence is likely the 'Read File' tool, which will read the ...",
    },
}
```

---

### **`run_tools_in_sequence` Method**

Runs the specified tools in sequence for the given objective and action by running the **ToolPrimingAgent** in sequence and feeding the results of one tool to the next.

- **Parameters:**
  - `objective` (str): The objective for running the tools.
  - `action` (Dict): The action containing the tools to run.
  - `action_info_order` (Optional[List[str]]): The order of action information to include in the Agent prompt.
  - `tool_info_order` (Optional[List[str]]): The order of tool information to include in the Agent prompt.
- **Returns:** Union[Dict, None]: The final result of the tool execution or an error dictionary.

**Example:**

```python
from agentforge.modules.actions import Actions

objective = 'Automate file backup'
action = {
    "Name": "Automated File Backup",
    "Description": "This action automates the process of backing up files from a specified directory...",
    "Tools": ["Read Directory", "Read File", "File Writer"],
}

actions = Actions()
result = actions.run_tools_in_sequence(objective=objective, action=action)
```

**Expected Output:**

```python
result = 'Files copied successfully from path/to/source to path/to/destination'
```

**Explanation:**

The `run_tools_in_sequence` method uses the `prime_tool_for_action` method in a loop, where it primes each tool with the results of the previous tool execution. The **ToolPrimingAgent** interprets the previous results and context to prime the next tool in the sequence, responding with a `next_tool_context` parameter which is used as context for the next tool.
