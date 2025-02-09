# Persona Guide

Personas in **AgentForge** are files that bundle various attributes—ranging from domain knowledge to personality traits—into a single resource that agents can draw upon. Rather than just a “character profile,” a persona is effectively extra data your agent can leverage to enrich its responses or maintain context.

---

## Overview

1. **Where They Live**: Personas reside in `.agentforge/personas/`. Each persona is a separate YAML file (e.g., `botty.yaml`, `expert.yaml`).  
2. **How They’re Loaded**: **AgentForge** checks if personas are enabled via `system.yaml` under the `persona` section. It then merges the specified persona’s attributes into an agent’s data at runtime.  
3. **How Agents Use Them**: Any attribute you define in a persona can appear in your prompt YAML file as a placeholder (like `{name}` or `{description}`). If that placeholder is present, **AgentForge** automatically substitutes the persona’s data.

---

## Enabling Personas in `system.yaml`

```yaml
persona:
  enabled: true
  name: default
```

- **`enabled`**: Toggles whether the framework attempts to load persona data at all.  
- **`name`**: Specifies a default persona file (minus the `.yaml` extension). By default, this is `"default"`, meaning it will look for `.agentforge/personas/default.yaml`.

If `enabled` is set to `false`, no persona data is loaded, and any references to persona variables in your prompts won’t be populated.

---

## Persona File Structure

A persona file is typically very flexible. Here’s an example:

```yaml
# .agentforge/personas/botty.yaml

name: Botty McBotFace
description: |
  A cheerful assistant who likes to crack jokes and provide friendly advice.

domain_knowledge: |
  - Familiar with basic math, cooking tips, and cat facts.
  - Loves discussing the weather.

favorite_color: green
location: Virtual Town
```

1. **You can define any keys you want**—`name`, `description`, `domain_knowledge`, etc.  
2. **Values can be strings, lists, or nested objects**—whatever your agent needs.  
3. **Keys become lowercase** internally. Make sure you reference them in prompts using lowercase placeholders (e.g., `{domain_knowledge}`). 
4. **Persona vs. Runtime**—If both a persona and a runtime argument define the same variable, the runtime argument takes precedence.

---

## Using Personas in Agent Prompts

Agents automatically load the default persona declared in `system.yaml`. But you can override which persona file to use by specifying a `persona` key in the agent’s prompt YAML:

```yaml
# .agentforge/prompts/friendlyagent.yaml

prompts:
  system:
    identity: "You are {name}, {description}"
    knowledge: "{domain_knowledge}"
  user: "Hello, who are you?"

persona: botty
```

When this agent runs:

- **If** `persona.enabled: true` in `system.yaml`, it checks for a file named `botty.yaml` in `.agentforge/personas/`.  
- **Merges** the persona’s attributes (e.g., `name`, `description`, `domain_knowledge`) into `agent_data`.  
- **Prompt placeholders** like `{name}` or `{domain_knowledge}` get replaced with the persona’s data.

---

## Overriding the Default Persona

If you don’t specify `persona: botty` (or some other name) in your prompt file, **AgentForge** uses the default persona (`name: default`) from `system.yaml`. That means it looks for `.agentforge/personas/default.yaml`.

To override at the agent level:

```yaml
persona: some_other_persona
```

And ensure `.agentforge/personas/some_other_persona.yaml` exists.

---

## Case-Insensitive Keys

When persona data is loaded, all keys are converted to lowercase. So if your YAML file says:

```yaml
Name: MyPersona
Location: Virtual
```

Then in your agent’s prompt, you’d reference them as `{name}` or `{location}`, both in lowercase.

---

## Example Usage in Code

```python
from agentforge.agent import Agent

class FriendlyAgent(Agent):
    def process_data(self):
        # The loaded persona data is available at self.agent_data['persona']
        persona_info = self.agent_data['persona']
        if persona_info:
            # e.g. persona_info['name'] -> 'Botty McBotFace'
            pass

        # You can also see merged placeholders at self.template_data if needed
        pass
```

---

## Best Practices

1. **Keep Persona Minimal**  
   Store only the data you truly need. The more data you load, the more cluttered your agent’s context can become.  
2. **Use Consistent Naming**  
   If your persona file is `expert.yaml`, reference it as `persona: expert` (all lowercase) in your agent prompt.  
3. **Document Persona Keys**  
   Clearly note which attributes exist (`name`, `description`, etc.) so you remember to use them in your prompt placeholders.  
4. **Fallback**  
   If you don’t override the default persona, your agents will always use `.agentforge/personas/default.yaml`. Keep that file up to date for broad use cases.
5. **Persona vs. Runtime**  
   If both a persona and a runtime argument define the same variable, the runtime argument takes precedence.

---

## Conclusion

Personas in **AgentForge** provide a flexible way to inject contextual or knowledge-based data into your agents’ prompts. Whether you want a friendly “Botty” persona with a playful personality or an “Expert” persona brimming with domain knowledge, simply define the relevant attributes in a YAML file, reference them in your agent’s prompt, and let AgentForge handle the rest.

**For More Info**:

- [System Settings Guide](../Settings/System.md) – Controls the default persona name and whether personas are enabled.  
- [Prompt Handling](../Agents/AgentPrompts.md) – Explains how placeholders like `{name}` are merged into final prompts.

---

**Need Help?**

If you have questions or need assistance, feel free to reach out:

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)  
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)
