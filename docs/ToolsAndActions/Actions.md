# Actions

## Overview

**Actions Class Documentation**

The **Actions** class provides a comprehensive suite of methods for managing and executing actions and tools within the framework. It is designed to offer flexibility and modularity, allowing developers to create custom solutions or use generic examples. **Actions** within our framework are sequences of one or more tools executed in a specific order to perform complex tasks. They combine the functionality of individual tools into cohesive workflows. Actions can consist of a single tool or multiple tools, each contributing a step towards the overall objective of the action.

Actions are defined in YAML files and managed within the `actions` directory in the project, facilitating organized development and straightforward access.

**Actions Directory**: You can find the action definitions in the `your_project_root/.agentforge/actions` directory.

## Defining Actions in YAML

Each action is defined in a YAML file, which includes attributes detailing the steps involved:

- **Name**: The title of the action.
- **Description**: A clear explanation of what the action does.
- **Example**: An example command showing how the action could be executed.
- **Instruction**: Step-by-step instructions on how the action should be carried out.
- **Tools**: A list of tools used in the action.

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

## Class Overview

```python
class Actions:
    def __init__(self):
    def initialize_collection(self, collection_name: str) -> None:
    def auto_execute(self, objective: str, context: Optional[str] = None, threshold: Optional[float] = 0.8) -> Union[Dict, None]:
    def get_relevant_actions_for_objective(self, objective: str, threshold: Optional[float] = None, num_results: int = 1, parse_result: bool = True) -> Dict:
    def select_action_for_objective(self, objective: str, action_list: Union[str, Dict], context: Optional[str] = None, parse_result: bool = True) -> Union[str, Dict]:
    def craft_action_for_objective(self, objective: str, tool_list: Union[str, Dict], context: Optional[str] = None, info_order: Optional[List[str]] = None, parse_result: bool = True) -> Union[str, Dict]:
    def run_tools_in_sequence(self, objective: str, action: Dict, action_info_order: Optional[List[str]] = None, tool_info_order: Optional[List[str]] = None) -> Union[Dict, None]:
    def prime_tool(self, objective: str, action: Union[str, Dict], tool: Dict, previous_results: Optional[str], tool_context: Optional[str], action_info_order: Optional[List[str]] = None, tool_info_order: Optional[List[str]] = None) -> Dict:
    def execute_tool(self, tool: Dict, payload: Dict) -> Union[Dict, None]:
    def load_tool_from_storage(self, tool: str) -> Optional[Dict]:
    def get_tool_list(self, num_results: int = 20, parse_result: bool = True) -> Optional[Dict[str, Union[List[str], None, List[Dict]]]]:
    def format_item(item: Dict[str, Union[str, List[str]]], order: Optional[List[str]] = None) -> str:
    def format_item_list(self, item_list: Dict, order: Optional[List[str]] = None) -> Optional[str]:
    def parse_item_list(self, item_list: Dict) -> Optional[Dict[str, Dict]]:
    def parse_tools_in_action(self, action: Dict) -> List[Dict] | None:

```

## Detailed Method Descriptions

### **`__init__` Method**

Initializes the **Actions** class, setting up logger, storage utilities, and loading necessary components for action processing.

- **Parameters:** None
- **Returns:** None

**Example:**

```python
from agentforge.modules.Actions import Actions

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
from agentforge.modules.Actions import Actions

actions = Actions()
actions.initialize_collection('Actions')
actions.initialize_collection('Tools')
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
from agentforge.modules.Actions import Actions

objective = 'Stay up to date with current world events'

actions = Actions()
result = actions.auto_execute(objective)
```

**Expected Output:**

```python
result = 'Here are the the most recent events ...'
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

**Example when `parse_result` is `True`:**

```python
from agentforge.modules.Actions import Actions

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
    "isotimestamp": "2024-08-04 15:53:04",
    "unixtimestamp": 1722808384.63121,
  },
  "Write File": {
    "Description": "The 'Write File' action combines directory examination and file writing operations...",
    "Example": "# Example usage of the Write File action:\ndirectory_structure = read_directory('path/to/folder'...",
    "Instruction": "To perform the 'Write File' action, follow these steps:\n1. Use the 'Read Directory' tool...",
    "Name": "Write File",
    "Tools": "Read Directory, File Writer",
    "isotimestamp": "2024-08-04 15:53:04",
    "unixtimestamp": 1722808384.63121,
  },
}
```

**Example when `parse_result` is `False`:**

```python
from agentforge.modules.Actions import Actions

