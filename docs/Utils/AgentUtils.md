# AgentUtils Documentation

## Introduction

`AgentUtils` is a class within the AgentForge framework that provides utility functions to support agent operations. These include loading agent-specific configurations, handling persona overrides, and parsing YAML strings. The class plays a pivotal role in configuring agents with their required settings and data.

## Loading Agent Data

The `load_agent_data` method is responsible for initializing an agent with its necessary configurations. It pulls information from several sources, including agent-specific overrides for personas and model settings.

### Example Usage:

```python
agent_utils = AgentUtils()
agent_data = agent_utils.load_agent_data('SampleAgent')
```

This function will set up `SampleAgent` with all its required settings, ready for it to perform its tasks. It handles several key aspects:

- Persona overrides, where it checks if an agent specifies a different persona from the default.
- API and model overrides, allowing an agent to use a different LLM API or model if specified.
- Combining default model settings with agent-specific overrides for model parameters.

## Setting Objectives

Agents can have specific objectives set, which guide their actions. The `prepare_objective` method allows users to input a custom objective or opt to use default settings.

### Example Usage:

```python
user_defined_objective = agent_utils.prepare_objective()
```

This prompts the user to define an objective. If the user provides an input, it sets that as the objective for the agent; otherwise, it retains the default objective.

## Parsing YAML Strings

`AgentUtils` provides functionality to parse strings in YAML format, which is often used in agent configuration files.

### Example Usage:

```python
yaml_content = agent_utils.parse_yaml_string(yaml_block)
```

The `parse_yaml_string` method takes a string formatted as a YAML block and parses it into a Python dictionary.
This is useful when agents need to interpret YAML content within strings,
such as agent responses, prompts or settings defined inline within text.

## Extracting YAML Blocks

To assist with parsing, the class includes a method to extract content from YAML blocks denoted by triple backticks (` ```yaml `).

### Example Usage:

```python
extracted_yaml = AgentUtils.extract_yaml_block(yaml_string)
```

This static method uses a regular expression to find and extract YAML content from a larger text block. It's particularly useful when dealing with markdown files or other documents where YAML blocks are embedded within other content.

---

For developers and users of the AgentForge framework, `AgentUtils` simplifies the process of setting up agents and ensures that they operate with the correct configurations. By handling overrides and parsing configurations, it allows for flexible and dynamic agent behavior within the system.

---