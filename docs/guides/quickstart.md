# Quickstart

This is the first AgentForge workflow to run when you are new to the project.

It installs AgentForge, scaffolds `.agentforge/`, turns on debug mode, and runs one direct Agent without provider credentials.

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

## 3. Enable Debug Mode

Debug mode returns a simulated response instead of calling a model provider.

No API keys or local model services are needed for this quickstart.

Use this copy/paste command to set `debug.mode` to `true`:

```shell
python -c "from pathlib import Path; p = Path('.agentforge/settings/system.yaml'); text = p.read_text(); p.write_text(text.replace('mode: false', 'mode: true', 1))"
```

You can also edit `.agentforge/settings/system.yaml` directly:

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

The current scaffold defaults to Gemini for real model calls, so a real call requires `GOOGLE_API_KEY` unless you change `.agentforge/settings/models.yaml`.

Cloud credentials and local model services are covered in [First Real Model Run](first_real_model_run.md).

## Next

- Continue to [First Real Model Run](first_real_model_run.md) when you are ready to leave debug mode.
- Read [Core Concepts](core_concepts.md) when you want the mental model before editing more YAML.
- Use [Installation Details](installation_guide.md) for environment setup, provider key examples, and troubleshooting links.
