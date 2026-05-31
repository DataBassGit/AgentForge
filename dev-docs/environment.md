# Environment Notes

This document is for agents and developers running AgentForge locally. It is not an end-user installation guide.

## Local Virtual Environment

The repository uses a local `.venv/` using Python 3.14:

```shell
source .venv/bin/activate
python --version
python -m pip --version
```

Use this venv for normal local checks when it exists. If the venv is missing, recreate it with the current local development Python:

```shell
python3.14 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r REQUIREMENTS.txt
.venv/bin/python -m pip install -e .
```

The package metadata declares `requires-python = ">=3.10"` and classifiers through Python 3.14. Python 3.14 is the preferred local development version after the compatibility review, but Python 3.10 remains the declared lower bound until later compatibility work intentionally changes it.

## Python Compatibility Checks

Use a separate temporary venv when rechecking Python compatibility or dependency resolution without disturbing the repo-local `.venv/`:

```shell
python3.14 -m venv --clear /tmp/agentforge-py314-compat
/tmp/agentforge-py314-compat/bin/python -m pip install --upgrade pip
/tmp/agentforge-py314-compat/bin/python -m pip install -r REQUIREMENTS.txt
/tmp/agentforge-py314-compat/bin/python -m pip install -e .
/tmp/agentforge-py314-compat/bin/python -m pytest
```

This full Python 3.14 install path has passed for `REQUIREMENTS.txt`, editable package metadata, and the default pytest suite. The remaining compatibility risk is not a known `python_version <= "3.13"` blocker; it is the size and build surface of the Chroma, Torch, sentence-transformers, and optional media stack.

## Dependencies

The repo has two dependency sources:

- `pyproject.toml` for package metadata, runtime install dependencies, build-system requirements, and optional extras.
- `REQUIREMENTS.txt` for local development and broader optional tooling.

They are not guaranteed to match exactly. When adding or changing dependencies, decide which surface is affected:

- Runtime library dependency: update `[project].dependencies` in `pyproject.toml`.
- Local development or test-only dependency: update `REQUIREMENTS.txt` only if the repo intentionally tracks it there.
- Optional feature dependency: prefer `[project.optional-dependencies]` or a clear environment note instead of forcing all users to install it.
- Build-only dependency: update `[build-system].requires`, not runtime dependencies.

Do not install heavy or network-fetched dependencies unless the task requires it. Network access may be restricted in agent sessions.

## Static Tooling

Ruff and basedpyright are local developer tools tracked in `REQUIREMENTS.txt`. They are not runtime package dependencies.

Install only the static tools when validating cleanup guardrails in an existing venv:

```shell
python -m pip install ruff basedpyright
```

Run Ruff lint checks without applying fixes:

```shell
ruff check .
```

Run Ruff formatting in check mode only unless the change explicitly approves formatting edits:

```shell
ruff format --check .
```

Run basedpyright as the repo type checker:

```shell
basedpyright --project pyproject.toml
```

Ruff owns line length and signature-adjacent style guardrails. BasedPyright owns type checking only and should not be used for formatting or line-length enforcement.

## Git Hooks

Tracked Git hooks live in `.githooks/`. Install them for the local checkout with:

```shell
scripts/install-git-hooks.sh
```

The pre-push hook uses `AGENTFORGE_PYTHON` when set, then `.venv/bin/python`, then legacy `venv/bin/python`, then a system Python fallback. It runs full-repo Ruff lint, Ruff format check, basedpyright, and the default pytest suite:

```shell
ruff check .
ruff format --check .
basedpyright --project pyproject.toml
python -m pytest
```

The whole configured Python tree is expected to stay clean for Ruff and basedpyright. Pytest remains full default-suite verification, with integration-marked tests excluded by `pytest.ini`.

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

## Package And Install Checks

Build package artifacts into `/tmp` when validating install workflow changes:

```shell
python -m build --sdist --wheel --outdir /tmp/agentforge-package-dist
```

Install the built wheel into a clean Python 3.14 venv and verify imports plus setup-file scaffolding:

```shell
python3.14 -m venv --clear /tmp/agentforge-package-install
/tmp/agentforge-package-install/bin/python -m pip install --upgrade pip
/tmp/agentforge-package-install/bin/python -m pip install /tmp/agentforge-package-dist/agentforge-0.6.5-py3-none-any.whl
```

AgentForge does not currently install an `agentforge` console script. Use `python -m agentforge.init_agentforge` to scaffold `.agentforge/` and `python -m agentforge.init_codex_oauth` for Codex OAuth setup.

## Known Friction Points

- Public install docs and package/dependency workflow still need an alignment pass.
- Package metadata now supports Python 3.14 while keeping the lower bound at Python `>=3.10`; broad annotation modernization, such as replacing `Optional[...]` with `... | None`, should happen in scoped cleanup rather than the tooling baseline.
- No public `agentforge` console command is installed yet; revisit a real CLI/scaffold command during beginner workflow work if it becomes useful.
- Tools and Actions are deprecated in public docs but still present in source and setup files for compatibility.
- Storage tests should use `FakeChromaStorage` unless exercising Chroma integration specifically.
- Tests may create a temporary repo-root `.agentforge`; cleanup is handled by fixtures/bootstrap, but check `git status --short` after interrupted runs.
