# `Agent` Super Class

---

## Overview
The `Agent` class serves as the superclass for all agent types in the framework. It handles core functionalities such as data loading, prompt generation, prompt execution, and more.

### Agent as a Default Template

The `Agent` super class serves as a default template for creating new agents. By providing basic functionalities and methods that can be overridden, it simplifies the process of defining specialized SubAgents. For more details on how to create SubAgents by extending this class, refer to the [SubAgents](SubAgentCreation.md) Page.

---

## Attributes
- `_agent_name`: Holds the name of the agent. If not explicitly provided, it defaults to the class name.
- `agent_data`: Contains data specific to the agent, loaded from storage.
- `storage`: Interface to the data storage component.

---

## Class Initialization

### `__init__(self, agent_name=None, log_level='info')`

**Purpose**: Initializes an instance of the `Agent` class. It sets up the agent name, data storage, and logging.

**Arguments**:
- `agent_name`: Optional. The name of the agent. Defaults to the class name if not provided.
- `log_level`: Optional. The logging level. Defaults to 'info'.

**Initialization Steps**:
1. If `agent_name` is not provided, use the class name as the agent name.
2. Load agent data using `self.functions.load_agent_data`.
3. Initialize data storage from `self.agent_data['storage']`.
4. Create a `Logger` instance and set its log level.

```python
    def __init__(self, agent_name=None, log_level="info"):
        """This function Initializes the Agent, it loads the relevant data depending on it's name as well as setting up the storage and logger"""
        if agent_name is None:
            self._agent_name = self.__class__.__name__

        self.functions = Functions()
        self.agent_data = self.functions.load_agent_data(self._agent_name)
        self.storage = self.agent_data['storage']

        self.logger = Logger(name=self._agent_name)
        self.logger.set_level(log_level)
```



---

## For Main Agent Methods

For a detailed walkthrough of the main methods in the `Agent` class that are essential for creating SubAgents, please refer to the [Agent Methods](AgentMethods.md) Page.


---