objective = 'Stay up to date with current world events'
threshold = 0.8

actions = Actions()
actions_list = actions.get_relevant_actions_for_objective(objective=objective, threshold=threshold, num_results=5, parse_result=False)
```

**Expected Output:**

```python
action_list = {
    "ids": ["2", "1"],
    "distances": [0.9825570668139221, 1.0215830964195936],
    "metadatas": [
        {
            "Description": "The 'Web Search' action combines a Google search, web scraping, and text chunking operations...",
            "Example": "# Example usage of the Web Search action:\nquery = \"OpenAI GPT-4\"\n...",
            "Instruction": "To perform the 'Web Search' action, follow these steps:\n1. Use the 'Google Search' tool...",
            "Name": "Web Search",
            "Tools": "Google Search, Web Scrape, Intelligent Chunk",
            "isotimestamp": "2024-08-04 12:33:09",
            "unixtimestamp": 1722796389.9486,
        },
        {
            "Description": "The 'Write File' action combines directory examination and file writing operations...",
            "Example": "# Example usage of the Write File action:\ndirectory_structure = read_directory('path/to/folder'...",
            "Instruction": "To perform the 'Write File' action, follow these steps:\n1. Use the 'Read Directory' tool...",
            "Name": "Write File",
            "Tools": "Read Directory, File Writer",
            "isotimestamp": "2024-08-04 12:33:09",
            "unixtimestamp": 1722796389.9486,
        },
    ],
    "documents": [
        "The 'Web Search' action combines a Google search, web scraping, and text chunking operations...",
        "The 'Write File' action combines directory examination and file writing operations...",
    ],
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
from agentforge.modules.Actions import Actions

objective = 'Stay up to date with current world events'
context = 'Focus your scope on technology' 

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
    "reasoning": "The objective is to \"Stay up to date with current world events\". Performing a web search can help achieve this by retrieving relevant and timely information. The provided actions are not explicitly tailored to this goal, but the 'Web Search' action comes closest in terms of functionality. It allows for a Google search, which can be used to find news articles or updates on global issues. Although it's not a perfect match, I recommend using the 'Web Search' action as it offers the most relevant capabilities to address the objective.",
}
```

**Example when `parse_result` is `False`:**

```python
selected_action = actions.select_action_for_objective(objective=objective, action_list=action_list, context=context, parse_result=False)
```

**Expected Output when `parse_result` is `False`:**

```python
selected_action = """action: Web Search
reasoning: The objective is to "Stay up to date with current world events". Performing a web search can help achieve this by retrieving relevant and timely information. The provided actions are not explicitly tailored to this goal, but the 'Web Search' action comes closest in terms of functionality. It allows for a Google search, which can be used to find news articles or updates on global issues. Although it's not a perfect match, I recommend using the 'Web Search' action as it offers the most relevant capabilities to address the objective."""
```

---

### **`craft_action_for_objective` Method**

Crafts a new action for the given objective using the **Craft Action Agent**.

- **Parameters:**
  - `objective` (str): The objective to craft an action for.
  - `tool_list` (Union[str, Dict]): The list of tools to be used. Will convert to a string for the agent prompt if given a Dict.
  - `context` (Optional[str]): The context for action crafting.
  - `parse_result` (bool): Whether to parse the result (default is True).
  - `info_order` (Optional[List[str]]): Tool information to include in the formatted tool list.
- **Returns:** Union[str, Dict]: The crafted action or formatted result.

**Example:**

```python
from agentforge.modules.Actions import Actions

objective = 'Automate file backup'
tool_list = {
  "File Writer": {
    "Args": "folder (str), file (str), text (str), mode (str='a')",
    "Command": "write_file",
    "Description": "The 'File Writer' tool writes the provided text to a specified file within ...",
    "Example": "write_file(folder='/path/to/folder', file='example.txt', text='Hello, World!', mode='a') ...",
    "Instruction": "To use the 'File Writer' tool, follow these steps:\n1. Call the `write_file` function ...",
    "Name": "File Writer",
    "Script": "agentforge.tools.WriteFile",
    "isotimestamp": "2024-08-06 17:05:17",
    "unixtimestamp": 1722985517.85723,
  },
  # ... more tools ...
}

