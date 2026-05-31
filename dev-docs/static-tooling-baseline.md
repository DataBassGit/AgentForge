# Static Tooling Baseline

Developer-only snapshot of the repo's Ruff and basedpyright state. This is a current cleanup baseline, not project planning history.

## Tooling Context

- Python: the initial baseline used `venv/bin/python --version`, which reported `Python 3.13.13`; the repo-local development environment later moved to `.venv/` on Python 3.14.
- Ruff: the initial baseline used `venv/bin/ruff --version`, which reported `ruff 0.15.15`.
- basedpyright: the initial baseline used `basedpyright 1.39.6`.
- Config source: root `pyproject.toml`.
- Scope: `src` and `tests` for basedpyright; Ruff default discovery from the repo root.
- Dependency context: only Ruff and basedpyright were installed during the initial baseline, so missing-import diagnostics can include dependencies from the broader local development stack.

## Ruff Baseline

`ruff check .` runs and currently fails with 284 violations. Ruff reports 175 safe-fixable findings, with 5 additional hidden unsafe fixes available only if explicitly requested.

The repo now selects Ruff `UP045` so touched Python files use `T | None` instead of `Optional[T]`. This intentionally increases the full-repo baseline until older untouched modules are selected for cleanup.

| Rule | Count | Main meaning |
| --- | ---: | --- |
| `UP045` | 115 | `Optional[T]` annotations that should use `T | None`. |
| `E501` | 80 | Lines over the configured 120-character limit. |
| `F401` | 47 | Unused imports. |
| `E402` | 12 | Module-level imports after executable setup code. |
| `F541` | 10 | f-strings without placeholders. |
| `E701` | 8 | Multiple statements on one line after a colon. |
| `F841` | 6 | Assigned local variables never used. |
| `E722` | 3 | Bare `except`. |
| `F811` | 2 | Redefined names. |
| `PLR0913` | 1 | Function has more than 6 arguments. |

The single `PLR0913` finding is `src/agentforge/modules/actions.py:425`, where a function has 7 arguments and should be handled as a focused API/design cleanup rather than a formatting-only fix.

The highest-count category is now `UP045`, which should be burned down only when each older subsystem is already being touched. The original hotspots remain useful for orientation, but their counts should be refreshed after the next dedicated static cleanup pass.

`ruff format --check .` runs and currently reports 112 files that would be reformatted, with 21 files already formatted. Do not run broad formatting until a cleanup pass explicitly owns the resulting churn.

## Ruff Clean Scopes

Focused `ruff check` and `ruff format --check` currently pass for these selected file groups after applying formatting only to the files in each group:

- Selected config/Cog/core test files plus `src/agentforge/testing/bootstrap.py`.
- Selected storage/memory boundary files: `src/agentforge/core/memory_manager.py`, `src/agentforge/storage/memory.py`, `src/agentforge/storage/persona_memory.py`, `src/agentforge/storage/chat_history_memory.py`, `tests/memory_tests`, `tests/storage_tests/test_fake_chroma.py`, `tests/core_tests/test_memory_manager.py`, `tests/integration_tests/test_persona_memory_integration.py`, and `tests/integration_tests/test_example_cog_with_personamemory.py`.

## BasedPyright Baseline

`basedpyright --project pyproject.toml` runs and currently fails after analyzing 132 files, with 293 errors and 19 warnings.

| Rule | Count | Main meaning |
| --- | ---: | --- |
| `reportOptionalMemberAccess` | 95 | Values typed as possibly `None` are used without narrowing. |
| `reportMissingImports` | 65 | Imports cannot be resolved in the current environment. |
| `reportArgumentType` | 51 | Argument types do not match callable signatures. |
| `reportAttributeAccessIssue` | 47 | Accessed attributes are unknown for the inferred type. |
| `reportMissingModuleSource` | 19 | Installed or referenced modules lack analyzable source. |
| `reportReturnType` | 9 | Returned values do not match annotated return types. |
| `reportOptionalSubscript` | 7 | Values typed as possibly `None` are subscripted without narrowing. |
| `reportOperatorIssue` | 5 | Operators are used with incompatible inferred types. |
| `reportAssignmentType` | 4 | Assigned values do not match declared types. |
| `reportCallIssue` | 3 | Call shape cannot be proven compatible. |

Top basedpyright hotspots by path are `src/agentforge` with 222 diagnostics, `tests/cog_tests` with 22, `tests/config_tests` with 14, `tests/memory_tests` with 12, and `tests/utils` with 9. The highest-count individual files are `src/agentforge/storage/chroma_storage.py`, `src/agentforge/modules/actions.py`, `src/agentforge/agent.py`, `tests/cog_tests/test_cog_trail_logging_and_flow_validation.py`, and `src/agentforge/utils/discord/discord_utils.py`.

The missing-import group should be interpreted carefully until the dependency and package workflow align the development environment. The optional-member and dynamic-attribute findings are more useful cleanup signals for Agent, Cog, Config, storage, memory, and test fixture boundaries.

## BasedPyright Clean Scopes

Focused basedpyright currently passes for these selected file groups without suppressions:

- Selected config/Cog/core tests and neighboring files after adding explicit narrowing and keeping invalid test input marked as intentionally untyped.
- Selected storage/memory boundary files after chat-history access narrowing, memory storage/collection typing, `T | None` annotations in touched memory classes, structured `CogConfig` handling in `PersonaMemory`, and tests that use production attributes rather than dynamic test-only attributes.

## Cleanup Staging Notes

Start cleanup by subsystem rather than by tool. Good next cuts are unused imports and line length in one owned subsystem, the one `PLR0913` signature outlier, optional narrowing in Agent/Cog/Config flow outside the already-clean selected scopes, and dynamic test fixture attributes that basedpyright cannot currently prove.

Storage/memory still has larger cleanup candidates outside the current clean scope: Chroma storage typing and recovery scripts, ScratchPad shape and ownership, retrieval ownership boundaries, storage privacy/data-retention policy, and whether memory formatting helpers should stay as framework defaults or move closer to consumers.

Do not add a basedpyright baseline suppression file yet. The current report is intentionally visible so later cleanup work can choose which categories become enforced and which require environment or typing-policy decisions first.
