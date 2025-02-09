# System Settings Guide

The `system.yaml` file lies at the heart of **AgentForge**, configuring everything from persona usage to debugging and logging preferences. Understanding how to adjust these settings allows you to tailor the framework’s behavior to your specific requirements.

---

## Location

```
your_project_root/.agentforge/settings/system.yaml
```

All fields discussed here live under this single YAML file, which is loaded by the AgentForge `Config` class.

---

## Default `system.yaml` Structure

Below is the default structure you’ll find in `system.yaml`, with some sample values:

```yaml
# Persona settings
persona:
  enabled: true
  name: default

# Debug settings
debug:
  mode: false
  save_memory: false
  simulated_response: "Text to simulate an LLM response."

# Logging settings
logging:
  enabled: true
  console_level: warning
  folder: ./logs
  files:
    agentforge: error
    model_io: error

# Miscellaneous settings
misc:
  on_the_fly: true

# System file paths (Read/Write access)
paths:
  files: ./files
```

---

## Persona Settings

```yaml
persona:
  enabled: true
  name: default
```

- **`enabled`**  
  - **Type**: Boolean  
  - **Description**: Toggles whether agents should load persona files from `.agentforge/personas/`.  
  - **Default**: `true`  

- **`name`**  
  - **Type**: String  
  - **Description**: The default persona file name (without the `.yaml` extension) if an agent doesn’t specify its own.  
  - **Default**: `"default"`  

**How It Works**:  
When `enabled` is true, the system attempts to load a persona from `.agentforge/personas/<name>.yaml`. Agents can override this via a `Persona: custom_persona_name` field in their YAML prompt file if needed.

For a detailed explanation of how personas work, please refer to the **[Personas Guide](../Personas/Personas.md)**.

---

## Debug Settings

```yaml
debug:
  mode: false
  save_memory: false
  simulated_response: "Text to simulate an LLM response."
```

- **`mode`**  
  - **Type**: Boolean  
  - **Description**: Enables debug mode for the entire framework.  
  - **Behavior**: If `true`, agents skip real model calls and instead use `simulated_response`.  
  - **Default**: `false`  

- **`save_memory`**  
  - **Type**: Boolean  
  - **Description**: In debug mode, determines whether to save memory or any interaction data.  
  - **Default**: `false`  
  - **Note**: This setting can override normal behavior to avoid writing test data to storage.  

- **`simulated_response`**  
  - **Type**: String  
  - **Description**: A placeholder output used in debug mode instead of calling a real LLM.  
  - **Default**: `"Text to simulate an LLM response."`  

**When To Use**:  
- Set `debug.mode: true` during development or testing to iterate quickly without incurring real API calls.  
- Provide a custom `simulated_response` if you need your agent to parse something more structured, like JSON, or to test your agent’s parsing logic.

---

## Logging Settings

```yaml
logging:
  enabled: true
  console_level: warning
  folder: ./logs
  files:
    agentforge: error
    model_io: error
```

1. **`enabled`**  
   - **Type**: Boolean  
   - **Description**: Toggles whether AgentForge should write logs at all.  
   - **Default**: `true`  

2. **`console_level`**  
   - **Type**: String (one of `critical`, `error`, `warning`, `info`, `debug`)  
   - **Description**: Specifies the minimum severity level for logs to appear on the console.  
   - **Default**: `warning`  
   - **Behavior**: Messages below this level are hidden in the console output.  

3. **`folder`**  
   - **Type**: String  
   - **Description**: The path (relative to project root) where log files are stored.  
   - **Default**: `"./logs"`  

4. **`files`**  
   - **Type**: Dictionary  
   - **Description**: Defines multiple log files and their log levels. For instance:  
     - `agentforge: error` writes log messages of `error` level (and above) into `agentforge.log`.  
     - `model_io: error` sends logs to `model_io.log` for debugging LLM interactions.  

**Example**:

```yaml
logging:
  enabled: true
  console_level: info
  folder: ./MyLogs
  files:
    agentforge: debug
    model_io: warning
    actions: info
```

Logs are typically accessed through a `Logger` instance in your agents or system modules, e.g.:

```python
self.logger.log("A debug message", "debug", "agentforge")
```

---

## Miscellaneous Settings

```yaml
misc:
  on_the_fly: true
```

- **`on_the_fly`**  
  - **Type**: Boolean  
  - **Description**: Enables dynamic reloading of prompts and some configuration data without needing to restart the entire system.  
  - **Default**: `true`  

When `on_the_fly` is true, **AgentForge** will re-check YAML files for updates each time an agent runs. This is particularly helpful for prompt tweaking or minor configuration changes during iterative development.

---

## System File Paths

```yaml
paths:
  files: ./files
```

- **`files`**  
  - **Type**: String  
  - **Description**: Points to a directory where agents can read and write files.  
  - **Default**: `"./files"`  

In more advanced setups, you can extend the `paths` dictionary with additional directories (for instance, `paths.logs` or `paths.temp`). Agents will recognize these paths under `agent_data['settings']['system']['paths']`.

---

## Example Usage in an Agent

When you instantiate an agent, the system settings become available via:

```python
from agentforge.agent import Agent

class MyAgent(Agent):
    def process_data(self):
        sys_settings = self.agent_data['settings']['system']
        
        if sys_settings['debug']['mode']:
            # Use simulated_response for debugging
            pass
        
        if sys_settings['persona']['enabled']:
            # Persona-based logic
            pass

        # Access logs
        log_enabled = sys_settings['logging']['enabled']
        self.logger.log(f"Logging enabled: {log_enabled}", "info", "agentforge")
```

---

## Best Practices

1. **Use Debug Mode Sparingly**  
   Keep `debug.mode: false` in production to avoid bypassing real LLM calls.  
2. **Fine-Tune Logging**  
   Choose appropriate log levels for each file to avoid clutter and focus on what matters.  
3. **On-the-Fly During Development**  
   `misc.on_the_fly: true` is a major time-saver for rapid iteration. Turn it off if you need stable, unchanging configurations in a production environment.  
4. **Keep File Paths Organized**  
   Any directories you specify here should exist, or you’ll see errors if an agent tries to read/write to them.

---

## Conclusion

The `system.yaml` file gives you direct control over **AgentForge**’s persona management, debugging behaviors, logging outputs, and other core functions. By adjusting these settings, you can quickly adapt the framework to different development, testing, or production needs.

For more details about how system settings mesh with the rest of the configuration ecosystem (including model definitions and storage options), see our:

- [Settings Overview](Settings.md)  
- [Models Guide](Models.md)  
- [Storage Guide](Storage.md)
- [Personas Guide](../Personas/Personas.md)

---

**Need Help?**

If you have questions or need assistance, feel free to reach out:

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)  
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)