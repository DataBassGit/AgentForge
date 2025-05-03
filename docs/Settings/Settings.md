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
| system.yaml  | High-level framework options and file paths    | [System Settings](System.md) |
| models.yaml  | Model defaults and API/model library           | [Model Settings](Models.md)  |
| storage.yaml | Storage backend configuration                  | [Storage Settings](Storage.md)|

## Setting Hierarchy

Settings in AgentForge follow a hierarchy of resolution:

1. **Global Settings**: Defined in settings YAML files, these apply to all components.
2. **Agent Overrides**: Individual agents can override global settings with specific needs.
3. **Cog Settings**: Cogs can define settings that apply to all agents within them.

## Custom Overrides

### Agent Overrides
Agents can override global settings via their own YAML definitions:

- **Model overrides**: Add a `model_overrides` section to change `api`, `model`, or `params` per agent.
- **Storage overrides**: Use `storage_overrides` to adjust storage options for a specific agent.

### Cog Settings
Cogs automatically handle configuration resolution for contained agents:

- **Persona resolution**: Cogs can specify a persona to use for all agents.
- **Memory Configuration**: Memory nodes in cogs inherit settings from the cog configuration.
- **Response Format**: Cogs can define default response formats for agent outputs.

Overrides merge in order: API-level → class-level → model-level → cog-level → agent-level.

## Best Practices

- Keep each YAML file focused on its concern: system, models, or storage.
- Favor global defaults; apply agent-level overrides only when necessary.
- For multi-agent systems, use cog-level settings for consistency.
- Ensure the `.agentforge/settings` directory exists at your project root.
- Leverage `system.misc.on_the_fly` for dynamic reloading during development.

## Related Documentation
- [Agents Guide](../Agents/Agents.md)
- [Cogs Guide](../Cogs/Cogs.md)
- [Personas Guide](../Personas/Personas.md)
- [Memory Guide](../Storage/Memory.md)