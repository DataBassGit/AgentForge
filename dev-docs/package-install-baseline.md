# Package Install Baseline

Recorded 2026-05-30 and refreshed 2026-05-31. This is developer-only package and install evidence, not public install documentation.

## Metadata Decision

- Package metadata moved from `setup.py` into `pyproject.toml` using the setuptools build backend.
- `setup.py` was removed so runtime package metadata has one source of truth.
- `requires-python` remains `>=3.10`, with classifiers through Python 3.14.
- Base runtime dependencies remain conservative and installed by default. Heavy dependency slimming is deferred until optional extras and lazy-import diagnostics can be designed together.
- Build-only `setuptools` moved to `[build-system].requires`; it is not a runtime package dependency.
- AgentForge does not install an `agentforge` console script. The supported setup commands remain `python -m agentforge.init_agentforge` and `python -m agentforge.init_codex_oauth`.

## Artifact Evidence

Built artifacts with:

```shell
python -m build --sdist --wheel --outdir /tmp/agentforge-package-dist
```

The refreshed isolated build completed after allowing access to PyPI for build-system requirements.

Results:

| Check | Result |
| --- | --- |
| Wheel artifact | `/tmp/agentforge-package-dist/agentforge-0.6.5-py3-none-any.whl` |
| Source artifact | `/tmp/agentforge-package-dist/agentforge-0.6.5.tar.gz` |
| Wheel setup YAML files | 38 files under `agentforge/setup_files/` |
| Sdist setup YAML files | 38 files under `src/agentforge/setup_files/` |
| Cache files | No `__pycache__`, `*.pyc`, or `*.pyo` files found in wheel or sdist |
| Console entry points | No `entry_points.txt` found in the wheel |
| Wheel metadata | Name `agentforge`, version `0.6.5`, license expression `GPL-3.0-or-later`, `Requires-Python: >=3.10`, Python classifiers 3.10 through 3.14 |
| Optional extras | Existing `other` extra preserved with `opencv-python` and `pytesseract` |

Representative setup resources verified in both artifacts:

- `setup_files/settings/system.yaml`
- `setup_files/settings/models.yaml`
- `setup_files/prompts/response_agent.yaml`
- `setup_files/cogs/example_cog.yaml`
- `setup_files/tools/read_file.yaml`
- `setup_files/actions/web_search.yaml`
- `setup_files/personas/default_assistant.yaml`

## Clean Install Evidence

Created a clean Python 3.14 venv at `/tmp/agentforge-package-install`, installed the built wheel with dependencies, and verified:

- `import agentforge` succeeds.
- `import agentforge.config` succeeds.
- Installed package metadata reports version `0.6.5`.
- `agentforge/setup_files/settings/system.yaml` is available through package resources.
- `python -m agentforge.init_agentforge` runs from a temporary project directory without a repo checkout on `sys.path`.
- The scaffold creates 38 YAML files under `.agentforge`, including representative settings, prompts, cogs, tools, actions, and personas.
- Running `python -m agentforge.init_agentforge` a second time skips identical files without prompting or rewriting them.
- `Config(root_path=...)`, `Config.reset(root_path=...)`, and `AGENTFORGE_ROOT` each load the scaffolded `.agentforge` root.
- `/tmp/agentforge-package-install/bin/agentforge` is absent.
- `pip check` reports no broken requirements.

The sandboxed dependency install cannot resolve PyPI without network access. After approving PyPI access, the wheel installed successfully with its dependencies.

## Editable Install Evidence

The local Python 3.14 `.venv` reports `agentforge` version `0.6.5` as an editable install with project location `/home/ansel/Projects/AgentForge`. Focused package, config, Ruff, and basedpyright checks ran through that environment.

## Remaining Risks

- The default install is still large because it includes Chroma, sentence-transformers, Torch/CUDA-selected packages, spaCy, provider SDKs, Discord, and media-related dependencies.
- Public install docs still need an update after package behavior stabilizes.
- A real public CLI or scaffold command has not been designed yet. Revisit it during beginner workflow work rather than restoring the broken historical console script.
- Live provider and service-backed workflows were not exercised by these package checks.
