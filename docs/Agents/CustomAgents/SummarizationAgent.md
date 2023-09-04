# Summarization Agent

## Overview

The `SummarizationAgent` is a SubAgent designed to summarize text. It inherits its core functionalities from the [Agent](./Agent.md) superclass.

Curious about what a SubAgent is? Check out [SubAgents](./SubAgents.md).

---

## Class Definition

```python
from .agent import Agent

class SummarizationAgent(Agent):

    def run(self, **kwargs):
        # ...
        
    def get_search_results(self, text):
        # ...
```

## Overridden Methods

### `run(self, **kwargs)`

Overrides the superclass `run` method to include text summarization. Retrieves the text using `get_search_results` and then runs the parent method.

```python
def run(self, **kwargs):
    text = self.get_search_results(kwargs['query'])
    if text is not None:
        summary = super().run(text=text)
        return summary
```

---

### `get_search_results(self, text)`

Fetches search results based on the query. Returns the text to be summarized.

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

To utilize the `SummarizationAgent`, do this:

```python
summarization_agent = SummarizationAgent()
```
