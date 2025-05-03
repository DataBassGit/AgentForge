# Persona Guide

A **persona** in **AgentForge** is a YAML configuration that defines an identity, background knowledge, style, and default values. When enabled, personas drive prompt variables and determine the storage context (`storage_id = persona`) for both individual agents and multi-agent cogs.

## 1. What Is a Persona?
- A structured YAML file under `.agentforge/personas/`.
- A bundle of key–value pairs (e.g., `name`, `description`, `goals`, `voice`).
- An optional data source for enriching prompts and scoping memory/storage.

### Effects on Agents and Cogs
- **Prompt Rendering**: Persona fields become placeholders in prompt templates (e.g., `{name}`, `{description}`).
- **Storage Resolution**: Memory classes use the persona name as `storage_id` when personas are enabled.
- **Memory Namespacing**: Each persona's interactions are stored in its own context, isolating data.
- **Cog Resolution**: Cogs can specify a persona to use for all agents within the cog, ensuring consistent identity.

## 2. Enabling & Disabling Personas
In `system.yaml`, configure:
```yaml
persona:
  enabled: true      # Set to false to ignore persona data
  name: default      # Fallback persona filename (without .yaml)
```
- **enabled** (`bool`): Toggles persona loading. Default `true`.
- **name** (`string`): The default persona file (minus `.yaml`).

When `enabled: false`, persona data is skipped and placeholders remain unresolved.

## 3. Folder Structure
```plaintext
.agentforge/
  personas/
    default.yaml
    alice.yaml
    chaos_goblin.yaml
```
- `.agentforge/personas/` is initialized from `src/agentforge/setup_files/personas/` when you scaffold a project.
- Filenames must match the persona `name` exactly (case‑sensitive). Use lowercase and hyphens or underscores.

## 4. Sample Persona File
```yaml
# .agentforge/personas/alice.yaml
name: Alice
description: |
  A friendly assistant with a cheerful tone
  and a knack for storytelling.
goals:
  - Provide helpful, concise answers.
  - Engage users with fun facts.
voice: conversational
```
- **name** (`string`): Display name for prompts.
- **description** (`string`): Multi-line background text.
- **goals** (`list[string]`): Mission statements or guidelines.
- **voice** (`string`): Style or tone descriptor.

## 5. Using Personas in Agents
Include a `persona` key in your prompt template YAML to have it rendered at runtime:
```yaml
prompts:
  system: |
    You are {name}, {description}
    Use the following tone of voice: {voice}
    Goals:
    - {goals}
    
  user: "The user has said the following message: {user_input}"
persona: alice
```
When `persona: alice` and `persona.enabled: true`, AgentForge loads `alice.yaml` and substitutes the fields into placeholders.

## 6. Using Personas in Cogs
Cogs can define a persona to use for all agents within the cog:
```yaml
cog:
  name: "ExampleFlow"
  description: "A sample decision workflow."
  persona: alice  # Optional: specify persona for all agents in this cog
  
  agents:
    - id: analyze
      template_file: AnalyzeAgent
    # ...other agents
```

The persona resolution in Cogs follows this hierarchy:
1. Cog-specific persona (if defined in the cog YAML)
2. Default system persona from system.yaml
3. No persona if persona.enabled is false

The resolved persona is used for storage resolution (for memory nodes) and is accessible to agents within the cog.

## 7. Best Practices
- Name files clearly (`scout_ranger.yaml`), matching the `persona` key in prompts.
- Keep persona files focused on static data (identity, style, key facts).
- Avoid large persona blocks that may clutter prompt context.
- Use runtime variables for dynamic data; runtime overrides persona fields.
- Maintain a meaningful default persona; avoid overloading `default.yaml` with multiple roles.
- For multi-agent systems, use a single persona in the cog definition for consistent identity.

---

## Related Documentation
- [System Settings Guide](../Settings/System.md)  
- [Agent Prompts](../Agents/AgentPrompts.md)  
- [Cogs Guide](../Cogs/Cogs.md)  
- [Memory Guide](../Storage/Memory.md)
