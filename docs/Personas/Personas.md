# Persona Guide

## Overview

**Personas** in our system serve as an abstraction of the knowledge that an agent has access to, rather than merely defining the agent’s character or personality traits. They encapsulate vast and varied information – from specific subject matters to general world facts, and yes personality traits – they constitute the database of knowledge that the agents can use during their operation.

### Location of Persona Files

Each persona is uniquely defined in a YAML file within the `personas` directory.
You can find this directory at `your_project_root/.agentforge/personas`

### Flexible Structure of Persona Files

The persona files are templates with a flexible structure:

- **Optional Attributes**: Every attribute in a persona file is optional. Include only the information pertinent to the persona you're creating.
- **Custom Attributes**: Add any attributes that represent the knowledge or information the agent should have access to.
- **Blank Template**: Each file starts as a blank slate, allowing for complete customization and adaptability to the agent’s knowledge needs.

#### Persona File Template (`default.yaml`):

```yaml
# Persona Configuration File
# Use this file as a template to define the persona of your agent(s).
# Each attribute in this file will be automatically loaded as part of the agent data for prompt rendering.
# However, it's important to note that merely defining attributes here does not guarantee their use by the agent.
# Attributes must also be referenced in the corresponding agent's prompt template YAML file to be utilized in interactions.
# To ensure compatibility, attribute names should follow the Python convention for variables (e.g., lowercase with underscores) to avoid issues.
# Note: Attribute key names are case-insensitive; the system will automatically convert them to lowercase when adding them to the agent data.
# Therefore, ensure that attributes in the prompt templates are also defined in lowercase and that they adhere to the python variable naming convention..

# Feel free to add, modify, or remove attributes according to your needs.

# Name: The name of your agent or persona.
# This should be unique and descriptive, giving a clear indication of your agent identity or purpose.
Name: Persona Name

# Description: A detailed description of your agent.
# This should include any background information, capabilities, and the general tone or personality your agent embodies.
# Use the '|+' syntax for multi-line strings to ensure proper formatting.
Description: |+
    Describe your agent here...

# Location: The primary operating environment or context of your agent.
# This can be virtual, physical, or conceptual, depending on your agent's design.
Location: Virtual Environment/Physical Location

# Setting: The detailed setting in which your agent operates.
# This can help in providing contextual background for your agent's interactions and responses.
Setting: |+
    Provide a detailed description of the setting or context in which your agent operates. This could be a 
    virtual space, like a digital assistant in a smart home, or a fictional world for game-based NPCs. 
    The setting can influence how the agent interacts and responds to queries.

# Username: A default or suggested username for interactions.
# This can be useful for personalizing responses or for systems that require user identification.
Username: DefaultUser

# Objective: The primary goal or function of your agent.
# This can be as broad as providing assistance and answering questions, or as specific as performing tasks in a particular domain.
Objective: Define the primary goal of your agent here.

# Additional Attributes: You can add any number of additional attributes to further define your agent.
# Examples might include 'Skills', 'KnowledgeAreas', 'PreferredPronouns', etc.
# Use the same format as above to add new sections.

# Example of an additional attribute:
# Skills:
#   - "Skill 1: Description"
#   - "Skill 2: Description"
#   - "Add as many skills as relevant for your agent."

# Remember to save your changes to this file before using it with your system.
# This will ensure your agent persona is accurately represented and can perform as intended.

```

### Usage of Personas in Agents

- **Default Persona**: The `system.yaml` file under the `.agentforge/settings` folder specifies the system's default persona.

```yaml system.yaml
# system.yaml
Persona: default # <--- Name of the Persona YAML File in the .agentforge/personas folder
# ... other settings ...
```

- **Overriding Personas**: Agents can specify a different `Persona` attribute in their YAML configuration to override the default persona set by the system configuration file.

```yaml
# agent.yaml
Prompts: 
  # Agent sub-prompts

Persona: persona_name # Optional: Override persona set by system
```

### Agents using Persona Information

The information defined in the persona is automatically injected into the agent data, like any other variable passed to the agent via code. However, the attribute name of the defined knowledge variable **MUST** be referenced in the prompt file in order for it to be used. This allows the system to inject and render that information onto the prompt that is passed to the Large Language Model (LLM).



To illustrate this, consider a persona file where the `Name` attribute is set to 'Botty Mc.BotFace':


```yaml
# botty.yaml
Name: Botty Mc.BotFace
# ... more attributes ...
```

This `Name` information can be used by an agent when running inference. By default, the system will use the **persona** selected in the [system configuration](../../src/agentforge/setup_files/settings/system.yaml) file. This can be overridden be referencing a different **persona** file in the agent's corresponding prompt YAML file, as shown:

```yaml
# example_agent.yaml
Prompts:
  System: |+
    Your name is {name}.
# ... other sub prompts ... 

Persona: botty # Optional | We tell the agent to use this persona - Use the persona YAML file name without the extension.
```

The text `{name}` in the prompt file will be replaced with the `Name` value from the **persona** file when it's rendered. So a possible rendered prompt when sent to the LLM would look like this:

```text
Your name is Botty Mc.BotFace.
```

Each attribute defined in the persona file can be used in a similar way, allowing for highly adaptable and context-aware agent interactions.

>**Important Note**: Attribute key names in the persona file are case-insensitive; the system will automatically convert them to lowercase when adding them to the agent data. Therefore, when referencing these attributes in the prompt templates, ensure you use them in lowercase and that they adhere to the python variable naming convention. 

## Conclusion

With **Personas**, we aim to provide a flexible, efficient, and effective way of encapsulating the knowledge that an agent can use. They are not just about creating a psychological profile for an agent but about equipping an agent with the necessary knowledge to perform its tasks optimally.