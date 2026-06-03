# AgentForge Documentation

Start here if you are new to AgentForge.

This public documentation path leads with the smallest successful workflow first, then moves into reference material after the basic shape is clear.

## Beginner Path

1. [Quickstart](guides/quickstart.md): Install AgentForge, scaffold `.agentforge/`, and understand the no-credential debug-mode first-run boundary.
2. [First Real Model Run](guides/first_real_model_run.md): Learn when provider credentials or local model services are required.
3. [Core Concepts](guides/core_concepts.md): Build the mental model for Agents, prompts, settings, and Cogs.
4. [Beginner Cog Walkthrough](guides/beginner_cog_walkthrough.md): Move from one Agent to a small multi-agent workflow.
5. [Advanced Reference](guides/advanced_reference.md): Continue into optional memory, personas, storage, custom APIs, custom Agents, utilities, and legacy Tools/Actions.

The [Using AgentForge](guides/using_agentforge.md) guide is the workflow hub for this path.

## Reference After The First Run

- [Agents](agents/agents.md): Agent lifecycle, prompt files, and advanced subclass hooks.
- [Cogs](cogs/cogs.md): Cog schema, flow transitions, branching, loops, return values, and memory configuration.
- [Settings](settings/settings.md): System, model, and storage settings.
- [APIs](apis/apis.md): Provider integration and advanced custom API hooks.
- [Memory](memory/memory.md) and [Personas](personas/personas.md): Optional context systems.
- [Storage](storage/chroma_storage.md), [Utilities](utils/utils_overview.md), and [Tools & Actions](tools_and_actions/overview.md): Advanced or compatibility references.

Internal contributor and agent guidance intentionally lives outside the public docs path in the repository's `dev-docs/` tree.
