from agentforge.utils.functions.ParsingUtils import parse_yaml_stringfrom agentforge.utils.functions.ParsingUtils import extract_yaml_block

# Agent Utils Documentation

## Introduction

`AgentUtils` is a crucial class within the **AgentForge** framework, designed to provide a suite of utility functions that facilitate various agent operations. Key among its functionalities are loading agent-specific configurations, handling persona data, and parsing YAML content. This class is instrumental in equipping agents with the necessary configurations and data, ensuring they are primed for their designated tasks.

## Loading Agent Data

The `load_agent_data` method is pivotal in initializing an agent with its requisite configurations, sourcing data from multiple defined settings and potentially agent-specific overrides.

### Example Usage:

```python
agent_utils = AgentUtils()
agent_data = agent_utils.load_agent_data('AgentName')
```

This function initializes `AgentName` with all necessary configurations, encompassing several critical components:

- **Model and API Overrides**: If the agent specifies alternative model or API settings, these are applied here, superseding the default configurations.
- **Parameter Merging**: Default parameters from the model settings are merged with any agent-specific or model-specific overrides, culminating in a final parameter set for the agent's operation.
- **Persona Data**: Incorporates the ability to utilize a specific persona, enhancing the agent's interaction capabilities based on predefined or dynamically assigned personas.
- **Prompts and Storage**: Ensures that the agent is supplied with the necessary prompts for operation and access to storage utilities for data handling.

The extracted `agent_data` dictionary includes the following keys, populating `self.agent_data` within the agent instance:

- `name`: The name of the agent.
- `settings`: General settings from the configuration, relevant to all agents.
- `llm`: An instance of the language model, initialized based on the specified or overridden API and model settings.
- `params`: Finalized parameters for the language model, considering all levels of overrides and defaults.
- `prompts`: A collection of prompt templates designated for the agent, extracted from its corresponding YAML file.
- `storage`: An interface to the storage utility, facilitating data access and persistence.
- `persona`: Persona details if specified, which could alter the agent's interaction style or data processing.

## Parsing YAML Strings

`AgentUtils` also specializes in parsing YAML-formatted strings into Python dictionaries, a process integral to interpreting agent configurations or dynamic content.

### Example Usage:

```python
yaml_content = parse_yaml_string(agent_utils.logger, yaml_block)
```

### Parsing Process:

- The `parse_yaml_string` method accepts a YAML string and converts it into a structured Python dictionary. This functionality is essential for agents that need to interpret or utilize configuration data and settings expressed in YAML within their operational context.

## Extracting YAML Blocks

Additionally, the class can extract YAML content from larger text blocks, a feature useful when dealing with documents or data where YAML is embedded within other formats.

### Example Usage:

```python
extracted_yaml = extract_yaml_block(AgentUtils.logger, yaml_string)
```

### Extraction Process:

- Utilizes a regular expression to identify and isolate YAML blocks within a given text, enabling the extraction of pure YAML content for further parsing or processing.


