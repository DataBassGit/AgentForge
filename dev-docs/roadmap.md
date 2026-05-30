# Roadmap

This roadmap records current development direction so cleanup work does not
block likely future features. It is not a release promise and should stay
grounded in reusable framework needs.

## Near-Term Cleanup

Modernize AgentForge into a stable library dependency before downstream
projects rely on fragile local-checkout behavior.

Current cleanup work should prioritize:

- package metadata, dependency, and supported-Python alignment;
- reproducible local development and install workflows;
- setup-file defaults that avoid spreading invalid or unsupported parameters;
- provider configuration and diagnostics;
- structured-output failure messages;
- focused regression coverage around providers, memory, configuration, and Cog
  execution.

Avoid choices that make AgentForge depend on one consumer project's folder
shape, credentials, prompts, or persistence policy.

## Beginner Workflow Documentation

After the stable cleanup baseline, public docs should help a new user move from
installation to a direct Agent run and then to a small multi-agent Cog workflow.

Current developer docs should not become a substitute for public beginner docs.
When public examples are added, keep them small, runnable, and independent from
private project notes.

## Prompt And Tooling Direction

Advanced prompt templating may grow beyond the current placeholder renderer.
Jinja-capable templating is a possible direction, but it should be introduced as
a clear framework feature with escaping, missing-value behavior, and migration
expectations documented.

Tools and Actions are deprecated and should eventually be replaced by a
supported modern surface, likely influenced by MCP-style tool contracts. Until
that direction is explicit, preserve compatibility and avoid deepening the
legacy API unnecessarily.

## Provider Integrations

Provider work should expand where concrete use cases justify maintenance cost.
Every provider path should have:

- documented configuration expectations;
- parameter filtering or validation at the provider boundary;
- actionable authentication and empty/malformed-response diagnostics;
- tests that avoid live network calls unless live behavior is the contract.

Do not add broad provider abstractions before repeated needs are visible across
multiple providers.

## Memory, Retrieval, And Runtime Patterns

Memory and retrieval features should grow carefully. AgentForge can offer
storage primitives, declarative memory nodes, and retrieval hooks, but consumer
applications must retain authority over data ownership, retention, filtering,
and whether retrieved content is allowed to affect product decisions.

Future runtime patterns may include clearer launch/deployment workflows,
consumer-owned workflow packaging, or richer persisted execution trails. These
should be added only when shared consumer needs are concrete.

## Design Constraints For Current Work

- Keep `.agentforge/` a consumer-owned configuration boundary.
- Keep setup defaults conservative because they propagate to new projects.
- Keep provider-specific behavior behind provider classes.
- Keep Cog flow decisions declarative where possible.
- Keep tests fast and fake-backed by default.
- Keep dev-only documentation outside `docs/` unless intentionally made public.
