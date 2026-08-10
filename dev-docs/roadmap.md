# Roadmap

This roadmap records current development direction for AgentForge.
It is not a release promise or task list; it is a durable guide for choices that affect the library's shape.

AgentForge should remain an independent orchestration framework for consumer-owned `.agentforge/` resources, prompt templates, provider configuration, memory surfaces, and Cog workflows.
Avoid choices that make the library depend on one consumer project's folder shape, credentials, prompts, persistence policy, or product workflow.

## Onboarding And Setup Defaults

Public docs should keep the first user path small: scaffold `.agentforge/`, run a no-credential debug smoke test, then use the default Codex OAuth real-model path before branching into optional providers.

The shipped setup files should stay conservative because they propagate into new projects.
Defaults should prefer valid, documented behavior with clear authentication requirements.
AgentForge should continue using explicit module commands such as `python -m agentforge.init_agentforge` and `python -m agentforge.init_codex_oauth`; a broad public CLI should be added only if concrete workflow needs justify it.

Starter templates and UI-oriented setup may become useful later, but they should not force a rename or relocation of `src/agentforge/setup_files/` until the consumer experience is concrete.

## Prompt And Tooling Direction

Advanced prompt templating may grow beyond the current placeholder renderer.
Jinja-capable templating is a possible direction, but it should be introduced as a clear framework feature with escaping, missing-value behavior, and compatibility expectations documented.

Tools and Actions are legacy compatibility surfaces.
They should eventually be replaced by a supported modern interface, likely influenced by MCP-style tool contracts.
Until that direction is explicit, preserve compatibility for trusted project-owned definitions and avoid deepening the legacy API unnecessarily.

## Provider Integrations And Modalities

Provider work should expand where concrete use cases justify maintenance cost.
Every provider path should have documented configuration expectations, parameter filtering or validation at the provider boundary, actionable authentication diagnostics, and focused tests that avoid live network calls unless live behavior is the contract.

AgentForge already has text, audio-input, audio-output, and basic image/vision paths.
Unsupported modalities should fail clearly, supported modalities should have provider-specific request/response tests, and setup defaults should not imply capabilities that the provider path cannot actually handle.

Do not add broad provider abstractions before repeated needs are visible across multiple providers.
Do not add broad image-generation promises until provider modality requirements and ownership boundaries are explicitly scoped.

## Memory, Retrieval, And Runtime Patterns

Memory and retrieval features should grow carefully.
AgentForge can offer storage primitives, declarative memory nodes, retrieval hooks, and execution trail data, but consumer applications must retain authority over data ownership, retention, filtering, and whether retrieved content is allowed to affect product decisions.

Future runtime patterns may include clearer launch/deployment workflows, consumer-owned workflow packaging, richer persisted execution trails, or starter-project generation.
Add those surfaces only when shared consumer needs are concrete.

## Security, Privacy, And Logging

AgentForge should strive for a practical security and privacy baseline.

Privacy settings should correspond to real behavior.
If a setting disables logging, memory, persistence, external calls, or audio/file retention, tests or focused inspection should prove the sensitive path is actually disabled or clearly document the limitation.

Logger behavior should become simpler and more explicit over time.
Runtime category creation, settings-file mutation, model I/O logging, and redaction defaults should be treated as design decisions that need docs and tests before they become durable public contracts.

## Dependencies And Packaging

AgentForge should keep package metadata, supported Python versions, setup-file inclusion, and installation workflows aligned.
Heavy dependencies such as Chroma, sentence-transformers, Torch/CUDA-selected packages, spaCy, provider SDKs, Discord, and media libraries should move behind optional extras or lazy import boundaries when that can be done without breaking supported workflows.

Local developer tooling belongs in development requirements.
Runtime library dependencies belong in package metadata only when normal users need them for supported behavior.

## Design Constraints

- Keep `.agentforge/` a consumer-owned configuration boundary.
- Keep setup defaults valid, documented, and conservative.
- Keep provider-specific behavior behind provider classes.
- Keep Cog flow decisions declarative where possible.
- Keep tests fast and fake-backed by default.
- Keep dev-only documentation outside `docs/` unless intentionally made public.
- Keep public docs aligned with current supported behavior.
