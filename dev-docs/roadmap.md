# Roadmap

This roadmap records current development direction so cleanup work does not block likely future features. It is not a release promise and should stay grounded in reusable framework needs.

## Near-Term Cleanup

Modernize AgentForge into a stable library dependency before downstream projects rely on fragile local-checkout behavior.

Current cleanup work should prioritize:

- package metadata, dependency, and supported-Python alignment;
- reproducible local development and install workflows;
- setup-file defaults that avoid spreading invalid or unsupported parameters;
- provider configuration and diagnostics;
- current local and cloud provider compatibility for prominent model families;
- graceful handling of text, image, audio-input, and audio-output modalities;
- structured-output failure messages;
- code and logic quality issues that indicate outdated libraries, real bugs, bad architecture, or unclear ownership;
- focused regression coverage around providers, memory, configuration, and Cog execution.

Avoid choices that make AgentForge depend on one consumer project's folder shape, credentials, prompts, or persistence policy.

## Beginner Workflow Documentation

After the stable cleanup baseline, public docs should help a new user move from installation to a direct Agent run and then to a small multi-agent Cog workflow.

Current developer docs should not become a substitute for public beginner docs. When public examples are added, keep them small, runnable, and independent from private project notes.

## Prompt And Tooling Direction

Advanced prompt templating may grow beyond the current placeholder renderer. Jinja-capable templating is a possible direction, but it should be introduced as a clear framework feature with escaping, missing-value behavior, and migration expectations documented.

Tools and Actions are deprecated and should eventually be replaced by a supported modern surface, likely influenced by MCP-style tool contracts. Until that direction is explicit, preserve compatibility and avoid deepening the legacy API unnecessarily.

Other development is currently happening on Tools/Actions and MCP support on the `dev` branch. Cleanup work on this branch should avoid that section until branches are ready to reconvene.

## Provider Integrations

Provider work should expand where concrete use cases justify maintenance cost. Every provider path should have:

- documented configuration expectations;
- parameter filtering or validation at the provider boundary;
- actionable authentication and empty/malformed-response diagnostics;
- tests that avoid live network calls unless live behavior is the contract.

Do not add broad provider abstractions before repeated needs are visible across multiple providers.

## Modalities

AgentForge already has text, audio-input, audio-output, and basic image/vision paths. Modernization should make those paths graceful and explicit: unsupported modalities should fail clearly, supported modalities should have provider-specific request/response tests, and setup defaults should not imply capabilities that the provider path cannot actually handle.

Vision support is still rudimentary and should be reviewed as part of provider modernization. Image generation is a future feature and should be tracked as roadmap direction only during the current cleanup pass unless a separate implementation effort explicitly scopes it.

## Memory, Retrieval, And Runtime Patterns

Memory and retrieval features should grow carefully. AgentForge can offer storage primitives, declarative memory nodes, and retrieval hooks, but consumer applications must retain authority over data ownership, retention, filtering, and whether retrieved content is allowed to affect product decisions.

Future runtime patterns may include clearer launch/deployment workflows, consumer-owned workflow packaging, or richer persisted execution trails. These should be added only when shared consumer needs are concrete.

## Security And Privacy Baseline

AgentForge does not need enterprise-scale security process before cleanup can continue, but it should maintain a practical minimum baseline. Cleanup work should review input and output validation, temporary-file cleanup, path handling, credential handling, logging redaction, provider payload construction, and any setting that claims to protect privacy.

Privacy settings should correspond to real behavior. If a setting disables logging, memory, persistence, external calls, or audio/file retention, tests or focused inspection should prove the sensitive path is actually disabled or clearly document the remaining limitation.

## Design Constraints For Current Work

- Keep `.agentforge/` a consumer-owned configuration boundary.
- Keep setup defaults conservative because they propagate to new projects.
- Keep provider-specific behavior behind provider classes.
- Keep Cog flow decisions declarative where possible.
- Keep tests fast and fake-backed by default.
- Keep dev-only documentation outside `docs/` unless intentionally made public.
- Keep public docs updates for cleanup closure once code behavior has stabilized.
