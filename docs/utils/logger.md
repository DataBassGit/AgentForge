# Logger Utility Guide

## Introduction

The **Logger** utility in **AgentForge** provides a flexible and comprehensive system for capturing log messages across different modules. It allows you to:

1. Organize logs by categories or files (e.g., "agentforge", "model_io", "actions", etc.).  
2. Route unconfigured log categories through a configured fallback without changing consumer configuration.
3. Control verbosity with various log levels (debug, info, warning, error, critical).  
4. Output logs to both console (with color-coded levels) and file (for auditing or later review).

---

## How It Works

### 1. `Logger` (High-Level Interface)

When you instantiate `Logger(name='Something')`, it reads from your system's logging settings and sets up standard Python logging handlers for the configured log files. If code asks for a category that is not configured, AgentForge logs through the configured fallback category instead of editing `system.yaml`.

**Example**:

```python
from agentforge.utils.logger import Logger

my_logger = Logger(name='MyModule', default_logger='mymodule') 
my_logger.log("Hello, world!", level='info')
```

### 2. `BaseLogger` (Behind the Scenes)

`BaseLogger` handles the actual creation of file and console handlers:

- **Console Handler**: Uses a `ColoredFormatter` to color-code log messages based on level.  
- **File Handler**: Writes configured categories to `<project_root>/<log_folder>/<log_file>.log` when `logging.folder` is relative.

**You typically don't create `BaseLogger` objects directly**. Instead, the `Logger` class handles it for you when you call `Logger(...).log(...)`.

---

## Setup and Configuration

### 1. `system.yaml` Example

Below is a snippet showing how logging might appear in your `system.yaml` under `settings.system.logging`.

```yaml
logging:
  enabled: true
  console_level: warning
  folder: ./logs
  files:
    agentforge: error
    model_io: debug
```

- **`enabled`**: Set to `false` to disable logging globally.  
- **`console_level`**: Minimum severity level to show in console logs (one of `debug`, `info`, `warning`, `error`, `critical`).  
- **`folder`**: The directory where log files will be created. Relative paths resolve under the active AgentForge project root.
- **`files`**: A dictionary of log file "names" → minimum levels. Only listed names get dedicated log files.

### 2. Unconfigured Categories

If code references a log file that doesn't exist in `files`, AgentForge does not update `system.yaml` and does not create a new category file. The message is routed to the configured fallback category, usually `agentforge`:

```python
logger.log("Flow diagnostics", logger_file='Flow', level='debug')
```

With the default setup, that message writes to `logs/agentforge.log` because `Flow` is not listed in `logging.files`.

---

## Basic Usage

1. **Instantiating a Logger**

```python
from agentforge.utils.logger import Logger

my_logger = Logger(name='DataProcessor', default_logger='dataprocess')
```

- **`name`**: A string typically matching your module or class. Shows up in log messages as `[DataProcessor] My message`.  
- **`default_logger`**: The preferred category when you don't specify one. If it is not listed in `logging.files`, AgentForge falls back to `agentforge` or the first configured category.

2. **Logging Messages**

```python
my_logger.log("An informational message", level='info')
my_logger.log("Something suspicious", level='warning')
my_logger.log("Detailed debugging info", level='debug', logger_file='model_io')
```

- **`level`** can be `debug`, `info`, `warning`, `error`, or `critical`.  
- **`logger_file`** (optional) overrides the default file for this message.
- Unsupported levels raise `ValueError` instead of silently becoming `info`.

---

## Advanced Methods

### 1. Level-Specific Helpers

For convenience, `Logger` provides shortcuts:

```python
my_logger.debug("Debug details")
my_logger.info("General information")
my_logger.warning("Potential problem")
my_logger.error("An error occurred")
my_logger.critical("Critical failure!")
```

### 2. Logging Prompts and Responses

Specifically designed for model interactions, these two methods log content at `debug` level in the `model_io` file:

- **`log_prompt(model_prompt: dict)`**  
  Expects a dictionary with `system` and `user` keys.  
  ```python
  my_logger.log_prompt({'system': "System text", 'user': "User text"})
  ```

- **`log_response(response: str)`**  
  Logs the raw response from the model.  
  ```python
  my_logger.log_response("Model replied with some content")
  ```

### 3. Handling Parsing Errors

When you parse a model response but encounter an exception, call:

```python
my_logger.parsing_error(model_response, error)
```

It logs both the response content and the exception at `error` level.

---

## Usage Within Agents

If you're building a **custom agent** (subclassing `Agent`), you already have a logger via `self.logger`. For instance:

```python
from agentforge.agent import Agent

class MyAgent(Agent):
    def process_data(self):
        self.logger.debug("Processing data in MyAgent")
        # ...
```

No need to instantiate a new `Logger`. This ensures logs are routed correctly and adopt the same config.

---

## Example: Putting It All Together

```python
from agentforge.utils.logger import Logger

def main():
    # 1. Instantiate a Logger for our module
    data_logger = Logger(name='DataModule', default_logger='agentforge')

    # 2. Log at different levels
    data_logger.info("Data processing started")
    data_logger.debug("Loaded 100 records from the database")
    data_logger.warning("Inconsistent formatting in record #57")

    # 3. Log to another configured category
    data_logger.log("Detailed model diagnostic", level='debug', logger_file='model_io')

    # 4. Log a prompt/response scenario
    prompt = {"system": "You are an assistant.", "user": "Hello, assistant!"}
    data_logger.log_prompt(prompt)
    data_logger.log_response("Greetings, user!")

if __name__ == "__main__":
    main()
```

What happens behind the scenes:

- Configured categories write to their own log files under the active project root.
- Unconfigured categories fall back to `agentforge` or the first configured category and leave `system.yaml` unchanged.
- Console output appears when the message meets or exceeds `console_level`.

---

## Best Practices

1. **Meaningful Logger Names**  
   Use the module or class name for clarity. For additional categories, pass `logger_file` as needed.  
2. **Choose Appropriate Levels**  
   - `debug`: Fine-grained informational events for diagnosing problems.  
   - `info`: General operational messages.  
   - `warning`: Indications of potential issues.  
   - `error`: Serious issues that need attention.  
   - `critical`: Severe errors that might force the application to stop.  
3. **Use `self.logger` in Agents**  
   Rely on the pre-initialized logger from the base `Agent` class rather than creating a new one.  
4. **Mind Sensitive Data**  
   Avoid logging API keys, personally identifiable info, or other sensitive content.  
5. **Console vs. File**  
   By default, console logs follow `console_level` from `system.yaml`. If you see too many messages in your console, raise that level to `info` or `warning`.

---

## Conclusion

The Logger system in **AgentForge** lets you track and audit your agents' behavior with minimal setup. Configure dedicated categories in `system.yaml` when you want separate files, and rely on fallback routing for incidental diagnostic categories.

---

**Need Help?**

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)  
- **Discord**: [Join our Discord Server](https://discord.gg/ttpXHUtCW6)
