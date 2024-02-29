# System YAML Configuration

This configuration file provides options for customizing the system according to your needs. Here is a map to guide you through each section of your `system.yaml` file. 

## System Configuration File

```yaml
Persona: default
OnTheFly: true
SaveMemory: true
TimeStampMemory: true

Logging:
  Enabled: true
  Folder: ./Logs
  Files:
    AgentForge: warning
    ModelIO: debug
    Results: warning

Paths:
  Files: ./Files
```
---

## Configuration Settings

- `Persona`: The default system persona. It's the name of the persona file located in the Persona folder. The default setting is the 'default' persona template.

- `OnTheFly`: A boolean setting that enables on-the-fly prompting. If set to `true`, the agent prompt YAML files can be updated in real time without needing to restart the system - an essential feature for quickly tweaking and debugging prompts.

- `SaveMemory`: This setting determines if the agents can save their results to the data store. By default, it's set to `true`. This is separate from the log files.

- `TimeStampMemory`: A boolean setting that controls whether each memory the agent saves to the datastore will have a timestamp associated with it.

---

## Logging Configuration and Usage

The logging system within **AgentForge** is designed to provide flexible and detailed logging capabilities. It is configurable through system settings, allowing for selective logging based on the developer's needs or system requirements.

### Configuration Settings

The logging behavior is controlled through the following settings:

- **`Enabled`**: Determines if logging is active. If set to `false`, logging will be disabled across the system.
  
- **`Folder`**: Defines the directory path, relative to the project root, where log files are stored. This path is used by the logger to organize log output.
  
- **`Files`**: Specifies the different log files to be generated, each with a designated purpose and log level. The default log files include:
  - **`AgentForge`**: Captures general system activities and events.
  - **`ModelIO`**: Records interactions between the system and models, such as prompts and responses.
  - **`Results`**: Logs the outcomes or results processed by the system.

### Log Levels

Each log file can be set to record messages at or above a specified severity level:

- **`debug`**: Captures detailed diagnostic information useful for debugging.
- **`info`**: Records general informational messages about system operations.
- **`warning`**: Indicates potential issues that are not immediately harmful.
- **`error`**: Logs serious issues that might prevent operation or lead to significant problems causing the process to terminate.
- **`critical`**: Records very severe error events that might cause the application to terminate.

### Directing Logs to Specific Files

Logs can be directed to specific files by specifying the file name (without the `.log` extension) as the last parameter in the logging method. For example, to log a model prompt at the debug level to the `ModelIO` log file:

```python
logger.log(f'Prompt:\n{prompt}', 'debug', 'ModelIO')
```

### Custom Log Files

Developers can define additional log files by adding entries to the `Files` configuration. Each new log file should have an associated log level. Logs can then be directed to any defined file using the method shown above, ensuring versatile and organized logging across different system components.

### Practical Implications

By leveraging these logging capabilities, developers can maintain a granular understanding of their system's operations, troubleshoot issues efficiently, and keep a record of significant events or decisions made by the application, fostering transparency and reliability.

---

## Paths Configuration

The `Paths` section in the **AgentForge** system configuration file allows you to specify directory paths that agents can interact with during their operation. These paths are crucial for enabling agents to read from and write to specific locations, enhancing their functionality and integration with external resources.

### Configuration Details

- **Relative Paths**: All paths defined in this section are be relative to the project root directory. This relative addressing ensures that your configurations are portable and consistent across different environments or deployment scenarios.

- **Unrestricted Quantity**: You can define as many paths as necessary for your project needs. This flexibility supports various use cases, from simple data logging to complex interactions involving multiple data sources or output directories.

- **Supported File Types**: Currently, the system is configured to allow agents to access text (.txt) and PDF (.pdf) files within these paths. This limitation focuses on the most common file types for text processing and document consumption.

- **Future Extensions**: Plans are in place to expand the supported file types to include other media, broadening the scope of agent capabilities and the types of data they can manipulate.

### Practical Use

Defining paths is particularly beneficial when leveraging [Tools & Actions](../ToolsAndActions/Overview.md) within **AgentForge**, as it provides agents with necessary access to interact with and manipulate files as part of their operational logic.

>**Note**: Ensure that the paths you provide are accessible and writable as required by your agent's operations to avoid runtime errors or access issues.