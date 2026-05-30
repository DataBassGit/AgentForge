# Core Coding Philosophy

This is AgentForge's local adaptation of the shared Abode coding philosophy. It
is the default review standard for cleanup, feature work, tests, and developer
docs in this repository.

## Core Philosophy

Optimize for human-readable flow. A reader should be able to scan the top-level
structure, understand the execution path, and open focused helpers only when
they need implementation detail.

The body is the outline. If an orchestration method cannot be understood from
its named steps, the steps are misnamed, misplaced, or doing too much.

AgentForge already follows this shape in places such as `Agent.run()`,
`Cog.run()`, `AgentRunner`, `MemoryManager`, and `TransitionResolver`. Continue
that direction.

## Structure

- Keep public entry points and high-level orchestration near the top of a file.
- Use focused helpers when they name real responsibilities, hide complexity,
  create a testable boundary, or make the flow easier to scan.
- Inline helpers that only forward to another helper without adding a useful
  concept.
- Consolidate real duplication in validation rules, config normalization,
  provider parameter handling, storage setup, prompt/parsing helpers, and test
  fixtures.
- Avoid abstracting coincidental similarity. If two blocks only look alike but
  serve different responsibilities, keep them local until the shared contract is
  real.
- Keep control flow shallow with guard clauses, early returns, lookup maps,
  dispatch helpers, and named policy helpers where they improve readability.
- Avoid using Python `match` as a broad switch-statement replacement. Prefer
  explicit helpers, dictionaries, or strategy boundaries when branching grows.

## Local Python Style

Match the style of the file being edited. Most Python files in this repository
use standard 4-space indentation; do not reindent touched files just to satisfy
an external preference.

Use `snake_case` for functions and variables, `PascalCase` for classes, and
`UPPER_CASE` for constants.

Public classes, public methods, and nontrivial private helpers should usually
have short docstrings. Prefer one useful sentence. Add Args or Returns sections
only when they clarify something the signature does not.

Use inline comments sparingly. A comment should explain why a decision exists,
what invariant is being protected, or why ordering matters. If a comment only
restates the next line, improve the name or structure instead.

## Boundaries

Validate at framework boundaries: config loading, YAML schema normalization,
provider parameter filtering, file-system paths, storage setup, and public
entry points. Once validation establishes an assumption, downstream code should
not keep rediscovering it.

Keep providers replaceable. Provider-specific request details, retry decisions,
response extraction, and credential diagnostics should stay inside provider
classes or shared provider helpers.

Keep consumer data and product decisions outside the library. The framework can
offer extension points and reusable patterns, but application-owned prompts,
personas, memory content, and workflow authority should remain application
owned.

Keep setup-file changes intentional. Anything under
`src/agentforge/setup_files/` can be copied into user `.agentforge/` projects,
so default YAML changes are public behavior changes.

## File Size And Navigation

Use file size as a review prompt, not a rigid rule.

- Around 600 lines, assess whether a clearer module boundary or helper module
  would improve navigation.
- Around 800+ lines, avoid adding meaningful new behavior without extracting a
  responsibility or recording why local growth is clearer for this change.
- Existing oversized files do not need emergency cleanup, but touched areas
  should become easier to read when practical.

For files with multiple responsibilities, use short section comments that match
local style. Do not add ceremony to tiny single-purpose files.

## Tests

Test at the boundary where breakage matters. Prefer a focused unit test for
pure behavior, an integration-style test for wiring/config/data flow, and a
live test only when the behavior cannot be proven with fakes.

Test code should follow the same readability standard: scenario, action, and
expected behavior should be easy to scan, while noisy setup lives in fixtures or
well-named helpers.

Do not keep tests that no longer assert supported behavior. Update or retire
tests when the contract changes, and explain the new contract in the relevant
doc or test name.

## Cleanup Discipline

Refactoring toward clarity is not rollback. It is fine to simplify wiring,
reorganize method groups, or remove ceremony while preserving boundaries and
testability.

Do not combine broad style cleanup with behavior changes. If a task requires
both, isolate mechanical edits from semantic edits so reviewers can tell what
changed.

Before finishing, ask:

- Does the top-level flow read like an execution index?
- Did the change use or improve the right validation boundary?
- Are provider, config, memory, prompt, and parsing responsibilities still
  separate?
- Are tests focused on the risk introduced?
- Did docs stay concise and close to the decision they explain?
