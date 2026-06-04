# AgentForge Documentation

Start here if you are new to AgentForge.

This is the canonical public documentation hub.
The path below starts with a no-credential smoke test, moves to the default Codex OAuth real-model setup, and then introduces Cogs before advanced reference material.

## Beginner Path

1. [Quickstart](guides/quickstart.md): Install AgentForge, scaffold `.agentforge/`, and run a debug-mode smoke test without provider credentials.
2. [First Real Model Run](guides/first_real_model_run.md): Turn the same direct Agent path toward the default Codex OAuth model setup.
3. [Core Concepts](guides/core_concepts.md): Build the mental model for Agents, prompts, settings, and Cogs.
4. [Beginner Cog Walkthrough](guides/beginner_cog_walkthrough.md): Move from one Agent to a small multi-agent workflow.
5. [Branch/Loop Cog Walkthrough](guides/branch_loop_cog_walkthrough.md): Add a decision branch, revision loop, fallback, and loop guard.
6. [Advanced Reference](guides/advanced_reference.md): Continue into optional memory, personas, storage, custom APIs, custom Agents, utilities, and legacy Tools/Actions.

## Setup And Support

- [Using AgentForge](guides/using_agentforge.md): Project-root discovery, `.agentforge/` ownership, debug smoke-test boundaries, and real-model setup boundaries.
- [Installation Details](guides/installation_guide.md): Extra environment setup detail beyond the quickstart.
- [Prerequisites Details](guides/prerequisites_guide.md): Optional credentials, local model services, and platform dependencies.
- [Troubleshooting](guides/troubleshooting_guide.md): Common setup and provider errors.

## Reference After The Beginner Path

- [Agents](agents/agents.md): Agent lifecycle, prompt files, and advanced subclass hooks.
- [Cogs](cogs/cogs.md): Cog schema, flow transitions, branching, loops, return values, and memory configuration.
- [Settings](settings/settings.md): System, model, and storage settings.
- [APIs](apis/apis.md): Provider integration and advanced custom API hooks.
- [Memory](memory/memory.md) and [Personas](personas/personas.md): Optional context systems.
- [Storage](storage/chroma_storage.md), [Utilities](utils/utils_overview.md), and [Tools & Actions](tools_and_actions/overview.md): Advanced or compatibility references.

Internal contributor and agent guidance intentionally lives outside the public docs path in the repository's `dev-docs/` tree.
