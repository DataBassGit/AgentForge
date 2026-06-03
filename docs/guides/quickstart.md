# Quickstart

This is the first stop in the beginner documentation path.

The full copy/paste no-credential direct Agent walkthrough belongs here.

For now, this page establishes the setup boundaries and next links without adding the full runnable example yet.

## What This Step Is For

The first successful workflow should prove that AgentForge is installed, the project owns a `.agentforge/` directory, and debug mode can bypass real provider calls.

It should not require cloud API keys, a running local model service, memory, personas, storage tuning, subclassing, or Cog branching.

## Install And Scaffold

Create and activate a Python environment for your project, then install AgentForge:

```shell
pip install agentforge
```

From the root of the project that should own AgentForge resources, scaffold `.agentforge/`:

```shell
python -m agentforge.init_agentforge
```

The scaffold creates project-owned settings, prompts, cogs, personas, tools, actions, and custom API folders under `.agentforge/`.

Some scaffolded folders are advanced or compatibility surfaces; beginners can ignore them until the direct Agent and beginner Cog paths work.

## Where AgentForge Looks For `.agentforge/`

AgentForge resolves the active project root in this order:

1. An explicit `Config(root_path=...)` or `Config.reset(root_path=...)` call.
2. The `AGENTFORGE_ROOT` environment variable.
3. Auto-discovery walking upward from the running script until it finds `.agentforge/`.

For the beginner path, keep your script inside the project that contains `.agentforge/`.

If your script lives outside that project, set `AGENTFORGE_ROOT` before running it:

```shell
export AGENTFORGE_ROOT=/path/to/your/project
```

Explicit `Config(root_path=...)` and `Config.reset(root_path=...)` are advanced deterministic setup options used most often in tests or tools.

## Credential Boundary

The no-credential first run uses debug mode so AgentForge returns a simulated response instead of calling a model provider.

Cloud credentials and local model services are part of the next step, [First Real Model Run](first_real_model_run.md).

The current scaffold defaults to Gemini for real model calls, so a real call requires `GOOGLE_API_KEY` unless you change `.agentforge/settings/models.yaml`.

## Next

- Continue to [First Real Model Run](first_real_model_run.md) when you are ready to leave debug mode.
- Read [Core Concepts](core_concepts.md) when you want the mental model before editing more YAML.
- Use [Installation Details](installation_guide.md) for environment setup, provider key examples, and troubleshooting links.
