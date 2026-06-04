# Quickstart

This is the first AgentForge workflow to run when you are new to the project.

It installs AgentForge, scaffolds `.agentforge/`, turns on debug mode for a smoke test, and runs one direct Agent without provider credentials.

## 1. Create A Project Environment

From the project directory that should own your AgentForge files, create and activate a Python environment:

```shell
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, activate the environment with:

```shell
.venv\Scripts\activate
```

Install AgentForge:

```shell
pip install agentforge
```

## 2. Scaffold `.agentforge/`

Run the scaffold command from the same project directory:

```shell
python -m agentforge.init_agentforge
```

This creates the project-owned `.agentforge/` resource folder.

For this first run, you only need `.agentforge/settings/system.yaml` and `.agentforge/prompts/hello_agent.yaml`.

## 3. Enable Debug Mode For A Smoke Test

Debug mode returns a simulated response instead of calling a model provider.

No API keys or local model services are needed for this quickstart.

Open `.agentforge/settings/system.yaml` and set `debug.mode` to `true`:

```yaml
debug:
  mode: true
```

## 4. Run One Agent

Create `run_hello_agent.py` in your project root:

```python
from agentforge.agent import Agent

result = Agent("hello_agent").run(user_input="AgentForge")
print(result)
```

Run it:

```shell
python run_hello_agent.py
```

The final output line should be:

```text
Hello from AgentForge debug mode.
```

When `debug.mode` is `true`, AgentForge may print config/debug messages before that final line.

## Where AgentForge Looks For `.agentforge/`

AgentForge resolves the active project root in this order:

1. An explicit `Config(root_path=...)` or `Config.reset(root_path=...)` call.
2. The `AGENTFORGE_ROOT` environment variable.
3. Auto-discovery walking upward from the running script until it finds `.agentforge/`.

For the beginner path, keep `run_hello_agent.py` inside the project that contains `.agentforge/`.

If your script lives outside that project, set `AGENTFORGE_ROOT` before running it:

```shell
export AGENTFORGE_ROOT=/path/to/your/project
```

Explicit `Config(root_path=...)` and `Config.reset(root_path=...)` are advanced deterministic setup options used most often in tests or tools.

## Credential Boundary

This quickstart uses debug mode, so it does not need provider credentials.

When debug mode is off, the shipped scaffold defaults to the Codex OAuth model path in `.agentforge/settings/models.yaml`.
That real-model path is covered in [First Real Model Run](first_real_model_run.md).

API-key providers and local model services are alternatives after the smoke test works.

## Navigation

- Start: [AgentForge Documentation](../README.md)
- Continue to [First Real Model Run](first_real_model_run.md) when you are ready to leave debug mode.
- Read [Core Concepts](core_concepts.md) when you want the mental model before editing more YAML.
- Use [Installation Details](installation_guide.md) for environment setup, provider key examples, and troubleshooting links.
