from agentforge.utils.functions.ParsingUtils import parse_yaml_string

# Utilities Overview

## Introduction to Utilities

Utilities in the **AgentForge** system are a collection of support scripts and classes that enhance the functionality and user experience. They serve as the backbone for various operations within the framework, from handling prompts and tasks to providing user interfaces and parsing data.

This document provides an overview of the Utilities available, focusing on their usability and how they can be leveraged to build and maintain a robust **AgentForge** implementation.

## Function Utilities

The `function_utils.py` script is a convenience class that aggregates several utility scripts, each tailored to a specific aspect of the **AgentForge** system's functionality.

### Included Utilities

- **[AgentUtils](AgentUtils.md)**: Offers functions related to agent operations, including data loading and parsing.
- **[Logger](Logger)**: Contains functions for logging to both files and the console, allowing for more debugging control.
- **[PromptHandling](PromptHandling.md)**: Manages the rendering and handling of prompts that guide agent actions and responses.
- **[ToolUtils](ToolUtils.md)**: Facilitates the dynamic execution of tools, integral to performing actions within the system.
- **[UserInterface](UserInterface.md)**: Currently focused on console interaction, provides methods for managing user inputs and system modes.

Each utility script can be accessed via the `Functions` class:

```python
from agentforge.utils.function_utils import Functions

# Initialize the Functions class
functions = Functions()

# Utilize a specific utility
parsed_yaml = parse_yaml_string(functions.agent_utils.logger, yaml_string)
```

## Additional Utilities

Beyond the foundational function utilities, AgentForge encompasses scripts that facilitate integration with external services and data management systems:

- **[Storage Interface](StorageInterface.md).**: Acts as the central hub for data storage and retrieval operations within **AgentForge**, offering a standardized interface for interacting with various databases or filesystems. It's designed with flexibility in mind, allowing it to connect with different database implementations by using consistent method names across the board.
  
- **[ChromaUtils](../../src/agentforge/utils/chroma_utils.py)**: Integrates ChromaDB with the StorageInterface Utility, providing a specialized database for the system. While ChromaDB is the default, the framework is adaptable to other databases such as SQL or Pinecone, provided they have corresponding utility scripts with matching method signatures.

- **[PineconeUtils](../../src/agentforge/utils/pinecone_utils.py)**: Similar to ChromaUtils, PineconeUtils connects Pinecone — a vector database optimized for machine learning models — with the StorageInterface. This allows the system to leverage Pinecone's capabilities for managing vector data efficiently. **Note: Currently Non-Functional**

These utilities play an instrumental role in augmenting the **AgentForge** system, ensuring seamless interactions with a variety of data sources and external services.

For in-depth information on how to utilize the StorageInterface class
and integrate various databases within your **AgentForge** setup,
please refer to our [Storage Interface Detailed Documentation](StorageInterface.md).
