# Package Install Baseline

Recorded 2026-05-30 for Phase 1, Session 4. This is developer-only package and install evidence, not public install documentation.

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
python -m build --sdist --wheel --outdir /tmp/agentforge-session4-dist
```

Results:

| Check | Result |
| --- | --- |
| Wheel artifact | `/tmp/agentforge-session4-dist/agentforge-0.6.5-py3-none-any.whl` |
| Source artifact | `/tmp/agentforge-session4-dist/agentforge-0.6.5.tar.gz` |
| Wheel setup YAML files | 38 files under `agentforge/setup_files/` |
| Sdist setup YAML files | 38 files under `src/agentforge/setup_files/` |
| Cache files | No `__pycache__`, `*.pyc`, or `*.pyo` files found in wheel or sdist |
| Console entry points | No `entry_points.txt` found in the wheel |
| Wheel metadata | Name `agentforge`, version `0.6.5`, license expression `GPL-3.0-or-later`, `Requires-Python: >=3.10`, Python classifiers 3.10 through 3.14 |
| Optional extras | Existing `other` extra preserved with `opencv-python` and `pytesseract` |

Representative setup resources verified in both artifacts:

- `setup_files/settings/system.yaml`
- `setup_files/prompts/response_agent.yaml`
- `setup_files/cogs/example_cog.yaml`

## Clean Install Evidence

Created a clean Python 3.14 venv at `/tmp/agentforge-session4-install`, installed the built wheel with dependencies, and verified:

- `import agentforge` succeeds.
- `import agentforge.config` succeeds.
- Installed package metadata reports version `0.6.5`.
- `agentforge/setup_files/settings/system.yaml` is available through package resources.
- `python -m agentforge.init_agentforge` copies `.agentforge/settings/system.yaml`, `.agentforge/prompts/response_agent.yaml`, and `.agentforge/cogs/example_cog.yaml` in a temporary project directory.
- `/tmp/agentforge-session4-install/bin/agentforge` is absent.
- `pip check` reports no broken requirements.

The first clean-install attempt hit local disk quota because older temporary compatibility venvs were still present. After removing those generated temp directories, the same wheel install passed; this was an environment space issue rather than a package metadata failure.

## Remaining Risks

- The default install is still large because it includes Chroma, sentence-transformers, Torch/CUDA-selected packages, spaCy, provider SDKs, Discord, and media-related dependencies.
- Public install docs were intentionally not updated during this session; they still need the Phase 1 closure pass after package behavior stabilizes.
- A real public CLI or scaffold command has not been designed yet. Revisit it during beginner workflow work rather than restoring the broken historical console script.
- Live provider and service-backed workflows were not exercised by these package checks.
