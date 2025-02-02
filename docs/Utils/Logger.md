# Logger Utility Guide

## Introduction

The `Logger` utility in **AgentForge** provides a flexible and comprehensive logging system for developers. It allows you to capture and manage log messages across different components and modules, facilitating easier debugging, monitoring, and maintenance of your applications.

---

## Overview

The logging system consists of two main classes:

- **`BaseLogger`**: Sets up the foundational logging to files and the console with support for different log levels.
- **`Logger`**: Acts as a wrapper that manages multiple `BaseLogger` instances, allowing for modular and organized logging across various parts of your application.

---

## Key Features

- **Modular Logging**: Create separate log files for different aspects of your application (e.g., agent activities, model interactions).
- **Flexible Log Levels**: Control the verbosity of logs by setting different log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).
- **Console and File Logging**: Output logs to the console for immediate feedback and to files for persistent records.
- **Dynamic Configuration**: Loggers are configured based on the settings specified in the `system.yaml` file.

---

## Using the Logger

### Initialization

To use the `Logger`, you typically create an instance of it in your module or component:

```python
from agentforge.utils.logger import Logger

# Initialize the logger with the name of your module or component
logger = Logger(name='MyModule')
```

**Note:** If you are working within a custom agent and overriding methods, you do **not** need to initialize the logger, as the `Agent` base class already provides a logger instance accessible via `self.logger`.

---

### Basic Logging

You can log messages at various levels using the `log` method:

```python
# Log an informational message
logger.log("This is an informational message.", level='info')

# Log a debug message
logger.log("Debugging details here.", level='debug')

# Log a warning
logger.log("This is a warning message.", level='warning')

# Log an error
logger.log("An error occurred.", level='error')

# Log a critical error
logger.log("Critical failure!", level='critical')
```

**Note:** The `level` parameter can be one of `'debug'`, `'info'`, `'warning'`, `'error'`, or `'critical'`.

---

### Logging within Custom Agents

When developing custom agents by subclassing the `Agent` class, you have access to the logger via `self.logger`. There's no need to initialize a new `Logger` instance.

**Example:**

```python
from agentforge.agent import Agent

class MyCustomAgent(Agent):
    def process_data(self):
        # Log an informational message
        self.logger.log("Processing data...", level='info')

    def parse_result(self):
        # Log a debug message
        self.logger.log("Parsing result...", level='debug')
```

By using `self.logger`, your logs will be properly managed according to the system configurations and integrated seamlessly with the rest of the logging system.

---

## Configuration in `system.yaml`

The `Logger` utility relies on the `system.yaml` configuration file to determine logging behavior.

**Example Logging Configuration:**

```yaml
Logging:
  Enabled: true
  Folder: ./Logs
  Files:
    AgentForge: info
    ModelIO: debug
    Actions: warning
    Results: info
    DiscordClient: error
```

- **`Enabled`**: Set to `true` to enable logging.
- **`Folder`**: Specifies where log files are stored.
- **`Files`**: Defines log files and their corresponding log levels.
### Logging to Specific Log Files

The `Logger` can direct logs to different log files based on the `logger_file` parameter, which corresponds to the log files specified in your `system.yaml` configuration.

**Example of logging to a specific file:**

```python
# Log a message to the 'ModelIO' log file
logger.log("Model input/output details.", level='info', logger_file='ModelIO')

# In a custom agent, using self.logger
self.logger.log("Agent performed an action.", level='debug', logger_file='Actions')
```

---

### Logging Prompts and Responses

The `Logger` provides convenience methods for logging prompts and responses, particularly useful when working with language models.

**Logging a Prompt:**

```python
model_prompt = {
    'System': "You are an assistant.",
    'User': "What is the weather today?"
}

# If using logger instance
logger.log_prompt(model_prompt)

# In a custom agent
self.logger.log_prompt(model_prompt)
```

This logs the system and user prompts to the `ModelIO` log file.

**Logging a Model Response:**

```python
response = "The weather today is sunny with a high of 75 degrees."

# If using logger instance
logger.log_response(response)

# In a custom agent
self.logger.log_response(response)
```

This logs the model's response to the `ModelIO` log file.

---

### Logging Parsing Errors

When parsing responses from models, you might encounter errors. The `Logger` provides a method to log these parsing errors along with the problematic response.

```python
try:
    # Code that might raise a parsing error
    parsed_response = parse_model_response(response)
except Exception as e:
    # If using logger instance
    logger.parsing_error(response, e)
    
    # In a custom agent
    self.logger.parsing_error(response, e)
```

This logs detailed information about the parsing error to help you debug the issue.

---

### Logging Informational Messages

For important messages that you want to log and display prominently, you can use the `log_info` method:

```python
# If using logger instance
logger.log_info("Operation completed successfully.")

# In a custom agent
self.logger.log_info("Operation completed successfully.")
```

This method logs the message and prints it to the console in a highlighted format.

---

## Best Practices

- **Use `self.logger` in Custom Agents**: When working within agents, use `self.logger` to log messages. There's no need to initialize a new logger.
- **Consistent Naming**: Use meaningful names when initializing the `Logger` to identify the source of log messages easily.
- **Appropriate Log Levels**: Choose the correct log level to avoid cluttering logs with unnecessary information.
  - Use `debug` for detailed diagnostic information.
  - Use `info` for general operational messages.
  - Use `warning` for recoverable issues.
  - Use `error` for serious problems that need attention.
  - Use `critical` for severe errors that may cause the application to terminate.
- **Sensitive Information**: Avoid logging sensitive data such as API keys, passwords, or personal user information.

---

## Example: Putting It All Together

```python
from agentforge.agent import Agent


class MyCustomAgent(Agent):
  def load_data(self, **kwargs):
    super().load_data(**kwargs)
    self.logger.log("Data loaded successfully.", level='info')

  def process_data(self):
    try:
      # Processing data
      self.logger.log("Processing data...", level='debug')
      # Simulate data processing
      self.template_data['processed'] = self.template_data.get('raw_data', '').upper()
    except Exception as e:
      self.logger.log(f"An error occurred during data processing: {e}", level='error')

  def parse_result(self):
    try:
      # Parsing result
      self.logger.log("Parsing result...", level='debug')
      # Simulate result parsing
      self.template_data['parsed_result'] = self.result.lower()
    except Exception as e:
      self.logger.parsing_error(self.result, e)

  def build_output(self):
    self.output = f"Processed Output: {self.template_data.get('parsed_result', '')}"
    self.logger.log_info("Output built successfully.")


# Instantiate and run the agent
agent = MyCustomAgent()
agent.run(raw_data="Sample Input Data")
print(agent.output)
```

**Expected Logging Behavior:**

- Logs informational messages about data loading and output building.
- Logs debug messages for data processing and result parsing.
- Uses `self.logger` throughout, leveraging the built-in logger from the `Agent` base class.

---

## Conclusion

The `Logger` utility in **AgentForge** empowers developers with a robust and flexible logging system. By integrating it into your applications and utilizing `self.logger` within custom agents, you can enhance debugging, monitor application behavior, and maintain comprehensive records of your system's operations.

---

**Need Help?**

If you have questions or need assistance, feel free to reach out:

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)

---
