# Persona Guide

A **persona** in **AgentForge** is a YAML configuration that defines an agent's identity, background, style, and default values. When enabled, personas drive prompt variables and determine the storage context for both individual agents and multi-agent cogs.

## 1. What Is a Persona?
- A structured YAML file under `.agentforge/personas/`.
- Uses a nested schema with `static:` and `retrieval:` sections, this schema is important for the `PersonaMemory` node. 
- Provides identity, style, and context for prompt rendering and memory scoping.
- Example persona files (like `alice.yaml`, `chaos_goblin.yaml`) are for illustration only and are not included by default.

### Effects on Agents and Cogs
- **Prompt Rendering**: Persona fields become placeholders in prompt templates (e.g., `{persona.static.name}`, `{persona.retrieval.tone}`).
- **Storage Resolution**: Memory classes use the persona name as a storage namespace when personas are enabled.
- **Memory Namespacing**: Each persona's interactions are stored in its own context, isolating data.
- **Cog/Agent Resolution**: Cogs or agents can specify a persona, ensuring consistent identity.

## 2. Enabling & Configuring Personas
In `system.yaml`, configure:
```yaml
persona:
  enabled: true           # Set to false to ignore persona data
  name: default_assistant # Fallback persona filename (without .yaml)
  static_char_cap: 8000   # Max character length for persona markdown (0 = no limit)
```
- **enabled** (`bool`): Toggles persona loading. Default `true`.
- **name** (`string`): The default persona file (minus `.yaml`).
- **static_char_cap** (`int`): Truncates persona markdown injected into prompts if it exceeds this length. This is used exclusively in the `PersonaMemory` node

When `enabled: false`, persona data is skipped and placeholders remain unresolved.

## 3. Folder Structure
```plaintext
.agentforge/
  personas/
    default_assistant.yaml
    # (You may add your own, e.g. alice.yaml, chaos_goblin.yaml)
```
- `.agentforge/personas/` is initialized from `src/agentforge/setup_files/personas/` when you scaffold a project.
- Filenames must match the persona `name` exactly (case‑sensitive). Use lowercase and underscores or hyphens.

## 4. Persona YAML Schema (Current)

> **Note:** The `static`/`retrieval` schema is only required if you are using the `PersonaMemory` node. For standard (memory-less) persona usage, you may use any flat or nested structure that fits your prompt needs.
>
> When using `PersonaMemory`, the `retrieval` section defines attributes that are stored in a vector store and can be dynamically retrieved at runtime based on relevance. Only fields under `retrieval` are used for this dynamic retrieval; fields under `static` are not. This enables powerful, context-aware persona adaptation in Cogs that leverage `PersonaMemory`.

```yaml
# .agentforge/personas/alice.yaml (for illustration only)
static:
  name: Alice
  description: |
    A friendly assistant with a cheerful tone and a knack for storytelling.
  goal: Provide helpful, concise answers.
  
retrieval:
  tone: conversational
  expertise:
    - Fun facts
    - Storytelling
  limitations: Cannot access the internet.
  principles:
    - Helpfulness
    - Clarity
```
- **static**: Core identity information (name, description, goal, etc.)
- **retrieval**: Additional context, style, and values (tone, expertise, limitations, principles, etc.) used for dynamic retrieval by `PersonaMemory`.
- You may add or omit fields as needed for your use case.

## 5. Using Personas in Prompts
Reference persona fields in your prompt templates using dot notation:
```yaml
prompts:
  system: |
    You are {persona.static.name}, {persona.static.description}
    Use the following tone of voice: {persona.retrieval.tone}
    Goals:
    - {persona.static.goal}
  user: "The user has said the following message: {user_input}"
persona: alice
```
When `persona: alice` and `persona.enabled: true`, AgentForge loads `alice.yaml` and substitutes the fields into placeholders.

## 6. Using Personas in Cogs and Agents
Cogs or agents can define a persona to use for all agents within the cog or for a specific agent:
```yaml
cog:
  name: "ExampleFlow"
  description: "A sample decision workflow."
  persona: alice  # Optional: specify persona for all agents in this cog
  agents:
    - id: analyze
      template_file: analyze_agent
      # persona: custom_persona  # (Optional: agent-level override)
```

Persona resolution hierarchy:
1. Cog-defined persona (if defined in the cog YAML)
2. Agent-defined persona (if present)
3. Default system persona from system.yaml
4. No persona if persona.enabled is false

The resolved persona is used for storage resolution and is accessible to agents within the cog.

## 7. Brief Note: PersonaMemory
AgentForge includes a `PersonaMemory` system for dynamic storage and retrieval of persona-related facts and narratives. This is an advanced feature and is referenced in some example cogs. Full documentation for `PersonaMemory` will be provided separately.

---

## Related Documentation
- [System Settings Guide](../settings/system.md)
- [Agent Prompts](../agents/agent_prompts.md)
- [Cogs Guide](../cogs/cogs.md)
- [Memory Guide](../memory/memory.md)
