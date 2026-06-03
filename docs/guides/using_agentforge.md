# Using AgentForge

This guide is the beginner workflow hub for AgentForge.

Use it to choose the next public guide in the recommended order instead of starting from schemas, storage internals, subclass hooks, or legacy tools.

## Beginner Workflow

1. [Quickstart](quickstart.md): Install AgentForge, scaffold `.agentforge/`, and use debug mode as the first no-credential boundary.
2. [First Real Model Run](first_real_model_run.md): Turn the same direct Agent path toward a real model only after the debug path is understood.
3. [Core Concepts](core_concepts.md): Learn what Agents, prompt files, settings, and Cogs do before reading reference schemas.
4. [Beginner Cog Walkthrough](beginner_cog_walkthrough.md): Move from a direct Agent to a small no-memory Cog workflow.
5. [Branch/Loop Cog Walkthrough](branch_loop_cog_walkthrough.md): Add a beginner decision branch, revision loop, fallback, and `max_visits`.
6. [Advanced Reference](advanced_reference.md): Continue into memory, personas, storage, custom APIs, custom Agents, utilities, and legacy Tools/Actions.

## Setup Boundary

AgentForge reads consumer-owned resources from a `.agentforge/` directory.

Run the scaffold command from the root of the project that should own those resources:

```shell
python -m agentforge.init_agentforge
```

When AgentForge starts, it finds the active project root in this order:

1. An explicit `Config(root_path=...)` or `Config.reset(root_path=...)` call.
2. The `AGENTFORGE_ROOT` environment variable.
3. Auto-discovery walking upward from the running script until it finds `.agentforge/`.

Most beginners should scaffold `.agentforge/` in the project root and run scripts from that project.

Use `AGENTFORGE_ROOT=/path/to/project` when your script lives somewhere else or you want the project root to be unambiguous.

Use explicit `Config(root_path=...)` or `Config.reset(root_path=...)` only when you are writing advanced setup code, tests, or deterministic tooling.

## Credential Boundary

The first beginner path should not require cloud credentials.

AgentForge's debug mode returns a simulated response instead of calling a provider, so it is the right boundary for a first setup check.

Real provider calls require credentials or a running local model service.

The current scaffold's default model points at Gemini, so a real cloud call uses `GOOGLE_API_KEY` unless you change `.agentforge/settings/models.yaml`.

Provider setup belongs in [First Real Model Run](first_real_model_run.md), not in the first no-credential quickstart.

## After The Beginner Path

The reference docs remain available for intentional extension points and advanced workflows:

- [Agents](../agents/agents.md), [Agent Prompts](../agents/agent_prompts.md), and [Custom Agents](../agents/custom_agents.md)
- [Cogs](../cogs/cogs.md)
- [Settings](../settings/settings.md), [Model Settings](../settings/models.md), and [System Settings](../settings/system.md)
- [APIs](../apis/apis.md) and [Vision](../apis/vision.md)
- [Memory](../memory/memory.md), [Personas](../personas/personas.md), and [Storage](../storage/chroma_storage.md)
- [Utilities](../utils/utils_overview.md) and [Tools & Actions](../tools_and_actions/overview.md)

Internal AgentForge development guidance is kept in `dev-docs/`, not in the public beginner path.
