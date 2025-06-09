# Configuration Settings Overview

AgentForge manages framework settings through YAML files located in your project's `.agentforge/settings` directory. The singleton `Config` class reads every `.yaml` and `.yml` file under this folder, merging their contents into `Config.data['settings']`.

## Location

All configuration files reside at:
```
<project_root>/.agentforge/settings/
```

- **system.yaml**: System-level flags, file paths, debugging, and logging.
- **models.yaml**: Default model selection, API/model definitions, and embedding library.
- **storage.yaml**: Storage backend settings including persistence paths and timestamp options.

> Any additional YAML files placed in this directory will be loaded automatically.

## Accessing Settings in Code

```python
from agentforge.config import Config

config = Config()
settings = config.data['settings']
system = settings['system']
models = settings['models']
storage = settings['storage']
```

These objects drive behaviors such as debug mode, model instantiation, and data persistence.

## File Reference

| File         | Purpose                                        | Reference Guide              |
| ------------ | ---------------------------------------------- | ---------------------------- |
| system.yaml  | High-level framework options and file paths    | [System Settings](system.md) |
| models.yaml  | Model defaults and API/model library           | [Model Settings](models.md)  |
| storage.yaml | Storage backend configuration                  | [Storage Settings](storage.md)|

## Setting Hierarchy

Settings in **AgentForge** follow a clear hierarchy of resolution:

1. **Global Settings**: Defined in settings YAML files, these apply to all components.
2. **Agent Overrides**: Individual agents can override global model settings with `model_overrides` and certain agent-specific options.
3. **Cog Configuration**: Cogs define agent composition, memory nodes, and flow. Cogs can specify a `persona` (string) for all agents, and memory configuration is handled via memory nodes.

## Custom Overrides

### Agent Overrides
Agents can override global model settings via their own YAML definitions:

- **Model overrides**: Add a `model_overrides` section to change `api`, `model`, or `params` per agent. See [Model Settings](models.md) for details.
- **parse_response_as**: (optional) Specify a format (e.g., `json`, `yaml`) to parse the model's output. Example:

```yaml
parse_response_as: json
```

### Cog Configuration
Cogs define agent composition, memory nodes, and flow. Cogs can specify a `persona` (string) for all agents, and memory configuration is handled via memory nodes. There is no generic cog-level settings override.

## Best Practices

- Keep each YAML file focused on its concern: system, models, or storage.
- Favor global defaults; apply agent-level overrides only when necessary.
- For multi-agent systems, use cog-level persona and memory node configuration for consistency.
- Ensure the `.agentforge/settings` directory exists at your project root.
- Leverage `system.misc.on_the_fly` for dynamic reloading during development.

## Related Documentation
- [Agents Guide](../agents/agents.md)
- [Cogs Guide](../cogs/cogs.md)
- [Personas Guide](../personas/personas.md)
- [Memory Guide](../memory/memory.md)
