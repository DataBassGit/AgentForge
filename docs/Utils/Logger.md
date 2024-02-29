# Logging in AgentForge: `BaseLogger` and `Logger` Documentation

## Overview

The logging system in **AgentForge**, consisting of `BaseLogger` and `Logger` classes, provides a comprehensive framework for capturing and managing log messages across different components and modules. This document aims to help new developers understand and implement effective logging practices within their AgentForge-based projects.

## `BaseLogger` Class

The `BaseLogger` class sets up the foundation for file and console logging, allowing for messages to be logged at various levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) with support for multiple handlers.

### Key Features:

- File and Console Logging: Allows logging to specified files and the console, with configurable log levels.
- Dynamic Log Level Adjustment: Supports changing log levels at runtime to control the verbosity of log messages.
- Multiple Handlers: Manages different handlers for logging to various destinations.

### Initialization:

To initialize a `BaseLogger` instance, provide a logger name, log file, and initial log level:

```python
base_logger = BaseLogger(name='MyLogger', log_file='my_log.log', log_level='info')
```

## `Logger` Class

The `Logger` class acts as a wrapper, managing multiple `BaseLogger` instances tailored for different logging purposes, such as logging agent activities, model interactions, or system results.

### Key Features:

- Modular Logging: Facilitates separate log files for different aspects of the application, enhancing log organization.
- Convenience Methods: Provides methods for logging prompts, responses, and results, simplifying common logging tasks.

### Usage Example:

To utilize the `Logger` class for logging various messages, instantiate it and use the appropriate methods:

```python
logger = Logger(name='MyModule')

# Log a general informational message
logger.log("Starting application", 'info')

# Log a prompt to the model interaction logger
logger.log_prompt("What is the weather today?")

# Log a model response
logger.log_response("The weather is sunny")

# Log a critical error and raise an exception
logger.log("Critical system failure", 'critical')
```

## Logging a Message - Detailed Example:

To log a message using the `Logger` class, determine the appropriate log level and the logger type if necessary. Here is an example of logging an informational message and an error:

```python
# Logging an informational message
logger.log("This is an informational message", 'info')

# Logging an error message
logger.log("This is an error message", 'error')
```

The log messages will be directed to the configured log files and the console, according to the logger setup.

## Conclusion

Understanding and implementing the `BaseLogger` and `Logger` classes in **AgentForge** allows developers to maintain robust logging practices, crucial for monitoring application behavior, debugging issues, and ensuring transparency during execution.

By adhering to these logging conventions, developers can enhance the maintainability and observability of their **AgentForge** applications, ultimately leading to more reliable and user-friendly solutions.