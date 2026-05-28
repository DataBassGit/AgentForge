# Dynamic Toos l& Skills Functionality

## Introduction to Dynamic Tools

The Dynamic Tool & Skill system within our framework serves as a universal handler for executing functionalities. This system is designed to be model-agnostic, meaning that it can work with any model as long as the model is capable of responding in the correct format and possesses the requisite intelligence to execute the functions. Capabilities are defined and managed within dedicated directories, allowing for organized development and easy access.

There are two primary ways to extend the framework:

1. Skills (`SKILLS.md`): The modern standard for CLI-based commands, utilizing an isolated Docker environment for secure execution. Located in `your_project_root/.agentforge/skills`.

2. Python Tools (YAML): Native Python execution for deep framework integration and memory access. Located in `your_project_root/.agentforge/tools`.

## Defining Skills (The SKILLS Standard)

The Skills system is our standard for adding CLI-based executables, mapping closely to standard context protocols. Skills are parsed from `SKILLS.md` (or `SKILL.md`) files located anywhere recursively within your `.agentforge/skills` directory structure.

Skills use YAML Frontmatter for metadata and configuration, and the Markdown body as the tool's instruction set for the agent.

### Example SKILLS.md Definition
```markdown
---
name: blogwatcher
description: "Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool."
version: 2.0.0
author: JulienTant
platforms: [linux, macos, windows]
metadata:
  tags: [RSS, Blogs, Feed-Reader, Monitoring]
prerequisites:
  commands: [blogwatcher-cli]
---

# Blogwatcher

Track blog and RSS/Atom feed updates with the `blogwatcher-cli` tool. Supports automatic feed discovery, HTML scraping fallback, OPML import, and read/unread article management.

[... additional markdown instructions ...]

```

### Key Skill Attributes

 - **name**: A descriptive title for the skill (used in vector search and tool selection).

 - **description**: A clear explanation of what the skill does. Used as the primary document for vector semantic search.

 - **Markdown Body**: Read automatically as the Instruction parameter, providing agents with context on how to use the tool.

*note: see https://github.com/anthropics/skills for more details about how to write skills properly.*

### Secure Docker Execution

To maintain system security, all Skills execute strictly inside a persistent Docker container. The system automatically provisions and attaches to an `ubuntu:latest` container named `agentforge_skills_env` at runtime. This prevents LLM-driven shell execution vulnerabilities on the host machine. The system will throw a `RuntimeError` if an agent attempts to execute a CLI skill natively on the host machine.

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

To execute a **tool**, use the `dynamic_tool` method in the `ToolUtils` class. The method dynamically loads the specified **tool** or **skill** based on its module path and executes it using the provided arguments.

### Dynamic Tool Execution Process

1. **Dynamic Module Import**: The tool's script module is dynamically imported and routes the execution directly into the isolated `agentforge_skills_env` Docker container via the Docker SDK
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

In practice, however, you would not be building this payload or tool manually. The tool should be selected via searching chromadb for an appropriate tool, and the payload would be generated by an agent.

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

- **Docker Daemon**: Ensure Docker is installed and running on the host machine. If Docker is unavailable, the initialization process will log a warning and CLI skills execution will be completely disabled.
- **Python Packages**: The docker Python SDK (pip install docker) and pyyaml are required for parsing and executing the new SKILLS standard.
- **Script Path Specification**: Ensure that the `Script` path in the **YAML** definition matches the exact name of the module in the Python environment.
- **Function Compatibility**: The Python library function or method should be compatible with dynamic calling and must be defined within the specified script path.

## Best Practices for Tool Definitions

_ **Default to Skills***: If you are writing an integration with a third-party application or a CLI tool, always use the `SKILLS.md` standard. It is safer, more portable, and aligns with broader industry Context Protocols.
- **Keep Python Tools Local**: Use YAML Python tools only when you need deep integrations with local memory, system states, or internal Python logic.
- **Validate Your Definitions**: Test each **YAML** tool definition to ensure it functions as expected.
- **Follow the Format**: Adhere to the **YAML** format provided in the example to avoid execution errors.

By adhering to these guidelines and properly defining your tools in **YAML** files, you can leverage the Dynamic Tool functionality to enhance the automation capabilities of your system.

---
