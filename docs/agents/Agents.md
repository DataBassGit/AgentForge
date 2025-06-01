# Agents Overview

**Agents** are the orchestrators in **AgentForge**, binding configuration, prompts, models and storage into end‑to‑end AI workflows. An agent:

- Loads its YAML configuration (`prompts`, `params`, `personas`, `settings`).
- Initializes context (persona data, storage) via `Config`.
- Renders system/user prompts using `PromptProcessor`.
- Resolves and invokes the LLM model via `Config.resolve_model_overrides`.
- Parses and post‑processes model output (`parse_result`, `build_output`).
- Saves results or context to storage if enabled.
- Returns the final output (text, images, data) to the caller.

Agents adhere to a standard lifecycle (see [Agent Class](AgentClass.md)) but can be subclassed for specialized behaviors. Agents can be used standalone or as part of a [Cog](../cogs/cogs.md) in multi-agent workflows.

---

## Key Resources

### **[Agent Class](AgentClass.md)**
- Dive into the foundational class from which all agents derive. You'll find a detailed breakdown of the `Agent` class, its attributes, initialization process, methods, and the essential logic that underpins every agent in the framework. This is your go-to reference for understanding the functionalities that are indispensable for creating custom agents.

### **[Agent Prompts](AgentPrompts.md)**
- Explore the realm of prompts that dictate an agent's behavior and interactions. Grasp how these guiding instructions ensure agents understand their objectives and relay information effectively.

### **[Advance Custom Agents Examples](CustomAgents.md)**
- Comfortable with the default agent class? Here, you'll find some examples of custom agents in more complex or specialized use cases.

### **[Overriding LLM Settings](../settings/models.md/#specifying-model-overrides-in-agents)**
- Each agent holds the power to tailor the Large Language Model (LLM) settings it employs. This section delves into how agents can utilize default LLMs or opt for specific models fine-tuned for unique tasks, offering flexibility and precision.

### **[Multi-Agent Orchestration (Cogs)](../cogs/cogs.md)**
- Discover how to compose multiple agents into powerful cognitive architectures using **Cogs**. Cogs allow you to define complex, branching workflows in YAML without writing Python code, connecting agents through decision-based transitions and shared memory.

