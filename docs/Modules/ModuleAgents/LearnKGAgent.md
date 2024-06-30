from agentforge.utils.functions.ParsingUtils import parse_yaml_string

# LearnKGAgent Documentation

## Introduction

The `LearnKGAgent` class extends the base `Agent` functionality within the AgentForge framework, specifically tailored to enhance knowledge graphs through text analysis. This agent is adept at parsing text to extract meaningful sentences that contribute new insights or foundational knowledge to a knowledge graph.

## Key Features

- **Text Analysis**: Employs advanced techniques to analyze text chunks and identify sentences with significant, new information.
- **Knowledge Extraction**: Focuses on extracting valuable sentences that augment the intelligence of AI systems via knowledge graph enhancement.
- **YAML Output Parsing**: Interprets the YAML-formatted output, ensuring structured and actionable knowledge extraction results.

## Agent Workflow

### build_output Method

The `LearnKGAgent` customizes the `build_output` method to parse its analysis results into a structured YAML format. This parsing facilitates the integration of extracted knowledge into a database or knowledge graph:

```python
def build_output(self):
    try:
        self.output = parse_yaml_string(self.functions.agent_utils.logger, self.result)
    except Exception as e:
        self.logger.parsing_error(self.result, e)
```

### Exception Handling

- If parsing fails, the agent logs the error, providing clarity on the issue and re-raising the exception to notify the calling process of the failure.

## Usage in LearnDoc Module

Within the LearnDoc module, `LearnKGAgent` plays a pivotal role in processing text files to extract and inject knowledge:

1. The agent receives chunks of text, each requiring careful analysis.
2. It applies its knowledge extraction logic to identify sentences that offer new or foundational knowledge.
3. The extracted sentences are formatted and returned for subsequent injection into the designated knowledge base.

## Agent Intake Parameters

The agent is configured with specific prompts that guide its analysis and knowledge extraction process, these prompts are rendered with dynamic data:

- `existing_knowledge`: Presents existing entries in the knowledge graph to inform the agent's extraction decisions.
- `text_chunk`: Supplies the text chunk to be analyzed for new knowledge.

## Practical Usage Example of LearnKGAgent

To effectively employ the `LearnKGAgent` within your data processing workflow, particularly in the context of the LearnDoc module, you can follow this example that demonstrates the agent's integration into the file processing pipeline:

After initializing the necessary components and defining the text chunk and knowledge graph context, `LearnKGAgent` can be invoked to analyze the text and compare it against existing knowledge:

```python
# Assume 'self.store' is an instance of StorageInterface with access to stored knowledge.
# 'text_chunk' is a portion of text extracted and pre-processed for analysis.

# Query existing knowledge graph entries related to the text chunk.
kg_results = self.store.storage_utils.query_memory(text_chunk)

# Run the LearnKGAgent with the chunk and the existing knowledge graph results.
data = self.learn_kg.run(text_chunk=text_chunk, existing_knowledge=kg_results)

# 'data' now contains the processed output from LearnKGAgent, which includes
# extracted knowledge and possibly reasons for each piece of extracted information.
```

In this scenario, `LearnKGAgent` performs the following steps:

1. Receives a text chunk (`text_chunk`) and existing knowledge graph data (`kg_results`) as inputs.
2. Analyzes the chunk in the context of the provided knowledge graph data to identify new or foundational knowledge.
3. Returns structured data (`data`) that encapsulates the extracted knowledge, ready for integration into the knowledge base.

This example demonstrates how `LearnKGAgent` interacts with a knowledge graph and processes textual data to enrich the knowledge base, enhancing the AI system's intelligence and context awareness.

By incorporating `LearnKGAgent` into your workflows, you can automate the enhancement of your knowledge graphs, ensuring your AI systems remain updated with relevant and substantial information extracted from an array of textual sources.

## Conclusion

`LearnKGAgent` is an essential component for any project aiming to intelligently analyze text and enhance knowledge graphs. Its integration within the LearnDoc module demonstrates a practical application, showcasing how text can be transformed into structured, actionable knowledge.