actions = Actions()
crafted_action = actions.craft_action_for_objective(objective=objective, tool_list=tool_list, context=None)
```

**Expected Output when `parse_result` is `True`:**

```python
crafted_action = {
    "Name": "Automated File Backup",
    "Description": "This action automates the process of backing up files from a specified directory. It reads the contents of the directory, retrieves the text from each file, and writes the content to a backup file in a specified backup directory. This ensures that all files in the target directory are backed up into a single file in the backup directory.\n",
    "Example": "To back up all files from the 'documents' directory to a backup file in the 'backup' directory:\n1. Specify the source directory path as 'documents'.\n2. Specify the backup directory path as 'backup'.\n3. Run the action to create a backup file named 'backup.txt' in the 'backup' directory containing the contents of all files from the 'documents' directory.\n",
    "Instruction": "1. Use the 'Read Directory' tool to list all files in the source directory.\n   - Args: directory_paths='source_directory_path', max_depth=1\n2. For each file in the source directory, use the 'Read File' tool to read its content.\n   - Args: file_path='path_to_each_file'\n3. Use the 'File Writer' tool to write the content of each file to a backup file in the backup directory.\n   - Args: folder='backup_directory_path', file='backup.txt', text='content_of_each_file', mode='a'\n",
    "Tools": ["Read Directory", "Read File", "File Writer"],
}
```

**Example when `parse_result` is `False`:**

```python
crafted_action = actions.craft_action_for_objective(objective=objective, tool_list=tool_list, context=None, parse_result=False)
```

**Expected Output when `parse_result` is `False`:**

```python
crafted_action = """Here is a possible solution in YAML format:

```yaml
Name: Automated File Backup
Description: |+
  This action automates the process of backing up files from a specified directory. It reads the contents of the directory, retrieves the text from each file, and writes the content to a backup file in a specified backup directory. This ensures that all files in the target directory are backed up into a single file in the backup directory.
Example: |+
  To back up all files from the 'documents' directory to a backup file in the 'backup' directory:
  1. Specify the source directory path as 'documents'.
  2. Specify the backup directory path as 'backup'.
  3. Run the action to create a backup file named 'backup.txt' in the 'backup' directory containing the contents of all files from the 'documents' directory.
Instruction: |+
  1. Use the 'Read Directory' tool to list all files in the source directory.
     - Args: directory_paths='source_directory_path', max_depth=1
  2. For each file in the source directory, use the 'Read File' tool to read its content.
     - Args: file_path='path_to_each_file'
  3. Use the 'File Writer' tool to write the content of each file to a backup file in the backup directory.
     - Args: folder='backup_directory_path', file='backup.txt', text='content_of_each_file', mode='a'
Tools:
  - Read Directory
  - Read File
  - File Writer
```"""
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
from agentforge.modules.Actions import Actions

