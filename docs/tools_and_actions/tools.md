# ⚠️ DEPRECATION WARNING

**The Tools system is DEPRECATED.**

Do NOT use in production or with untrusted input. This system will be replaced in a future version with a secure implementation based on the MCP standard.

See: https://github.com/DataBassGit/AgentForge/issues/116 for details.

# Dynamic Tool Functionality

## Introduction to Dynamic Tools

The **Dynamic Tool** system within our framework serves as a universal handler for executing functionalities, known as **tools**, which are specified in **YAML** files. This system is designed to be model-agnostic, meaning that it can work with any model as long as the model is capable of responding in the correct format and possesses the requisite intelligence to execute the functions. Tools are defined and managed within a dedicated directory in the project structure, allowing for organized development and easy access.

**Tools Directory**: The tools are located within the `tools` directory in the project. Navigate to `your_project_root/.agentforge/tools` to access the **YAML** files for each tool.

## Defining Tools in YAML

Each **tool** is meticulously described in a **YAML** file, encompassing several key attributes for a complete and actionable definition:

- **Name**: A descriptive title for the tool.
- **Args**: Specifications of the arguments that the tool accepts, along with their respective data types.
- **Command**: The name of the function or method to be executed by the tool.
- **Description**: A detailed explanation of the tool's purpose and functionality.
- **Example**: A code snippet demonstrating the tool's usage.
- **Instruction**: Detailed steps on how to utilize the tool.
- **Script**: The path to the Python module where the tool's implementation resides.
- **Class**: The relevant class that contains the "Command" from above. Omit if the function is not in a class.

Here's a full example of a tool definition in YAML format:

```yaml
Name: Brave Search
Args:
  - query (str)
  - count (int, optional)
Command: search
Description: |
  The 'Brave Search' tool performs a web search using the Brave Search API. It retrieves search results based on the provided query. Each result includes the title, URL, description, and any extra snippets.

Instruction: |
  To use the 'Brave Search' tool, follow these steps:
  1. Call the `search` method with the following arguments:
     - `query`: A string representing the search query.
     - `count`: (Optional) An integer specifying the number of search results to retrieve. Defaults to 10 if not specified.
  2. The method returns a dictionary containing search results in the keys:
     - `'web_results'`: A list of web search results.
     - `'video_results'`: A list of video search results (if any).
  3. Each item in `'web_results'` includes:
     - `title`: The title of the result.
     - `url`: The URL of the result.
     - `description`: A brief description of the result.
     - `extra_snippets`: (Optional) Additional snippets of information.
  4. Utilize the returned results as needed in your application.

Example: |
  # Example usage of the Brave Search tool:
  brave_search = BraveSearch()
  results = brave_search.search(query='OpenAI GPT-4', count=5)
  for result in results['web_results']:
      print(f"Title: {result['title']}")
      print(f"URL: {result['url']}")
      print(f"Description: {result['description']}")
      print('---')

Script: .agentforge.tools.brave_search
Class: BraveSearch
```

In addition to defining **tools**, our system comes with a set of built in **tools**, which are python scripts located in the `agentforge/tools/` directory within the library package. These scripts can be used and referenced in the same way as the Brave Search example provided.

## Executing Tools with Dynamic Tool Functionality

To execute a **tool**, use the `dynamic_tool` method in the `ToolUtils` class. The method dynamically loads the specified **tool** based on its module path and executes it using the provided arguments.

### Dynamic Tool Execution Process

1. **Dynamic Module Import**: The tool's script module is dynamically imported using the `importlib` library.
2. **Command Execution**: The specific command (function or method) mentioned in the tool's **YAML** definition is then executed with the provided arguments.
3. **Result Handling**: The result of the command execution is returned as an object, potentially being used in further processing or returned to the caller.

### Example Tool Execution Code

To execute a **tool**, use the necessary information from the **tool**'s **YAML** file. Below is an example of how to use the `dynamic_tool` method with details typically found in a **tool**'s **YAML** definition:

```yaml
# brave_search.yaml
Name: Brave Search
Args: 
  - query (str)
  - number_result (int, optional)
Script: .agentforge.tools.brave_search
Class: BraveSearch
```

Based on the **YAML** file, we can construct a `payload` in Python and call the `dynamic_tool` method. Here we are doing this manually as an exercise, but the payload can also be built from the yaml file directly:

```python
from agentforge.utils.tool_utils import ToolUtils

tool_utils = ToolUtils()

# Create the tool dictionary with required keys
tool = {
    "Script": ".agentforge.tools.brave_search",  # Module path
    "Class": "BraveSearch",  # The class name in the module
    "Command": "search"  # The method to call
}

# The 'payload' dictionary is constructed based on the specifications from the 'google_search.yaml' file
payload = {
    "command": "search",  # Corresponds to the 'Command' in the YAML
    "args": {
        "query": "OpenAI",  # Corresponds to the 'Args' in the YAML
        "number_result": 5  # Corresponds to the 'Args' in the YAML
    }
}

# 'tool_module' is the path to the script specified under 'Script' in the YAML file
result = tool_utils.dynamic_tool(tool, payload)

# The result of the execution will be handled by the tool_utils object
```

>**Note on Tool Attributes**: Not all attributes defined in the tool's **YAML** file are used when executing the **tool** with the `dynamic_tool` method. Attributes such as `Name`, `Description`, `Example`, and `Instruction` provide context and usage information, which is crucial for the Large Language Model (LLM) to understand how to prime and prepare the **tool** for use. They inform the LLM about the **tool**'s purpose, how it operates, and how to properly integrate it into workflows. The actual execution relies on the `Command`, `Args`, and `Script` attributes to dynamically load and run the **tool**. The context becomes more relevant when we get into [Actions](actions.md).

## Implementing Custom Tools

For those looking to expand the system's capabilities with their own functionalities, users can create a `Custom Tools` directory inside their project folder. The path to these custom scripts should be set in the **tool**'s **YAML** file, which still resides within the `your_project_root/.agentforge/tools` directory. This allows users to seamlessly integrate their custom scripts into the system's workflow.

Here's an example structure for a custom tool definition:

```yaml
Name: My Custom Tool
Args: 
  - param1 (str)
  - param2 (int)
Command: my_custom_function
Script: my_project.Custom_Tools.MyCustomToolScript
Class: ClassName
```

Ensure that the `Script` attribute correctly points to the custom tool's script location within your project.

## Compatibility and Requirements

- **Script Path Specification**: Ensure that the `Script` path in the **YAML** definition matches the exact name of the module in the Python environment.
- **Function Compatibility**: The Python library function or method should be compatible with dynamic calling and must be defined within the specified script path.

## Best Practices for Tool Definitions

- **Validate Your Definitions**: Test each **YAML** tool definition to ensure it functions as expected.
- **Follow the Format**: Adhere to the **YAML** format provided in the example to avoid execution errors.

By adhering to these guidelines and properly defining your tools in **YAML** files, you can leverage the Dynamic Tool functionality to enhance the automation capabilities of your system.

---
