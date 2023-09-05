# Summarization Agent

## Introduction

The `SummarizationAgent` is a specialized agent that extends from the base `Agent` class. It is designed to provide concise summaries of provided text or search results from stored memories. By employing the power of the base `Agent` class, it utilizes its inherent functionalities and augments them to cater to specific summarization requirements.

Each agent, including the `SummarizationAgent`, is associated with a specific prompt `JSON` file which determines its interactions. This file contains a set of pre-defined prompt templates that guide the agent's behavior during its execution. For a comprehensive understanding of how these prompts are structured and utilized, you can refer to our [Prompts Documentation](../Prompts/AgentPrompts.md). To view the specific prompts associated with the `SummarizationAgent`, see its [JSON File](../../../src/agentforge/utils/installer/agents/SummarizationAgent.json).

>**Important Note:** This agent is pending a rework!!!

---

## Import Statements

```python
from agentforge.agent import Agent
```

The `SummarizationAgent` imports its foundational `Agent` class from the `.agentforge/` directory. By doing so, it gets access to the core features and methods provided by the `Agent` class.

---

## Class Definition

```python
class SummarizationAgent(Agent):

    def run(self, **kwargs):
        # ...
        
    def get_search_results(self, text):
        # ...
```

The `SummarizationAgent` class inherits from the `Agent` base class. It takes advantage of the core functionalities of the `Agent` class while overriding two methods, `run` and `get_search_results`, tailored to the specific requirements of summarization.

---

## Agent Methods

### Run
#### `run(**kwargs)`

**Purpose**: This method fetches search results based on the provided query or, if no query is provided, retrieves the most recent memories. It then returns a summary of the retrieved text.

**Workflow**:
1. Calls the `get_search_results` method with the given `query`.
2. If results are found, passes them to the superclass's `run` method to obtain a summary.
3. Returns the summary.


```python
def run(self, **kwargs):
    text = self.get_search_results(kwargs['query'])
    if text is not None:
        summary = super().run(text=text)
        return summary
```

---

### Get Search Results
#### `get_search_results(text)`

**Purpose**: Searches the memory for results matching the provided text. If no results are found, it fetches the most recent memories.

**Workflow**:
1. Sets up the search parameters for the "Results" collection with the given text.
2. If no results are found, retrieves the most recent entries from the memory.
3. Returns the retrieved text.

```python
def get_search_results(self, text):
    params = {'collection_name': "Results", 'query': text}
    search_results = self.storage.query_memory(params, 5)['documents']

    if search_results == 'No Results!':
        search_results = self.storage.peek(params['collection_name'])['documents']

    text = None
    if search_results != 'No Results!':
        text = "\n".join(search_results[0])

    return text
```

---

## How to Use

### Initialization

To utilize the `SummarizationAgent`, begin by initializing it:

```python
from agentforge.agents.SummarizationAgent import SummarizationAgent
summarization_agent = SummarizationAgent()
```

### Running the Agent

The `SummarizationAgent` can be run with an optional `query` parameter:

```python
summary = summarization_agent.run(query=text)
```

In this example, the `query` parameter represents the text you wish to obtain a summary of. If not provided, the agent will automatically search for the most recent memories in its storage and return a summary of them. This functionality makes the `SummarizationAgent` versatile in summarizing both specific text and the latest stored information.

---