objective = 'Automate file backup'
action = {
    "Name": "Automated File Backup",
    "Description": "This action automates the process of backing up files from a specified directory...",
    "Example": "To back up all files from the 'documents' directory to a backup file in the 'backup' ...",
    "Instruction": "1. Use the 'Read Directory' tool to list all files in the source directory...",
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

The `run_tools_in_sequence` method uses the `prime_tool` method in a loop, where it primes each tool with the results of the previous tool execution. The `ToolPrimingAgent` interprets the previous results and context to prime the next tool in the sequence, responding with a `next_tool_context` parameter which is used as context for the next tool.

---

### Understanding `action_info_order` and `tool_info_order` Parameters

The `action_info_order` and `tool_info_order` parameters define the sequence and attributes of the `action` and `tool` objects that are rendered into the ToolPrimingAgent prompt. These parameters help control what information is included and in what order, ensuring that only the necessary details are provided to the agent for the task.

#### Action and Tool Objects
An `action` object typically includes attributes such as:
- `Name`
- `Description`
- `Example`
- `Instruction`
- `Tools`

A `tool` object typically includes attributes such as:
- `Args`
- `Command`
- `Description`
- `Example`
- `Instruction`
- `Name`
- `Script`

### Parameters Definition
- `action_info_order`: This list defines the attributes from the `action` object that should be included in the prompt and their order.
- `tool_info_order`: This list defines the attributes from the `tool` object that should be included in the prompt and their order.
>**Note:** If no action or tool order is given all attributes will be rendered without a specific order.

### Example Usage
When the `action_info_order` and `tool_info_order` parameters are specified, they determine how the information is included in the **ToolPrimingAgent** prompt. For instance:

```python
from agentforge.modules.Actions import Actions

action_info_order = ["Name", "Description"]
tool_info_order = ["Name", "Description", "Args", "Instruction", "Example"]

action = Actions()
result = action.run_tools_in_sequence(objective=objective,
                                      action=selected_action,
                                      action_info_order=action_info_order,
                                      tool_info_order=tool_info_order)
```

### Rendering the Prompt
The **ToolPrimingAgent** prompt template has placeholders for the **action** and **tool** information:
```yaml
Prompts:
  System: |-
    You are a tool priming agent tasked with preparing a tool for an objective.

  Objective: |+
    Objective:
    {objective}
    
    To achieve this objective, the following action has been selected:
    {action}

  Tool: |+
    Your task is to prime the '{tool_name}' tool in the context of the selected action. Instructions explaining how to use the tool are as follows:
    {tool_info}

  # ... rest of the prompt template ...
```

Based on the above parameters, the **ToolPrimingAgent** prompt will be constructed as follows:

```
You are a tool priming agent tasked with preparing a tool for an objective

Objective:
Automate file backup

To achieve this objective, the following action has been selected:
Name: Automated File Backup
Description:
This action automates the process of backing up files from a specified directory. It reads the content of each file in the directory, writes the content to a backup file in a backup directory, and ensures the backup directory structure is maintained. This action uses the 'Read Directory', 'Read File', and 'File Writer' tools to achieve the objective.

Your task is to prime the 'Read Directory' tool in the context of the selected action. Instructions explaining how to use the tool are as follows:
Name: Read Directory
Description:
The 'Read Directory' tool generates and prints the structure of a directory or multiple directories in a tree-like format. 
It visually represents folders and files, and you can specify the depth of the structure to be printed. 
The tool can handle both a single directory path or a list of directory paths. 
If a specified path does not exist, the tool will create it. 
Additionally, it indicates if a directory is empty or if there are more files beyond the specified depth.

Args:
- directory_paths (str or list of str)
- max_depth (int)

Instruction:
To use the 'Read Directory' tool, follow these steps:
1. Call the `read_directory` function with the following arguments:
   - `directory_paths`: A string representing a single directory path, or a list of strings representing multiple directory paths.
   - `max_depth` (optional): An integer specifying the maximum depth of the directory structure to display. If not provided, the entire directory structure will be displayed.
2. The function will return a string representing the directory structure in a tree-like format.
3. If a specified path does not exist, the tool will create the directory.
4. The tool includes error handling for permissions and file not found errors.
5. Utilize the returned directory structure string as needed for your application.

Example:
# Example usage of the Read Directory tool for a single directory
directory_path = '/path/to/directory'
max_depth = 3
directory_structure = read_directory(directory_path, max_depth)
print(directory_structure)

# Example usage for multiple directories
directory_paths = ['/path/to/directory1', '/path/to/directory2']
max_depth = 2
directory_structure = read_directory(directory_paths, max_depth)
print(directory_structure)

# .... rest of the rendered prompt ...
```

The `action_info_order` and `tool_info_order` parameters provide a flexible and controlled way to render the necessary information into the **ToolPrimingAgent** prompt. By specifying these parameters, you ensure that the agent receives the precise information needed in the correct sequence, facilitating a structured and efficient tool priming process.

---

### **`prime_tool` Method**

Prepares the tool for execution by running the **ToolPrimingAgent**.

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
from agentforge.modules.Actions import Actions

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
  "Script": "agentforge.tools.Directory",
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

**Explanation:**

The `prime_tool` method prepares a tool for execution by formatting the tool information and running the `ToolPrimingAgent`. It constructs a payload that includes the formatted tool information, paths, previous results, and tool context. The `ToolPrimingAgent` returns a payload that includes arguments for the tool and context for the next tool in the sequence. This payload is used to execute the tool and prime the next tool in the sequence if there are more tools to run.

Certainly! Here's an updated version of the documentation for the `execute_tool` method that clarifies the expected output:

---

### **`execute_tool` Method**

Executes the tool using the dynamic tool utility with the prepared payload.

- **Parameters:**
  - `tool` (Dict): The tool to be executed.
  - `payload` (Dict): The payload to execute the tool with.
- **Returns:** Union[Dict, None]: The result of the tool execution or an error dictionary.

**Example:**

```python
from agentforge.modules.Actions import Actions

tool = {
  "Args": "directory_paths (str or list of str), max_depth (int)",
  "Command": "read_directory",
  "Description": "The 'Read Directory' tool generates and prints the structure of a directory ...",
  "Example": "directory_path = '/path/to/directory'\nmax_depth = 3\ndirectory_structure = ...",
  "Instruction": "To use the 'Read Directory' tool, follow these steps:\n1. Call the `read_directory` function ...",
  "Name": "Read Directory",
  "Script": "agentforge.tools.Directory",
}
payload = {
  "args": {"directory_paths": "./Files", "max_depth": 3},
  "thoughts": {
    "reasoning": "The 'Read Directory' tool needs to be primed to read the structure of the './Files' ...",
    "speak": "The 'Read Directory' tool is primed to read the structure of the './Files' directory up ...",
    "next_tool_context": "The next tool in the sequence is likely the 'Read File' tool, which will read the ...",
  },
}

actions = Actions()
result = actions.execute_tool(tool=tool, payload=payload)
```

**Expected Output:**

The expected output varies based on the tool being executed and its specific implementation. It could be:

- A result corresponding to the tool's functionality, such as:
  - A text representation of a folder tree if using a directory reading tool.
  - A success message indicating the completion of a file write operation.
  - A numerical result if the tool performs calculations.
- An error message if the tool encounters an issue during execution and includes graceful error handling.

**Example Output:**

```python
# For a successful scenario
result = {
  "status": "success",
  "data": "Folder tree structure..."
}

# For an error scenario
result = {
  "status": "error",
  "message": "An error occurred: Directory not found",
  "traceback": "Traceback (most recent call last):\n  File ..." 
}
```

The actual output will depend on the specific tool and its implementation.

---

### **`load_tool_from_storage` Method**

Loads configuration and data for a specified tool from the storage.

- **Parameters:**
  - `tool` (str): The name of the tool to load.
- **Returns:** Optional[Dict]: The loaded tool data, or None if an error occurs.

**Example:**

```python
from agentforge.modules.Actions import Actions

tool_name = 'Read Directory'

actions = Actions()
tool = actions.load_tool_from_storage(tool=tool_name)
```

**Expected Output:**

```python
tool = {
  "Args": "directory_paths (str or list of str), max_depth (int)",
  "Command": "read_directory",
  "Description": "The 'Read Directory' tool generates and prints the structure of a directory ...",
  "Example": "directory_path = '/path/to/directory'\nmax_depth = 3\ndirectory_structure = ...",
  "Instruction": "To use the 'Read Directory' tool, follow these steps:\n1. Call the `read_directory` function ...",
  "Name": "Read Directory",
  "Script": "agentforge.tools.Directory",
}
```

---

### **`get_tool_list` Method**

Retrieves the list of tools from storage.

- **Parameters:**
  - `num_results` (int): The number of tools to return.
  - `parse_result` (bool): Whether to parse the tool list for easier handling (default is True).
- **Returns:** Optional[Dict[str, Union[List[str], None, List[Dict]]]]: A dictionary containing all tool information, or None if there are no tools.

**Example with `parse_result` set to `True`:**

```python
from agentforge.modules.Actions import Actions

actions = Actions()
tool_list = actions.get_tool_list(num_results=10)
```

**Expected Output if `parse_result` is `True`:**

```python
tool_list = {
  "Google Search": {
    "Args": "query (str), number_result (int)",
    "Command": "google_search",
    "Description": "The 'Google Search' tool performs an internet search for a specified query and ...",
    "Example": "google_search(query='OpenAI', number_result=5) ...",
    "Instruction": "To use the 'Google Search' tool, follow these steps:\n1. Call the `google_search` function ...",
    "Name": "Google Search",
    "Script": "agentforge.tools.GoogleSearch",
    "isotimestamp": "2024-08-06 17:05:17",
    "unixtimestamp": 1722985517.85723,
  },
  "File Writer": {
    "Args": "folder (str), file (str), text (str), mode (str='a')",
    "Command": "write_file",
    "Description": "The 'File Writer' tool writes the provided text to a specified file within a given folder...",
    "Example": "write_file(folder='/path/to/folder', file='example.txt', text='Hello, World!', mode='a') ...",
    "Instruction": "To use the 'File Writer' tool, follow these steps:\n1. Call the `write_file` function ...",
    "Name": "File Writer",
    "Script": "agentforge.tools.WriteFile",
    "isotimestamp": "2024-08-06 17:05:17",
    "unixtimestamp": 1722985517.85723,
  },
  # ... more tools ...
}
```

**Example with `parse_result` set to `False`:**

```python
from agentforge.modules.Actions import Actions

actions = Actions()
tool_list = actions.get_tool_list(num_results=10, parse_result=False)
```

**Expected Output if `parse_result` is `False`:**

```python
tool_list = {
    "ids": ["1", "2", "3", "4", "5", "6"],
    "embeddings": None,
    "metadatas": [
        {
          "Args": "query (str), number_result (int)",
          "Command": "google_search",
          "Description": "The 'Google Search' tool performs an internet search for a specified query and ...",
          "Example": "google_search(query='OpenAI', number_result=5) ...",
          "Instruction": "To use the 'Google Search' tool, follow these steps:\n1. Call the `google_search` function ...",
          "Name": "Google Search",
          "Script": "agentforge.tools.GoogleSearch",
          "isotimestamp": "2024-08-06 17:05:17",
          "unixtimestamp": 1722985517.85723,
        },
        {
          "Args": "folder (str), file (str), text (str), mode (str='a')",
          "Command": "write_file",
          "Description": "The 'File Writer' tool writes the provided text to a specified file within a given folder...",
          "Example": "write_file(folder='/path/to/folder', file='example.txt', text='Hello, World!', mode='a') ...",
          "Instruction": "To use the 'File Writer' tool, follow these steps:\n1. Call the `write_file` function ...",
          "Name": "File Writer",
          "Script": "agentforge.tools.WriteFile",
          "isotimestamp": "2024-08-06 17:05:17",
          "unixtimestamp": 1722985517.85723,
        },
        # ... more tools ...
    ],
    "uris": None,
    "data": None,
    "included": ["documents", "metadatas"],
}
```

---

### **`format_item` Method**

Formats an item (action or tool) into a human-readable string.

- **Parameters:**
  - `item` (Dict[str, Union[str, List[str]]]): The item to format.
  - `order` (Optional[List[str]]): The order in which to format the item's keys.
- **Returns:** str: The formatted item string.

**Example:**

```python
from agentforge.modules.Actions import Actions

item = {
    "Name": "Copy Files",
    "Description": "The 'Copy Files' tool copies files from one location to another...",
    "Args": "source_path, destination_path",
    "Instruction": "To use the 'Copy Files' tool, provide the source and destination paths...",
    "Example": "copy_files('path/to/source', 'path/to/destination')",
}
order = ["Name", "Description", "Args", "Instruction", "Example"]

actions = Actions()
formatted_item = actions.format_item(item=item, order=order)
```

**Expected Output:**

```python
formatted_item = """Name: Copy Files
Description: The 'Copy Files' tool copies files from one location to another...
Args:
- source_path
- destination_path

Instruction:
To use the 'Copy Files' tool, provide the source and destination paths...

Example:
copy_files('path/to/source', 'path/to/destination')
"""
```

---

### **`format_item_list` Method**

Formats the actions into a human-readable string based on a given order and stores it in the agent's data for later use.

- **Parameters:**
  - `item_list` (Dict): The list of actions or tools to format.
  - `order` (Optional[List[str]]): The order in which to format the action's keys.
- **Returns:** Optional[str]: The formatted string of actions, or None if an error occurs.

**Example:**

```python
from agentforge.modules.Actions import Actions

item_list = {
  "Copy Files": {
    "Name": "Copy Files",
    "Description": "The 'Copy Files' tool copies files from one location to another...",
    "Args": "source_path, destination_path",
    "Instruction": "To use the 'Copy Files' tool, provide the source and destination paths...",
    "Example": "copy_files('path/to/source', 'path/to/destination')",
  },
  "Move Files": {
    "Name": "Move Files",
    "Description": "The 'Move Files' tool moves files from one location to another...",
    "Args": "source_path, destination_path",
    "Instruction": "To use the 'Move Files' tool, provide the source and destination paths...",
    "Example": "move_files('path/to/source', 'path/to/destination')",
  },
}

actions = Actions()
formatted_list = actions.format_item_list(items=item_list)
```

**Expected Output:**

```python
formatted_list = """---
Name: Copy Files
Description: The 'Copy Files' tool copies files from one location to another...
Args:
- source_path
- destination_path

Instruction:
To use the 'Copy Files' tool, provide the source and destination paths...

Example:
copy_files('path/to/source', 'path/to/destination')
---
Name: Move Files
Description: The 'Move Files' tool moves files from one location to another...
Args:
- source_path
- destination_path

Instruction:
To use the 'Move Files' tool, provide the source and destination paths...

Example:
move_files('path/to/source', 'path/to/destination')
---
"""
```

---

### **`parse_item_list` Method**

Parses and structures the actions fetched from storage for easier handling and processing.

- **Parameters:**
  - `item_list` (Dict): The list of actions or tools to parse.
- **Returns:** Optional[Dict[str, Dict]]: A dictionary of parsed actions, or None if an error occurs.

**Example:**

```python
from agentforge.modules.Actions import Actions

item_list = { # This could be a tool or action list
    "ids": ["1", "2", "3", "4", "5", "6"],
    "embeddings": None,
    "metadatas": [
        {
          "Args": "query (str), number_result (int)",
          "Command": "google_search",
          "Description": "The 'Google Search' tool performs an internet search for a specified query and ...",
          "Example": "google_search(query='OpenAI', number_result=5) ...",
          "Instruction": "To use the 'Google Search' tool, follow these steps:\n1. Call the `google_search` function ...",
          "Name": "Google Search",
          "Script": "agentforge.tools.GoogleSearch",
          "isotimestamp": "2024-08-06 17:05:17",
          "unixtimestamp": 1722985517.85723,
        },
        {
          "Args": "folder (str), file (str), text (str), mode (str='a')",
          "Command": "write_file",
          "Description": "The 'File Writer' tool writes the provided text to a specified file within a given folder...",
          "Example": "write_file(folder='/path/to/folder', file='example.txt', text='Hello, World!', mode='a') ...",
          "Instruction": "To use the 'File Writer' tool, follow these steps:\n1. Call the `write_file` function ...",
          "Name": "File Writer",
          "Script": "agentforge.tools.WriteFile",
          "isotimestamp": "2024-08-06 17:05:17",
          "unixtimestamp": 1722985517.85723,
        },
        # ... more tools ...
    ],
    "uris": None,
    "data": None,
    "included": ["documents", "metadatas"],
}

actions = Actions()
parsed_list = actions.parse_item_list(item_list=item_list)
```

**Expected Output:**

```python
parsed_list = {
    "Copy Files": {
        "Name": "Copy Files",
        "Description": "The 'Copy Files' tool copies files from one location to another...",
        "Args": "source_path, destination_path",
        "Instruction": "To use the 'Copy Files' tool, provide the source and destination paths...",
        "Example": "copy_files('path/to/source', 'path/to/destination')",
    },
    "Move Files": {
        "Name": "Move Files",
        "Description": "The 'Move Files' tool moves files from one location to another...",
        "Args": "source_path, destination_path",
        "Instruction": "To use the 'Move Files' tool, provide the source and destination paths...",
        "Example": "move_files('path/to/source', 'path/to/destination')",
    },
}
```

---

### **`parse_tools_in_action` Method**

Loads the tools specified in the action's configuration.

- **Parameters:**
  - `action` (Dict): The action containing the tools to load.
- **Returns:** List[Dict]: A list with the loaded tools or None.

**Example:**

```python
from agentforge.modules.Actions import Actions

action = {
    "Name": "File Backup",
    "Description": "The 'File Backup' action performs automated file backup operations...",
    "Tools": ["Copy Files", "Move Files"],
}

actions = Actions()
tools = actions.parse_tools_in_action(action=action)
```

**Expected Output:**

```python
tools = [
    {
        "Name": "Copy Files",
        "Description": "The 'Copy Files' tool copies files from one location to another...",
        "Args": "source_path, destination_path",
        "Instruction": "To use the 'Copy Files' tool, provide the source and destination paths...",
        "Example": "copy_files('path/to/source', 'path/to/destination')",
    },
    {
        "Name": "Move Files",
        "Description": "The 'Move Files' tool moves files from one location to another...",
        "Args": "source_path, destination_path",
        "Instruction": "To use the 'Move Files' tool, provide the source and destination paths...",
        "Example": "move_files('path/to/source', 'path/to/destination')",
    },
]
```

---
