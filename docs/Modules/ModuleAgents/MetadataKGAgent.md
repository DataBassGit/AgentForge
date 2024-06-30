from agentforge.utils.functions.ParsingUtils import parse_yaml_string

# MetadataKGAgent Documentation

## Introduction

The `MetadataKGAgent` class is an integral component of the **InjectKG** module, specializing in extracting and structuring metadata from textual content. This agent enhances knowledge graphs by providing detailed, contextual metadata, which significantly enriches the system's intelligence and data depth.

## Key Features

- **Metadata Extraction**: Analyzes text to identify and extract meaningful metadata, encapsulating essential information in a structured format.
- **YAML Format Parsing**: Parses and validates YAML-formatted output, ensuring consistency and reliability in metadata representation.
- **Error Logging**: Captures and logs parsing errors, providing clear feedback for debugging and error resolution.

## Method Overview: build_output

### Purpose

The `build_output` method enhances the base `Agent` functionality by specifically tailoring result parsing to handle YAML-formatted strings, converting them into structured data suitable for knowledge graph enhancement.

### Implementation Details

Upon execution, `build_output` performs the following actions:

- It parses the agent's raw result (YAML formatted) into structured data.
- It verifies the parsing integrity, capturing any parsing errors and logging them appropriately.

```python
def build_output(self):
    try:
        self.output = parse_yaml_string(self.functions.agent_utils.logger, self.result)
    except Exception as e:
        self.logger.parsing_error(self.result, e)
```

### Error Handling

- In case of parsing failures, the method logs detailed error messages and re-raises exceptions to indicate unsuccessful operations, ensuring transparency and maintainability.

## Usage Scenario: Enhancing Knowledge Graphs

`MetadataKGAgent` plays a vital role in extracting metadata to augment knowledge graphs. Its processing logic identifies key entities and relationships within a text, supplementing existing knowledge graph structures or initializing new ones with foundational metadata.

## Agent Intake Parameters

The agent is configured with specific prompts that guide its analysis and knowledge extraction process, these prompts are rendered with dynamic data:

- `existing_knowledge`: Presents the current state of the knowledge graph, which informs the agent's extraction strategy to avoid redundancy.
- `context`: Provides additional textual information that contextualizes the sentence for more nuanced metadata extraction.
- `sentence`: Specifies the text segment from which metadata should be extracted.

### Example Usage

Here's a simplistic example to demonstrate how `MetadataKGAgent` might be utilized in a workflow:

```python
# Assuming the agent is already initialized
context_paragraph = "The context providing background information."
sentence_to_analyze = "The sun emits light."
existing_knowledge = "Current knowledge graph entries."

# Agent processes the sentence to extract metadata
metadata = metadata_kg_agent.run(context=context_paragraph, 
                                sentence=sentence_to_analyze, 
                                existing_knowledge=existing_knowledge)

# Output contains structured metadata for knowledge graph integration
print(metadata)
```

## Conclusion

The `MetadataKGAgent` empowers developers to enrich knowledge bases with deep, contextual metadata, driving more intelligent and interconnected AI systems. By understanding and utilizing this agent, developers can enhance the robustness and depth of their knowledge graphs, ultimately facilitating more sophisticated data analyses and AI reasoning.