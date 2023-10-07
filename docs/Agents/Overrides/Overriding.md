# Overriding Default LLM Configurations

Every agent can autonomously override the default settings for the LLM
(Large Language Model) that are set in the `model.yaml` file.
This capability provides flexibility for agents to use specific models 
or parameters based on their individual tasks or requirements.

## Format

To override the defaults for an agent, you have to define a `ModelOverrides` attribute inside the agent's corresponding `YAML` file. 
The structure is analogous to the one in the `model.yaml` file.

Example:

```yaml
Prompts: 
  # Agent sub-prompts
ModelOverrides:
  API: openai_api
  Model: smart_model
  Params:
    # Model parameters specific to this agent
```

## Usage

By including the `ModelOverrides` attribute in an agent's `YAML` file,
you specify that the agent should utilize these settings instead of those in the primary `model.yaml`.
This is particularly useful if, for instance,
a specific agent needs to run on a more advanced model or with different parameters than other agents in the system.

> **Note**: Overriding defaults at the agent level provides granular control, but it's essential to ensure that the model and parameters defined are compatible and are available within the framework. Always test any overrides to ensure smooth operation.

---