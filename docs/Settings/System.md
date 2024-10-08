# System YAML Configuration

## Introduction

The `system.yaml` configuration file in **AgentForge** allows you to customize various system-level settings, including persona usage, storage options, logging, and accessible paths. This guide provides a concise explanation of each configuration option to help you tailor **AgentForge** to your needs.

---

## Default `system.yaml` Configuration

Here's the default `system.yaml` configuration file:

```yaml
# Persona Settings
PersonasEnabled: true
Persona: default

# Storage Settings
StorageEnabled: true
SaveMemory: true  # Requires StorageEnabled: true
ISOTimeStampMemory: true
UnixTimeStampMemory: true
PersistDirectory: ./DB/ChromaDB  # Relative path for persistent storage
DBFreshStart: true  # Wipes storage every time the system is initialized
Embedding: all-distilroberta-v1  # Embedding model for the vector database (ChromaDB)

# Misc. Settings
OnTheFly: true

# Logging Settings
Logging:
  Enabled: true
  Folder: ./Logs
  Files:
    AgentForge: debug
    ModelIO: debug
    Actions: debug
    Results: debug
    DiscordClient: error

# Paths the system (agents) have access to read and write
Paths:
  Files: ./Files
```

This file is located at:

```
your_project_root/.agentforge/settings/system.yaml
```

---

## Configuration Options Cheatsheet

| Setting                 | Type    | Description                                                                                           | Default                     |
|-------------------------|---------|-------------------------------------------------------------------------------------------------------|-----------------------------|
| **PersonasEnabled**     | Boolean | Enables or disables persona usage.                                                                    | `true`                      |
| **Persona**             | String  | Default persona name.                                                                                 | `'default'`                 |
| **StorageEnabled**      | Boolean | Enables or disables the storage system.                                                               | `true`                      |
| **SaveMemory**          | Boolean | Determines if agents save data to storage (requires `StorageEnabled: true`).                          | `true`                      |
| **ISOTimeStampMemory**  | Boolean | Includes ISO 8601 timestamps when saving data.                                                        | `true`                      |
| **UnixTimeStampMemory** | Boolean | Includes Unix timestamps when saving data.                                                            | `true`                      |
| **PersistDirectory**    | String  | Relative path for persistent storage.                                                                 | `'./DB/ChromaDB'`           |
| **DBFreshStart**        | Boolean | Wipes storage every time the system is initialized.                                                   | `true`                      |
| **Embedding**           | String  | Embedding model for the vector database (ChromaDB).                                                   | `'all-distilroberta-v1'`    |
| **OnTheFly**            | Boolean | Enables on-the-fly prompting (agents reload prompts without restart).                                 | `true`                      |
| **Logging**             | Section | Configures logging settings (enabled, folder, files, levels).                                          | See Logging Settings Below  |
| **Paths**               | Section | Specifies directories that agents can access.                                                         | See Paths Configuration     |

---

## Configuration Settings Explained

### 1. Persona Settings

#### **`PersonasEnabled`**

- **Type**: Boolean
- **Description**: Enables or disables the use of personas by agents.
- **Values**:
  - `true`: Agents can load and use persona data.
  - `false`: Agents won't access persona data.

#### **`Persona`**

- **Type**: String
- **Description**: Specifies the default persona to use when one isn't specified by an agent.
- **Usage**: Should match the name of a persona file in `.agentforge/personas/`.
- **Default**: `'default'`

### 2. Storage Settings

#### **`StorageEnabled`**

- **Type**: Boolean
- **Description**: Enables or disables the storage system.
- **Values**:
  - `true`: Agents can save and load data from storage.
  - `false`: Storage functionalities are disabled.

#### **`SaveMemory`**

- **Type**: Boolean
- **Description**: Determines if agents save their results or memory to the storage system.
- **Dependency**: Requires `StorageEnabled: true`.
- **Values**:
  - `true`: Agents save data to storage.
  - `false`: Agents do not save data to storage.

#### **`ISOTimeStampMemory`**

- **Type**: Boolean
- **Description**: Includes ISO 8601 timestamps when saving data.
- **Values**:
  - `true`: Data saved will include an ISO timestamp.
  - `false`: No ISO timestamp is included.

