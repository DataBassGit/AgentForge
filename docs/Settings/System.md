# System YAML Configuration

## Introduction

The `system.yaml` configuration file in **AgentForge** allows you to customize various system-level settings, including persona usage, storage options, logging, and accessible paths. This guide provides a detailed explanation of each configuration option to help you tailor **AgentForge** to your needs.

---

## System Configuration File

Here's the default `system.yaml` configuration file:

```yaml
# Persona Settings
PersonasEnabled: true
Persona: default

# Storage Settings
StorageEnabled: true
SaveMemory: true  # Saving Memory won't work if Storage is disabled
ISOTimeStampMemory: true
UnixTimeStampMemory: true

# Misc. Settings
OnTheFly: true

# Logging Settings
Logging:
  Enabled: true
  Folder: ./Logs
  Files:
    AgentForge: error
    ModelIO: error
    Actions: error
    Results: error
    DiscordClient: error

# Paths the system (agents) have access to read and write
Paths:
  Files: ./Files
```

This file can be found at `your_project_root/.agentforge/settings/system.yaml`

---

## Configuration Options Cheatsheet

| Setting                 | Type    | Description                                                                                   | Default     |
|-------------------------|---------|-----------------------------------------------------------------------------------------------|-------------|
| **PersonasEnabled**     | Boolean | Enables or disables persona usage.                                                            | `true`      |
| **Persona**             | String  | Default persona name.                                                                         | `'default'` |
| **StorageEnabled**      | Boolean | Enables or disables the storage system.                                                       | `true`      |
| **SaveMemory**          | Boolean | Determines if agents save data to storage (requires `StorageEnabled: true`).                  | `true`      |
| **ISOTimeStampMemory**  | Boolean | Includes ISO 8601 timestamps when saving data.                                                | `true`      |
| **UnixTimeStampMemory** | Boolean | Includes Unix timestamps when saving data.                                                    | `true`      |
| **OnTheFly**            | Boolean | Enables on-the-fly prompting (agents reload prompts without restart).                         | `true`      |
| **Logging**             | Section | Configures logging settings (enabled, folder, files, levels).                                  | See below   |
| **Paths**               | Section | Specifies directories that agents can access.                                                 | See below   |

---


## Configuration Settings Explained

### 1. Persona Settings

Personas allow agents to access predefined information or characteristics defined in persona files. These settings control the usage of personas in the system.

- **`PersonasEnabled`**: (Boolean) Enables or disables the use of personas by agents.
  - **`true`**: Agents can load and use persona data.
  - **`false`**: Persona loading is disabled; agents won't access persona data.

- **`Persona`**: (String) Specifies the default persona to use when one isn't specified by an agent.
  - The value should match the name of a persona file located in the `.agentforge/personas/` directory.
  - Default value is `'default'`.

### 2. Storage Settings

These settings control how agents save and manage their memory or data during operation.

- **`StorageEnabled`**: (Boolean) Enables or disables the storage system.
  - **`true`**: Agents can save data to the storage system.
  - **`false`**: Storage functionalities are disabled.

- **`SaveMemory`**: (Boolean) Determines if agents save their results or memory to the storage system.
  - **`true`**: Agents save data to storage (only if `StorageEnabled` is `true`).
  - **`false`**: Agents do not save data to storage.

  **Note**: `SaveMemory` has no effect if `StorageEnabled` is `false`.

- **`ISOTimeStampMemory`**: (Boolean) When saving data, includes an ISO 8601 timestamp.
  - **`true`**: Data saved will include a timestamp in ISO format.
  - **`false`**: No ISO timestamp is included.

- **`UnixTimeStampMemory`**: (Boolean) When saving data, includes a Unix timestamp.
  - **`true`**: Data saved will include a Unix timestamp.
  - **`false`**: No Unix timestamp is included.

### 3. Miscellaneous Settings

- **`OnTheFly`**: (Boolean) Enables or disables on-the-fly prompting.
  - **`true`**: Agents can update their prompt **YAML** files in real time without restarting the system. Useful for quick tweaking and debugging of prompts.
  - **`false`**: Changes to prompt files require a system restart to take effect.

### 4. Logging Settings

The logging system in **AgentForge** provides flexible and detailed logging capabilities. You can configure which logs are generated, their levels, and where they are stored.

#### Configuration Options

- **`Enabled`**: (Boolean) Enables or disables logging.
  - **`true`**: Logging is active.
  - **`false`**: Logging is disabled across the system.

- **`Folder`**: (String) Specifies the directory path (relative to the project root) where log files are stored.
  - Default is `'./Logs'`.

- **`Files`**: (Dictionary) Defines the log files to generate, with their associated log levels.
  - **Log Files**:
    - **`AgentForge`**: General system activities.
    - **`ModelIO`**: Interactions between the system and LLMs (prompts and model responses).
    - **`Actions`**: Logs related to agent actions and tool usage.
    - **`Results`**: A generic log for users to use at their discretion, not currently in use by the system.
    - **`DiscordClient`**: Specific logs for the Discord client integration.
  - **Log Levels**: Each log file can be set to record messages at or above a specified severity level:
    - **`debug`**, **`info`**, **`warning`**, **`error`**, **`critical`**.

#### Directing Logs to Specific Files

When logging within your agents or system components, you can direct logs to specific files by specifying the file name in the logging method.

**Example**:

```python
logger.log('This is a debug message.', 'debug', 'ModelIO')
```

This will write the message to the `ModelIO` log file if the log level is `debug` or higher.

#### Custom Log Files

You can define additional log files by adding entries to the `Files` section.

**Example**:

```yaml
Files:
  AgentForge: debug
  ModelIO: debug
  Actions: debug
  Results: debug
  DiscordClient: error
  CustomLog: info
```

You can then log to `CustomLog` in your code:

```python
logger.log('This is a custom log message.', 'info', 'CustomLog')
```

### 5. Paths Configuration

The `Paths` section defines directories that agents can read from and write to during their operation.

- **`Files`**: (String) Specifies the directory path (relative to the project root) where agents can access files.
  - Default is `'./Files'`.

#### Usage Notes

- **Relative Paths**: Paths are relative to the project root directory, ensuring portability across different environments.
- **File Access**: Agents can read and write to the specified paths, enabling them to interact with external resources or data as part of their operations.
- **Supported File Types**: Currently, agents can access text (`.txt`) and PDF (`.pdf`) files within these paths.
  - Future updates may expand supported file types.

---

## Example Usage in Agents

Agents can access these settings through the `agent_data['settings']` variable.

**Example**:

```python
class MyAgent(Agent):
    def load_additional_data(self):
        # Check if storage is enabled
        if self.agent_data['settings']['system']['StorageEnabled']:
            # Perform storage-related operations
            pass

        # Access default persona
        if self.agent_data['settings']['system']['PersonasEnabled']:
            default_persona = self.agent_data['settings']['system']['Persona']
            # Modify or use persona data
```

Note: The default `Agent` Class already handles the settings for `Personas` and `Storage`, this is simply an example of how users can access the system settings.

---

## Conclusion

By updating the `system.yaml` configuration file, you can fine-tune how **AgentForge** operates at a system level. Understanding each setting allows you to optimize performance, enhance security, and tailor the framework to your specific needs.

---

**Need Help?**

If you have questions or need assistance, feel free to reach out:

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)
