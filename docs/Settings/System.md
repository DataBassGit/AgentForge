# System Settings Guide

`system.yaml` is loaded from the project's `.agentforge/settings/system.yaml` and exposed via `Config().data['settings']['system']`.

## Location

```
<project_root>/.agentforge/settings/system.yaml
```

## Schema Overview

```yaml
persona:
  enabled: true       # Load persona files from .agentforge/personas/
  name: default       # Default persona filename (without .yaml)

debug:
  mode: false         # If true, uses simulated_response instead of real LLM calls
  save_memory: false  # In debug mode, whether to write memory to storage
  simulated_response: "Text designed to simulate an LLM response for debugging purposes"

logging:
  enabled: true                 # Toggle all logging on or off
  console_level: warning        # Minimum severity for console output
  folder: ./logs                # Relative folder for log files
  files:                        # Per-logger file-level overrides
    agentforge: error
    model_io: error

misc:
  on_the_fly: true   # Reload YAML configs at runtime for dynamic updates

paths:
  files: ./files     # Read/write directory available to agents
```

### persona
- **enabled** (bool): Toggle persona loading. Default `true`.
- **name** (string): Persona filename (no `.yaml`). Default `default`.
- Behavior: When enabled, `Config` loads `.agentforge/personas/<name>.yaml`. Agents can override via their own `personas` key.

### debug
- **mode** (bool): Enable debug mode to bypass real LLM calls.
- **save_memory** (bool): If debug mode is on, decide whether to persist memory during tests.
- **simulated_response** (string): Text returned in place of real model output.

### logging
- **enabled** (bool): Globally enable or disable logging.
- **console_level** (string): One of `critical`, `error`, `warning`, `info`, `debug`.
- **folder** (string): Path for writing log files, relative to project root.
- **files** (map[string,string]): Keys are logger names; values are minimum log level for that file.

### misc
- **on_the_fly** (bool): When `true`, **AgentForge** re-reads YAML files before each run for rapid iteration.

### paths
- **files** (string): Default directory for agent I/O operations. You can add extra entries (e.g., `paths.temp`) and they will appear under `settings.system.paths`.

## Accessing System Settings

```python
from agentforge.config import Config
system_settings = Config().data['settings']['system']
```

## Examples

```yaml
# Run in debug with a custom simulated response
debug:
  mode: true
  simulated_response: "{\"status\":\"ok\"}"  
```

## Related Guides

- [Settings Overview](Settings.md)
- [Model Settings Guide](Models.md)
- [Storage Settings Guide](Storage.md)

---

**Need Help?**

If you have questions or need assistance, feel free to reach out:

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)  
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)