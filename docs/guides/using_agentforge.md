# Using AgentForge

This guide explains the setup boundaries AgentForge uses when your script runs.

Use it when you need to understand where `.agentforge/` belongs, how AgentForge finds it, when debug mode is useful, and when provider setup begins.

For the recommended first-run order, start from the [AgentForge Documentation](../README.md) hub.

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

## Smoke-Test Boundary

The first setup check should not require provider credentials.

AgentForge's debug mode returns a simulated response instead of calling a provider, so it is the right boundary for a smoke test.

Use debug mode to prove that Python imports, `.agentforge/` discovery, prompt loading, and direct Agent execution all work.

## Real-Model Boundary

Real provider calls require either Codex OAuth, API keys, or a running local model service.

The shipped scaffold's default real model path is:

```yaml
default_model:
  api: openai_api
  model: codex_gpt55
```

Initialize Codex OAuth before using that default real-model path:

```shell
python -m agentforge.init_codex_oauth
```

Provider setup belongs in [First Real Model Run](first_real_model_run.md), not in the no-credential quickstart.

## After The Beginner Path

The reference docs remain available for intentional extension points and advanced workflows.

Start from [Advanced Reference](advanced_reference.md) when you are not sure which reference page you need:

- [Agents](../agents/agents.md), [Agent Prompts](../agents/agent_prompts.md), and [Custom Agents](../agents/custom_agents.md)
- [Cogs](../cogs/cogs.md)
- [Settings](../settings/settings.md), [Model Settings](../settings/models.md), and [System Settings](../settings/system.md)
- [APIs](../apis/apis.md) and [Vision](../apis/vision.md)
- [Memory](../memory/memory.md), [Personas](../personas/personas.md), and [Storage](../storage/chroma_storage.md)
- [Utilities](../utils/utils_overview.md) and [Tools & Actions](../tools_and_actions/overview.md)

Internal AgentForge development guidance is kept in `dev-docs/`, not in the public beginner path.

## Navigation

- Start: [AgentForge Documentation](../README.md)
- First run: [Quickstart](quickstart.md)
- Real model setup: [First Real Model Run](first_real_model_run.md)
