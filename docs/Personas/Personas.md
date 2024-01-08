# Persona Implementation Guide

## Overview of Personas

Personas are a core part of our system, allowing agents to have a distinct identity that can be tailored to the needs of various applications. Here's how personas are structured and implemented within our system.

### Location of Persona Files

Each persona is uniquely defined in a YAML file within the `personas` directory.
You can find this directory at `your_project_root/.agentforge/personas`

### Flexible Structure of Persona Files

The persona files are designed to be templates with a flexible structure:

- **Optional Attributes**: Every attribute in a persona file is optional. Include only the information pertinent to the persona you're creating.
- **Custom Attributes**: Feel free to add any attributes that will help define the persona for its intended use.
- **Blank Template**: Each file starts as a blank slate, allowing for complete customization.

#### Example Persona File (`default.yaml`):

```yaml
Name: HelperBot
Description: |+
  HelperBot is a versatile chatbot designed to assist in a range of tasks...
  [...more description...]

Personality: |+
  HelperBot exhibits a friendly, patient, and professional personality...
  [...more personality...]

Location: Multiple Platforms
Setting: |+
  HelperBot operates in a digital landscape...
  [...more setting...]

Username: User
```

### Usage of Personas in Agents

- **Default Persona**: A `directives.yaml` file under the `settings` folder specifies the system's default persona.

```yaml
# directives.yaml
Persona: default
```

- **Overriding Personas**: Agents can specify a different `Persona` attribute in their YAML configuration to override the default.

```yaml
# agent.yaml
Prompts: 
  # Agent sub-prompts
Persona: persona_name # Optional: Override default persona
```

### Consistency and Flexibility

- **Consistency**: While consistent attributes across persona files can be beneficial, they are not strictly required.
- **Flexibility**: The system accommodates diverse persona definitions, empowering users to craft personas that fit their specific requirements.

## Implementation Example

### Subclass Implementation (`PersonaAgent.py`)

To integrate persona attributes into an agent, you can create a `PersonaAgent` subclass that loads the persona data:

```python
from agentforge.agent import Agent

class PersonaAgent(Agent):

    def load_agent_type_data(self):
        persona = self.agent_data['persona']
        self.data['persona_name'] = persona['Name']
        self.data['persona_description'] = persona['Description']
        self.data['persona_personality'] = persona['Personality']
        self.data['persona_location'] = persona['Location']
        self.data['persona_setting'] = persona['Setting']
        self.data['persona_user'] = persona['Username']
```

This subclass method `load_agent_type_data` extracts various persona attributes from the configuration, making them readily available for the agent's operations.

### Child Agent Creation

Agents with specific roles can be derived from the `PersonaAgent`. Here's how child agents inherit the persona:

```python
from .PersonaAgent import PersonaAgent

class ReflectAgent(PersonaAgent):
    pass
```

```python
from .PersonaAgent import PersonaAgent

class TheoryAgent(PersonaAgent):
    pass
```

These child agents, `ReflectAgent` and `TheoryAgent`, now carry the persona attributes and can act within the framework of their defined personas.

# Conclusion

This guide is intended to provide you with a clear understanding of how to implement personas within our system. From creating persona files to weaving them into your agents, the process allows for robust and nuanced agent identities.

---
