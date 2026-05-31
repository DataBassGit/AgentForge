# Static Tooling Baseline

Developer-only snapshot of the repo's Ruff and basedpyright state. This is a current cleanup baseline, not project planning history.

## Tooling Context

- Python: repo-local development uses `.venv/` on Python 3.14.
- Ruff: `.venv/bin/ruff --version` reports `ruff 0.15.15`.
- basedpyright: `.venv/bin/basedpyright --version` reports `basedpyright 1.39.6`.
- Config source: root `pyproject.toml`.
- Ruff scope: default discovery from the repo root.
- basedpyright scope: `src` and `tests` through `pyproject.toml`.

## Current Baseline

The full repo static baseline is clean:

```shell
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/basedpyright --project pyproject.toml
```

Expected results:

| Check | Expected result |
| --- | --- |
| Ruff lint | `All checks passed!` |
| Ruff format | `135 files already formatted` |
| basedpyright | `0 errors, 0 warnings, 0 notes` |

Ruff safe fixes and formatting have been applied across the current Python tree. basedpyright cleanup uses normal type narrowing where practical and targeted inline ignores only for optional or dynamic integration surfaces where a real fix would require dependency, API, or legacy behavior design.

## Enforcement

The tracked pre-push hook now runs full static checks instead of checking only pushed Python files:

```shell
ruff check .
ruff format --check .
basedpyright --project pyproject.toml
python -m pytest
```

This means new Python changes should keep the whole configured tree clean, not just the files being pushed. Keep `pyproject.toml` as the source of truth for Ruff and basedpyright settings.

## Remaining Static-Adjacent Risks

Some cleaned areas still contain deferred architecture questions. The static pass intentionally does not redesign logger behavior, storage and retrieval ownership, dependency slimming, public documentation, or the legacy Tools/Actions surface.

Targeted inline ignores remain only where the runtime surface is intentionally dynamic or optional, such as optional Docker/LiteLLM/NaCl/DAVE imports and dynamic spaCy, Discord, or legacy storage attributes. Revisit those ignores when the corresponding subsystem is redesigned or made optional through supported extras.