#### **`UnixTimeStampMemory`**

- **Type**: Boolean
- **Description**: Includes Unix timestamps when saving data.
- **Values**:
  - `true`: Data saved will include a Unix timestamp.
  - `false`: No Unix timestamp is included.

#### **`PersistDirectory`**

- **Type**: String
- **Description**: Relative path for persistent storage.
- **Usage**: Specifies where the vector database (ChromaDB) will store data.
- **Default**: `'./DB/ChromaDB'`

#### **`DBFreshStart`**

- **Type**: Boolean
- **Description**: Determines if the storage database is wiped clean each time the system is initialized.
- **Values**:
  - `true`: Wipes storage on initialization (useful for development).
  - `false`: Keeps existing data between sessions.

#### **`Embedding`**

- **Type**: String
- **Description**: Specifies the embedding model used by the vector database (ChromaDB).
- **Usage**: Choose an embedding model compatible with ChromaDB.
- **Default**: `'all-distilroberta-v1'`

### 3. Miscellaneous Settings

#### **`OnTheFly`**

- **Type**: Boolean
- **Description**: Enables or disables on-the-fly prompting.
- **Values**:
  - `true`: Agents can update their prompt template **YAML** files in real time without restarting the system.
  - `false`: Changes to prompt files require a system restart.

### 4. Logging Settings

The logging system provides flexible and detailed logging capabilities.

#### **`Logging.Enabled`**

- **Type**: Boolean
- **Description**: Enables or disables logging.
- **Values**:
  - `true`: Logging is active.
  - `false`: Logging is disabled.

#### **`Logging.Folder`**

- **Type**: String
- **Description**: Directory path (relative to the project root) where log files are stored.
- **Default**: `'./Logs'`

#### **`Logging.Files`**

- **Type**: Dictionary
- **Description**: Defines log files and their log levels.
- **Log Files and Levels**:
  - **`AgentForge`**: `'debug'` - General system activities.
  - **`ModelIO`**: `'debug'` - Interactions with LLMs.
  - **`Actions`**: `'debug'` - Agent actions and tool usage.
  - **`Results`**: `'debug'` - Generic log for custom use.
  - **`DiscordClient`**: `'error'` - Logs for Discord client integration.

#### Directing Logs to Specific Files

Use the `logger.log` method with the file name to direct logs:

```python
logger.log('This is a debug message.', 'debug', 'ModelIO')
```

#### Custom Log Files

Add custom log files by extending the `Files` section:

```yaml
Files:
  AgentForge: debug
  CustomLog: info
```

Then log to it in your code:

```python
logger.log('Custom log message.', 'info', 'CustomLog')
```

### 5. Paths Configuration

#### **`Paths.Files`**

- **Type**: String
- **Description**: Directory path (relative to the project root) where agents can access files.
- **Default**: `'./Files'`

#### Usage Notes

- **Relative Paths**: Ensure paths are relative to the project root.
- **File Access**: Agents can read and write to the specified paths.
- **Supported File Types**: Currently supports text (`.txt`) and PDF (`.pdf`) files.

---

## Example Usage in Agents

Agents can access these settings through `self.agent_data['settings']['system']`.

**Example**:

```python
from agentforge.agent import Agent

class MyAgent(Agent):
    def load_additional_data(self):
        system_settings = self.agent_data['settings']['system']
        
        # Check if storage is enabled
        if system_settings['StorageEnabled']:
            # Perform storage-related operations
            pass

        # Access default persona
        if system_settings['PersonasEnabled']:
            default_persona = system_settings['Persona']
            # Use persona data as needed
```

---

## Best Practices

- **Keep `DBFreshStart` as `false` in production** to preserve data between sessions.
- **Use `OnTheFly: true` during development** for quick prompt iteration.
- **Set appropriate log levels** in `Logging.Files` to control verbosity.
- **Ensure paths are correct** and accessible by your agents.

---

## Conclusion

By configuring the `system.yaml` file, you can fine-tune **AgentForge** to suit your project's requirements. Understanding these settings allows you to optimize performance, manage storage effectively, and customize agent behaviors.

---

**Need Help?**

If you have questions or need assistance, feel free to reach out:

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)

---
