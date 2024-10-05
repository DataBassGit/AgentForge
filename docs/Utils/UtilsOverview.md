# Utilities Documentation

## Introduction to Functions

`Functions` is a crucial class within the **AgentForge** framework, designed to provide a suite of utility functions that facilitate various agent operations. This class is instrumental in equipping agents with the necessary configurations and data, ensuring they are primed for their designated tasks.

## Function Utilities

The `function_utils.py` script is a convenience class that aggregates several utility scripts, each tailored to a specific aspect of the **AgentForge** system's functionality.

### Included Utilities

- **[ParsingUtils](ParsingUtils.md)**: Contains methods for parsing formatted text into python dictionaries.
- **[PromptHandling](PromptHandling.md)**: Manages the rendering and handling of prompts that guide agent actions and responses.
- **[ToolUtils](ToolUtils.md)**: Facilitates the dynamic execution of tools, integral to performing actions within the system.
- **[UserInterface](UserInterface.md)**: Currently focused on console interaction, provides methods for managing user inputs and system modes.

Each utility script can be accessed via the `Functions` class:

### Logger Utilities


### **Example Usage**
```python
from agentforge.utils.function_utils import Functions

# Initialize the Functions class
functions = Functions()

yaml_string = '# Yaml content goes here'
# Utilize a specific utility
parsed_yaml = functions.parsing_utils.parse_yaml_content(yaml_string)
```

In this example we are parsing a string containing yaml into a python dictionary, this is useful for parsing agent responses formatted in **YAML**.


