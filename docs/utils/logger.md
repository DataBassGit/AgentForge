# Logger Utility Guide

## Introduction

The **Logger** utility in **AgentForge** provides a flexible and comprehensive system for capturing log messages across different modules. It allows you to:

1. Organize logs by categories or files (e.g., "agentforge", "model_io", "actions", etc.).  
2. Dynamically create new log files on-the-fly if they aren't defined in the system configuration.  
3. Control verbosity with various log levels (debug, info, warning, error, critical).  
4. Output logs to both console (with color-coded levels) and file (for auditing or later review).

---

## How It Works

### 1. `Logger` (High-Level Interface)

When you instantiate `Logger(name='Something')`, it reads from your system's logging settings and sets up a dictionary of underlying `BaseLogger` objects—one for each configured log file. If you attempt to log to a file that doesn't exist in your configuration, it automatically creates an entry in `system.yaml`, sets that file's level to `warning` by default, and saves the updated config.

**Example**:

```python
from agentforge.utils.logger import Logger

my_logger = Logger(name='MyModule', default_logger='mymodule') 
my_logger.log("Hello, world!", level='info')
```

### 2. `BaseLogger` (Behind the Scenes)

`BaseLogger` handles the actual creation of file and console handlers:

- **Console Handler**: Uses a `ColoredFormatter` to color-code log messages based on level.  
- **File Handler**: Writes logs to `<log_folder>/<log_file>.log` using the configured level and format.

**You typically don't create `BaseLogger` objects directly**. Instead, the `Logger` class handles it for you when you call `Logger(...).log(...)`.

---

## Setup and Configuration

### 1. `system.yaml` Example

Below is a snippet showing how logging might appear in your `system.yaml` under `settings.system.logging`. If a requested log file isn't listed, **AgentForge** dynamically adds it at level `warning`.

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
- **`folder`**: The directory where log files will be created.  
- **`files`**: A dictionary of log file "names" → default levels. For example, `agentforge: error` means that anything logged to the "agentforge" file will be written at `error` or above, unless updated at runtime.

### 2. Dynamic Creation of Log Files

If your code references a log file that doesn't exist in `files`, the system updates `system.yaml` and sets it to `warning` by default. This means you can do:

```python
logger.log("Hello from a brand-new log file!", logger_file='my_new_log', level='info')
```

…and the framework will:

1. Add `my_new_log` to `system.yaml` under `logging.files`.  
2. Set its level to `warning`.  
3. Save the updated config.  

---

## Basic Usage

1. **Instantiating a Logger**

```python
from agentforge.utils.logger import Logger

my_logger = Logger(name='DataProcessor', default_logger='dataprocess')
```

- **`name`**: A string typically matching your module or class. Shows up in log messages as `[DataProcessor] My message`.  
- **`default_logger`**: The default file you'll log to if you don't specify one. If it doesn't exist in `system.yaml`, it's created at `warning` level.

2. **Logging Messages**

```python
my_logger.log("An informational message", level='info')
my_logger.log("Something suspicious", level='warning')
my_logger.log("Detailed debugging info", level='debug', logger_file='model_io')
```

- **`level`** can be `debug`, `info`, `warning`, `error`, or `critical`.  
- **`logger_file`** (optional) overrides the default file for this message.

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
    data_logger = Logger(name='DataModule', default_logger='data_module')

    # 2. Log at different levels
    data_logger.info("Data processing started")
    data_logger.debug("Loaded 100 records from the database")
    data_logger.warning("Inconsistent formatting in record #57")

    # 3. Dynamically log to a new file
    data_logger.log("Something specialized", level='info', logger_file='special_data')

    # 4. Log a prompt/response scenario
    prompt = {"system": "You are an assistant.", "user": "Hello, assistant!"}
    data_logger.log_prompt(prompt)
    data_logger.log_response("Greetings, user!")

if __name__ == "__main__":
    main()
```

What happens behind the scenes:

- If `data_module` or `special_data` aren't in `system.yaml`, the logger updates `system.yaml` to include them (under `logging.files`) at `warning` level.  
- The relevant log messages go to `./logs/data_module.log` or `./logs/special_data.log` in addition to any console output if the level meets or exceeds the console threshold.

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

The updated Logger system in **AgentForge** lets you track and audit your agents' behavior with minimal setup. Developers can effortlessly create new log files at runtime, maintain separate logs for different components, and control verbosity on a per-file basis. This flexibility ensures you can keep your logs clean, relevant, and fully aligned with your application's needs.

---

**Need Help?**

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)  
- **Discord**: [Join our Discord Server](https://discord.gg/ttpXHUtCW6)
