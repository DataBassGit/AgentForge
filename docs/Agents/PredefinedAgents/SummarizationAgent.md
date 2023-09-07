# Summarization Agent

## Introduction

The `SummarizationAgent` is a specialized agent that extends from the base `Agent` class. Its primary function is to generate concise summaries based on provided text or to retrieve and summarize search results from stored memories. Building upon the foundation provided by the base `Agent` class, it augments the core functionalities to cater to the specific requirements of summarization.

Each agent, including the `SummarizationAgent`, is associated with a specific prompt `JSON` file which determines its interactions. This file contains a set of pre-defined prompt templates that guide the agent's behavior during its execution. For a comprehensive understanding of how these prompts are structured and utilized, you can refer to our [Prompts Documentation](../Prompts/AgentPrompts.md). To view the specific prompts associated with the `SummarizationAgent`, see its [JSON File](../../../src/agentforge/utils/installer/agents/SummarizationAgent.json).

---

## Import Statements

```python
from agentforge.agent import Agent
```

The `SummarizationAgent` imports the foundational `Agent` class from the `.agentforge/` directory, thereby gaining access to its core features and methods.

---

## Class Definition

```python
class SummarizationAgent(Agent):

    def run(self, text=None, query=None):
        # ...

    def run_query(self, query):
        # ...

    def get_search_results(self, text):
        # ...

    def summarize(self, text):
        # ...
```

The `SummarizationAgent` class inherits from the `Agent` base class. While it leverages the core functionalities of the `Agent` class, it also introduces new methods like `run_query` and `summarize`, tailored to its specific needs.

---

## Agent Methods

### Run
#### `run(text=None, query=None)`

**Purpose**: Depending on the provided parameters, the method either summarizes the given text directly or, if a query is provided, searches the memory for relevant results and summarizes them.

**Workflow**:
1. If `query` is provided, it calls the `run_query` method.
2. If `text` is provided, it directly calls the `summarize` method.
3. Returns the summarized text.

```python
def run(self, text=None, query=None):
    if query:
        return self.run_query(query)
    else:
        return self.summarize(text)
```

---

### Run Query
#### `run_query(query)`

**Purpose**: Fetches search results based on the provided query and summarizes them.

**Workflow**:
1. Calls the `get_search_results` method with the given `query`.
2. If results are found, calls the `summarize` method.
3. Returns the summarized text.

```python
def run_query(self, query):
    text = self.get_search_results(query)
    if text:
        return self.summarize(text)
```

---

### Get Search Results
#### `get_search_results(text)`

**Purpose**: Searches the memory for results similar to the provided query. If no results are found, it fetches the most recent memories.

**Workflow**:
1. Sets up the search parameters for the "Results" collection with the given text.
2. *If no results are found, retrieves the most recent entries from the memory.* (Not Implemented due to pending rework)
3. Returns the retrieved text.

```python
def get_search_results(self, query):
    params = {'collection_name': "Results", 'query': query}
    search_results = self.storage.query_memory(params, 5)['documents']

    # Rework Pending: ChromaDB updated how their collections work breaking this code, 
    # it used to look at most recent items now it always looks at the first 5
    # if search_results == 'No Results!': search_results = 
    # self.storage.peek(params['collection_name'])['documents']

    text = None
    if search_results != 'No Results!':
        text = "\n".join(search_results[0])

    return text
```

 >**NOTE**: This method currently does not retrieve any memories if no results are found due to recent Chroma DB update, a rework is pending.

---

### Summarize
#### `summarize(text)`

**Purpose**: Generates a concise summary of the provided text.

**Workflow**:
1. Calls the superclass's `run` method with the provided text.
2. Returns the summary.

```python
def summarize(self, text):
    # Simply summarize the given text
    return super().run(text=text)
```

---

## How to Use

### Initialization

To utilize the `SummarizationAgent`, you should first initialize it:

```python
from agentforge.agents.SummarizationAgent import SummarizationAgent
summarization_agent = SummarizationAgent()
```

### Running the Agent

The `SummarizationAgent` can be run in two modes:

1. Direct Summarization:

```python
summary = summarization_agent.run(text="Your text here...")
```

2. Summarization based on Query:

```python
summary = summarization_agent.run(query="Your query here...")
```

Whether you're providing a direct text or a query, the `SummarizationAgent` is engineered to deliver precise and relevant summaries, making it a versatile tool in the framework.

---