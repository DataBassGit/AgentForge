# Environment Notes

This document is for agents and developers running AgentForge locally. It is not an end-user installation guide.

## Local Virtual Environment

The repository currently contains a local `venv/` using Python 3.13:

```shell
source venv/bin/activate
python --version
python -m pip --version
```

Use this venv for local checks when it exists. If the venv is missing, create a new one with the Python version you are validating for the change. The package metadata currently declares `python_requires=">=3.9"` and classifiers through Python 3.13, while public docs and local commands may not be fully aligned. Treat Python-version claims as cleanup targets, not settled truth.

## Dependencies

The repo has two dependency sources:

- `setup.py` for install metadata.
- `REQUIREMENTS.txt` for local development and broader optional tooling.

They are not guaranteed to match exactly. When adding or changing dependencies, decide which surface is affected:

- Runtime library dependency: update `setup.py`.
- Local development or test-only dependency: update `REQUIREMENTS.txt` only if the repo intentionally tracks it there.
- Optional feature dependency: prefer an optional extra or clear environment note instead of forcing all users to install it.

Do not install heavy or network-fetched dependencies unless the task requires it. Network access may be restricted in agent sessions.

## Project Configuration

AgentForge expects consumer configuration under `.agentforge/`. Default resources live in `src/agentforge/setup_files/` and can be scaffolded with:

```shell
python -m agentforge.init_agentforge
```

For local tests, prefer isolated temporary `.agentforge` directories through fixtures. Avoid depending on a repo-root `.agentforge` unless the test is explicitly exercising bootstrap behavior.

Project root resolution uses this order:

1. `Config(root_path=...)` or `Config.reset(root_path=...)`.
2. `AGENTFORGE_ROOT`.
3. Auto-discovery walking upward from the running script.

For ad hoc scripts, set `AGENTFORGE_ROOT` or call `Config.reset(root_path=...)` when you need deterministic config loading.

## Test Bootstrap

`tests/conftest.py` calls `agentforge.testing.bootstrap.bootstrap_test_env()` to prepare tests. The bootstrap helper:

- changes the current working directory to the repo root;
- adds `src/` to `sys.path`;
- can create a repo-root `.agentforge` from setup files;
- can replace Chroma storage with fakes;
- can stub `Agent.run` to avoid live model calls;
- can silence logging and print output.

Use `isolated_config` for tests that need mutable `.agentforge` resources. That fixture copies setup files into a temporary directory and resets `Config` to that root.

## Running Tests

Default pytest behavior is configured in `pytest.ini`:

```ini
addopts = -p no:warnings -m "not integration"
```

Run the default suite with:

```shell
python -m pytest
```

Run focused tests by path when changing one subsystem:

```shell
python -m pytest tests/config_tests/test_config.py
python -m pytest tests/core_tests/test_transition_resolver.py
python -m pytest tests/utils/test_parsing_processor_two_stage.py
```

Integration-marked tests are skipped by default. Run them only when the change needs that coverage and the environment has required services or credentials:

```shell
python -m pytest -m integration
```

Live examples under `tests/real_tests/` use real provider behavior. Do not run them as routine verification.

## Credentials And External Services

Many providers read credentials from environment variables, such as OpenAI, Anthropic, Google, Groq, or provider-specific local services. Do not hard-code credentials in tests, docs, setup files, or examples.

Local providers such as Ollama or LM Studio should be treated as optional runtime integrations. Tests should use fakes unless the goal is explicitly to verify a live provider path.

Codex OAuth is separate from `OPENAI_API_KEY` and is initialized through:

```shell
python -m agentforge.init_codex_oauth
```

Do not change provider credential behavior without updating provider docs, setup defaults, and focused failure tests.

## Known Friction Points

- Public install docs, `REQUIREMENTS.txt`, and `setup.py` currently need an alignment pass.
- `setup.py` declares a console entrypoint for `agentforge.cli:main`; verify the source tree before relying on that CLI.
- Tools and Actions are deprecated in public docs but still present in source and setup files for compatibility.
- Storage tests should use `FakeChromaStorage` unless exercising Chroma integration specifically.
- Tests may create a temporary repo-root `.agentforge`; cleanup is handled by fixtures/bootstrap, but check `git status --short` after interrupted runs.
