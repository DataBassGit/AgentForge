# Action Selection Agent

## Introduction

The `ActionSelectionAgent` extends the foundational `Agent` class with specialized capabilities for action selection based on current tasks and parameters. This agent showcases the flexibility of the agent framework by incorporating advanced error handling and dynamic action processing based on task-specific data.

Each instance of the `ActionSelectionAgent` is configured through a specific YAML file that dictates its interactions through predefined prompt templates. These templates are crucial for guiding the agent's behavior during execution. For details on prompt structure and usage, refer to the [Prompts Documentation](../../Agents/AgentPrompts.md). The specific prompts for the `ActionSelectionAgent` can be found in its [YAML](../../../src/agentforge/setup_files/agents/ModuleAgents/ActionSelectionAgent.yaml) file.

## Import Statements
```python
from agentforge.agent import Agent
```
This import statement allows the `ActionSelectionAgent` to inherit features and methods from the base `Agent` class, facilitating the use of foundational functionalities and enabling the extension for action selection tasks.

## Class Definition
```python
class ActionSelectionAgent(Agent):
    # Class body including new methods and overrides
```
The `ActionSelectionAgent` inherits from the `Agent` base class, leveraging and extending its core functionalities to accommodate specific needs related to action selection based on the analysis of tasks and other relevant parameters.

## Overridden and New Agent Methods

### Run
#### `run(**kwargs)`
Overrides the base `run` method with additional error handling to address scenarios where no relevant action is identified. This method emphasizes robustness in the agent's operation, ensuring graceful handling of exceptions.

### Load Additional Data
#### `load_additional_data()`
Enhances the agent's data loading capabilities by integrating action-related data specific to the agent's operational context. This method now includes a call to `load_actions`, demonstrating an advanced approach to data preparation.

### Load Actions
#### `load_actions()`
A new method dedicated to fetching actions from a storage system based on current tasks and predefined criteria. This method showcases the agent's ability to dynamically adapt its behavior based on external data sources.

### Process Data
#### `process_data()`
Extends the base method to incorporate custom logic for action processing, including a mechanism to halt execution if no suitable action is found. This method is integral to the agent's decision-making process, ensuring that actions align with the current task and agent's capabilities.

### Stop Execution on No Action
#### `stop_execution_on_no_action()`
Introduces a custom exception handling approach to terminate the agent's execution flow if no appropriate actions are available. This method underscores the agent's ability to make autonomous decisions based on the availability of viable actions.

### Parse Actions
#### `parse_actions()`
Processes and structures actions retrieved from storage, preparing them for further analysis or selection. This method reflects the agent's sophistication in handling complex data formats and extracting meaningful information.

### Format Actions
#### `format_actions()`
Transforms actions into a human-readable format, facilitating ease of understanding and further processing. This method exemplifies the agent's role in bridging raw data and actionable insights.

### Parse Result
#### `parse_result()`
Adapts the method to parse results from the LLM, converting YAML formatted strings into structured Python dictionaries. This override is crucial for integrating LLM outputs into the agent's decision-making framework.

### Save Result
#### `save_result()`
Customizes the behavior to bypass the default result-saving mechanism. This adaptation reflects the agent's focused use case, where persisting results to memory is not required.

### Build Output
#### `build_output()`
Crafts the final output by intelligently selecting an action based on the LLM's generated results. This method is a key component of the agent's output generation process, highlighting its ability to synthesize information and make decisions.

### Set Number of Results
#### `set_number_of_results(new_num_results)`
Allows dynamic adjustment of the number of results considered during action selection, offering flexibility in how the agent evaluates potential actions.

### Set Threshold
#### `set_threshold(new_threshold)`
Enables the modification of the threshold value used in action selection, illustrating the agent's adaptability in assessing the relevance of actions.

---

## How to Use

### Initialization
To instantiate the `ActionSelectionAgent`, import and initialize it as follows:
```python
from agentforge.agents.ActionSelectionAgent import ActionSelectionAgent
action_selection_agent = ActionSelectionAgent()
```

### Running the Agent
Invoke the agent's `run` method to perform action selection based on current tasks and parameters:
```python
selected_action = action_selection_agent.run()
```
This process leverages the agent's comprehensive method overrides and new functionalities to determine and execute the most appropriate action.

> **Note**: The `ActionSelectionAgent` represents a sophisticated use case of the agent framework, demonstrating the system's flexibility in supporting complex decision-making processes and dynamic data handling.

For those interested in the actual code, please see the [ActionSelection.py](../../../src/agentforge/agents/ActionSelectionAgent.py) file.

--- 
