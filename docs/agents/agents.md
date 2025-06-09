# Agents Overview

Agents are the orchestrators in AgentForge, binding configuration, prompts, models, and storage into end-to-end AI workflows. An agent:

- Loads its configuration (prompts, params, persona, settings) using the Config system.
- Initializes context, including persona data and runtime variables.
- Renders system and user prompts using PromptProcessor, substituting dynamic variables.
- Resolves and invokes the LLM model as specified in its configuration.
- Parses and post-processes model output, building the final output.
- Returns the output (text, images, or data) to the caller.

Agents follow a standard lifecycle (see [Agent Class](agent_class.md)) and can be subclassed for custom behaviors. Agents may be used standalone or as part of a multi-agent workflow (see Cogs).

---

## Key Resources

- **[Agent Class](agent_class.md)**: Reference for the base Agent class, its attributes, initialization, and extension points.
- **[Agent Prompts](agent_prompts.md)**: Details on prompt templates, dynamic variables, and rendering logic.
- **[Custom Agents](custom_agents.md)**: Examples and guidance for subclassing Agent for advanced use cases.
- **[Model Overrides](../settings/models.md#specifying-model-overrides-in-agents)**: How to specify and override LLM settings per agent.
- **[Multi-Agent Orchestration (Cogs)](../cogs/cogs.md)**: How to compose agents into complex workflows using Cogs.

