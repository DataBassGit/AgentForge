# AgentForge Agent Guide

This file is the entrypoint for agents and developers working in this repository. It is local developer guidance, not user-facing package documentation. Keep public install and usage documentation in `README.md` and the existing `docs/` tree.

## Documentation Map

- `dev-docs/architecture.md` explains the main runtime components and extension boundaries.
- `dev-docs/core-coding-philosophy.md` defines the project coding standard for cleanup and feature work.
- `dev-docs/environment.md` covers local setup, the repo `.venv`, requirements, `.agentforge` discovery, and test execution.
- `dev-docs/package-install-baseline.md` records the current package metadata, artifact, and clean-install evidence.
- `dev-docs/pipeline-config-graph.md` gives the high-level data-flow map and a Mermaid graph.
- `dev-docs/python-compatibility-baseline.md` records the current Python 3.14 compatibility evidence.
- `dev-docs/roadmap.md` summarizes future direction that should shape current decisions.
- `dev-docs/static-tooling-baseline.md` records the current Ruff and basedpyright baseline for staged cleanup work.
- `dev-docs/test-review-baseline.md` records the current deterministic test-review baseline and first cleanup actions.
- `dev-docs/test-spec.md` describes how to create, update, organize, retire, and run tests.

Do not move these files into `docs/` unless the project intentionally decides they should become public documentation. The current `docs/` folder is used by the hosted documentation navigator.

## Working Rules

- Read the relevant `dev-docs/` page before changing a subsystem.
- Keep edits scoped to the requested work and the nearby code required to make that work coherent.
- Preserve public behavior unless the task explicitly asks for a public contract change.
- Prefer existing AgentForge patterns over introducing new framework shape.
- Keep consumer-owned configuration, prompts, personas, memory data, and product workflows out of the library unless they reveal a reusable framework need.
- When a change affects architecture, testing policy, local setup, or roadmap assumptions, update the corresponding `dev-docs/` page in the same change.

## Local Environment

The repository currently uses a local `.venv/` with Python 3.14. Use it for repo-local checks when available:

```shell
source .venv/bin/activate
python -m pytest
```

The default `pytest.ini` excludes tests marked `integration`. Use targeted test paths for focused changes, for example:

```shell
python -m pytest tests/core_tests/test_transition_resolver.py
```

See `dev-docs/environment.md` and `dev-docs/test-spec.md` before running live provider, audio, Discord, or storage checks.

## Change Discipline

- Start with `git status --short` and do not overwrite unrelated local changes.
- Prefer `rg` and `rg --files` for search.
- Use `apply_patch` for manual file edits.
- Do not run formatters or code generators that rewrite broad areas unless the task calls for that exact cleanup.
- Keep developer Markdown prose as one line per sentence or paragraph; do not hard-wrap prose to a fixed column. Preserve code blocks, tables, headings, links, frontmatter, and list structure when normalizing Markdown.
- For docs-only changes, validate links and paths with targeted inspection; do not run the full test suite unless runtime code changed.
