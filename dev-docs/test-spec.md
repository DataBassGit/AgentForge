# Test Specification

This document defines how to manage tests in AgentForge. It should be read
together with `core-coding-philosophy.md`.

## Test Layout

The test suite is organized by responsibility:

- `tests/agent_tests/`: direct `Agent` behavior and output parsing.
- `tests/apis_tests/`: provider runtime and provider-specific behavior.
- `tests/auth_tests/`: authentication helpers such as Codex OAuth.
- `tests/cog_tests/`: Cog orchestration, trails, flow validation, and
  agent-runner integration.
- `tests/config_tests/`: config loading, validation, and setup-file behavior.
- `tests/core_tests/`: core orchestration helpers.
- `tests/integration_tests/`: integration-marked framework behavior.
- `tests/memory_tests/`: memory surfaces and persona memory.
- `tests/multimedia_tests/`: image/audio modality support.
- `tests/storage_tests/`: storage fakes and storage boundary behavior.
- `tests/utils/`: shared test fakes and utility processor tests.
- `tests/real_tests/`: manual/live scripts that can call real providers.

Add new tests near the behavior they protect. Create a new folder only when a
new responsibility is large enough to be navigated separately.

## Default Test Policy

The default suite excludes `integration` tests through `pytest.ini`. Most
changes should be verified with targeted tests plus, when appropriate, the
default suite:

```shell
python -m pytest tests/path/to/test_file.py
python -m pytest
```

Use focused path runs during development. Use the full default suite when a
change touches shared config, Cog execution, provider base behavior, memory
interfaces, parsing, or setup files.

## Fakes And Fixtures

Prefer fakes for provider, storage, and network behavior. The default test
bootstrap can replace Chroma storage with `FakeChromaStorage` and stub
`Agent.run` so tests do not call live models.

Use `isolated_config` when a test needs to modify `.agentforge` files. It
copies setup files to a temporary directory and resets `Config` to that root.

Do not mutate shipped setup files or repo-root `.agentforge` resources in tests
unless the test owns cleanup. If a test writes YAML, write it into a temporary
`.agentforge` tree.

## When To Add Tests

Add or update tests when a change affects:

- YAML schema validation or normalization;
- setup files copied into consumer projects;
- provider request shape, parameter filtering, response parsing, or errors;
- prompt rendering or output parsing;
- Cog transition behavior, end-result extraction, trail logging, or memory
  triggers;
- storage semantics or memory update/query contracts;
- public extension points or subclass behavior;
- a bug that could regress silently.

Docs-only changes usually do not need pytest. Validate links, paths, and
rendering assumptions with targeted inspection.

## Test Shape

Make each test easy to scan:

1. Arrange the smallest realistic config or object graph.
2. Act through the public or subsystem boundary that matters.
3. Assert the observable behavior or error contract.

Keep noisy setup in fixtures or named helpers. Avoid repeating YAML construction
blocks across many tests when one helper can express the scenario clearly.

Prefer asserting behavior over implementation details. It is okay to assert
provider request shape, normalized dataclass fields, or logged/raised diagnostic
messages when those are the contract under test.

## Integration And Live Tests

Mark tests with `@pytest.mark.integration` when they require heavier wiring,
real local services, or slower cross-component behavior. They are skipped by
default.

Manual live scripts under `tests/real_tests/` can use real providers and
credentials. Do not make routine tests depend on API keys, OAuth state, running
Ollama/LM Studio instances, Discord tokens, Chroma HTTP servers, or network
access.

When adding a live path, also add fake-backed coverage for the reusable
framework behavior where practical.

## Updating Or Retiring Tests

Update tests when the supported contract changes. Do not preserve stale tests
by weakening assertions until they pass; make the new behavior explicit in the
test name, setup, and assertions.

Delete tests when they cover behavior that is no longer supported and no longer
guards a compatibility promise. If deletion removes the only coverage for a
nearby supported behavior, replace it with a focused current test in the same
change.

When retiring deprecated Tools/Actions behavior, keep compatibility tests only
for the behavior the project still intends to support during the transition.

## Acceptance Checklist

Before finishing a code change:

- The touched behavior has focused tests at the right boundary.
- Tests avoid live services unless live behavior is the point.
- Config tests use isolated `.agentforge` resources.
- Provider tests cover both success and useful failure diagnostics.
- Setup-file changes have tests that prove copied defaults still load.
- Deleted or changed tests reflect a documented contract change.
