# Dynamic Tool Functionality

## Introduction to Dynamic Tools

The Dynamic Tool system within our framework serves as a universal handler for executing functionalities, known as "tools," which are specified in YAML files. This system is designed to be model-agnostic, meaning that it can work with any model as long as the model is capable of responding in the correct format and possesses the requisite intelligence to execute the functions. Tools are defined and managed within a dedicated directory in the project structure, allowing for organized development and easy access.

**Tools Directory**: The tools are located within the `tools` directory in the project. Navigate to `your_project_root/.agentforge/tools` to access the YAML files for each tool.

## Defining Tools in YAML

Each tool is meticulously described in a YAML file, encompassing several key attributes for a complete and actionable definition:

- **Name**: A descriptive title for the tool.
- **Args**: Specifications of the arguments that the tool accepts, along with their respective data types.
- **Command**: The name of the function or method to be executed by the tool.
- **Description**: A detailed explanation of the tool's purpose and functionality.
- **Example**: A code snippet demonstrating the tool's usage.
- **Instruction**: Detailed steps on how to utilize the tool.
- **Script**: The path to the Python module where the tool's implementation resides.

Here's a full example of a tool definition in YAML format:

```yaml
Name: Google Search
Args: 
  - query (str)
  - number_result (int)
Command: google_search
Description: |-
  The 'Google Search' tool performs an internet search for a specified query and retrieves a specified number of results. 
  Each result includes a URL and a brief snippet summarizing the content of the page.
Example: |-
  # Example usage of the Google Search tool:
  search_results = google_search(query='OpenAI', number_result=5)
  for result in search_results:
      print(f"URL: {result[0]}, Snippet: {result[1]}")
Instruction: |-
  To use the 'Google Search' tool, follow these steps:
  1. Call the `google_search` function with two arguments:
     - `query`: A string representing the search query.
     - `number_result`: An integer specifying the number of search results to retrieve.
  2. The function will return a list of tuples, where each tuple contains:
     - A URL (string) of the search result.
     - A snippet (string) summarizing the content of the result.
  3. Utilize the returned list of results as needed for your application.
Script: .agentforge.tools.GoogleSearch
```

In addition to defining tools, our system comes with a set of default custom tools, which are Python scripts located in the `agentforge/tools/` directory within the library package. These scripts can be used and referenced in the same way as the Google Search example provided.

## Executing Tools with Dynamic Tool Functionality

To execute a tool, use the `dynamic_tool` method in the `ToolUtils` class. The method dynamically loads the specified tool based on its module path and executes it using the provided arguments.

### Dynamic Tool Execution Process

1. **Dynamic Module Import**: The tool's script module is dynamically imported using the `importlib` library.
2. **Command Execution**: The specific command (function or method) mentioned in the tool's YAML definition is then executed with the provided arguments.
3. **Result Handling**: The result of the command execution is handled appropriately, potentially being used in further processing or returned to the caller.

### Example Tool Execution Code

To execute a tool, use the necessary information from the tool's YAML file. Below is an example of how to use the `dynamic_tool` method with details typically found in a tool's YAML definition:

```yaml
# GoogleSearch.yaml
Name: Google Search
Args: 
  - query (str)
  - number_result (int)
Command: google_search
Script: .agentforge.tools.GoogleSearch
```

Based on the YAML file, we construct a `payload` in Python and call the `dynamic_tool` method:

```python
tool_utils = ToolUtils()
# The 'payload' dictionary is constructed based on the specifications from the 'GoogleSearch.yaml' file
payload = {
  "command": "google_search", # Corresponds to the 'Command' in the YAML
  "args": {
    "query": "OpenAI",       # Corresponds to the 'Args' in the YAML
    "number_result": 5       # Corresponds to the 'Args' in the YAML
  }
}

# 'tool_module' is the path to the script specified under 'Script' in the YAML file
result = tool_utils.dynamic_tool(".agentforge.tools.GoogleSearch", payload)

# The result of the execution will be handled by the tool_utils object
```

>**Note on Tool Attributes**: Not all attributes defined in the tool's YAML file are used when executing the tool with the `dynamic_tool` method. Attributes such as `Name`, `Description`, `Example`, and `Instruction` provide context and usage information, which is crucial for the Large Language Model (LLM) to understand how to prime and prepare the tool for use. They inform the LLM about the tool's purpose, how it operates, and how to properly integrate it into workflows. The actual execution relies on the `Command`, `Args`, and `Script` attributes to dynamically load and run the tool.

## Implementing Custom Tools

For those looking to expand the system's capabilities with their own functionalities, users can create a `Custom Tools` directory inside their project folder. The path to these custom scripts should be set in the tool's YAML file, which still resides within the `your_project_root/.agentforge/tools` directory. This allows users to seamlessly integrate their custom scripts into the system's workflow.

Here's an example structure for a custom tool definition:

```yaml
Name: My Custom Tool
Args: 
  - param1 (str)
  - param2 (int)
Command: my_custom_function
Script: my_project.Custom_Tools.MyCustomToolScript
```

Ensure that the `Script` attribute correctly points to the custom tool's script location within your project.

### Utilizing Python Libraries

Users are also free to reference any Python library functions or methods installed in the same environment as the project. Simply specify the library path in the `Script` attribute of the tool's YAML file.

## Future Implementations

Looking ahead, we plan to introduce 'Automatic Tool Creation' capabilities within our system. This will enable the system to autonomously develop and incorporate new tools based on operational data and interactions, all without direct human oversight. Such a feature promises to greatly enhance the system's adaptability and expand its functional repertoire, facilitating continuous evolution and efficiency in task automation.

## Compatibility and Requirements

- **Script Path Specification**: Ensure that the `Script` path in the YAML definition matches the exact name of the module in the Python environment.
- **Function Compatibility**: The Python library function or method should be compatible with dynamic calling and must be defined within the specified script path.

## Best Practices for Tool Definitions

- **Validate Your Definitions**: Test each YAML tool definition to ensure it functions as expected.
- **Follow the Format**: Adhere to the YAML format provided in the example to avoid execution errors.

By adhering to these guidelines and properly defining your tools in YAML files, you can leverage the Dynamic Tool functionality to enhance the automation capabilities of your system.

---
