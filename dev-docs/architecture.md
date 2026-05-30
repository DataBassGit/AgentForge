# AgentForge Architecture

This document is developer-facing architecture guidance for local work in the AgentForge repository. It describes durable design shape and extension boundaries. User-facing explanations belong in `README.md` and `docs/`.

## System Role

AgentForge is a Python library for building agents and Cog workflows from project-owned `.agentforge/` resources. The framework owns reusable runtime machinery: configuration loading, prompt rendering, provider calls, parsing, memory integration, and Cog orchestration. Applications own their product workflows, prompt content, credentials, personas, and persisted data.

Keep that boundary clear. A consumer project can expose a reusable framework gap, but consumer-specific behavior should not become library default behavior without a general AgentForge contract.

## Main Components

`Config` is the process-wide configuration loader. It discovers a project root, loads YAML from `.agentforge/`, resolves model/provider configuration, imports built-in or custom provider classes, resolves personas, and builds structured agent and Cog configuration through `ConfigManager`.

`ConfigManager` validates and normalizes raw YAML dictionaries into dataclasses under `src/agentforge/config_structs/`. It is the boundary where config shape should become explicit. Avoid scattering schema assumptions across runtime classes when they belong in validation or normalization.

`Agent` is the single-agent execution template. Its public `run()` flow loads data, processes inputs, renders prompts, calls the configured model, parses the result, runs post-processing hooks, and builds output. Subclasses should override the named extension points instead of replacing the whole flow.

`Cog` orchestrates multi-agent workflows. It loads a Cog config, builds agent instances through `AgentRegistry`, prepares memory through `MemoryManager`, executes agents through `AgentRunner`, routes transitions through `TransitionResolver`, records optional trail data, and returns the final result defined by the flow end condition.

`BaseModel` and provider classes under `src/agentforge/apis/` own model API request/response details. Shared retry, modality validation, prompt part building, and parameter filtering live in `BaseModel`; provider-specific request shape and response extraction live in subclasses.

`PromptProcessor` renders AgentForge prompt templates and nested placeholders from context/state/memory data. `ParsingProcessor` parses model outputs into supported structured formats with code-fenced parsing followed by bare parsing fallback.

Storage and memory code under `src/agentforge/storage/` provides reusable memory surfaces, Chroma-backed storage, chat history, scratchpad, and persona memory. Memory nodes are declared in Cog YAML and mediated through `MemoryManager`.

## Configuration Model

AgentForge reads consumer resources from `.agentforge/`, usually scaffolded from `src/agentforge/setup_files/`.

The important categories are:

- `settings/`: system, model, and storage defaults.
- `prompts/`: agent prompt templates.
- `cogs/`: declarative multi-agent workflows.
- `personas/`: optional persona content and defaults.
- `custom_apis/`: consumer-provided provider modules.
- `tools/` and `actions/`: deprecated surfaces retained for compatibility.

Project root discovery uses this precedence:

1. Explicit `Config(root_path=...)` or `Config.reset(root_path=...)`.
2. `AGENTFORGE_ROOT`.
3. Auto-discovery walking upward from the running script.

For tests and scripts, prefer explicit roots or the test bootstrap helper over depending on incidental current working directory behavior.

## Runtime Flow

A direct `Agent` run follows this shape:

1. `Config` loads prompt/settings/model/persona data for the agent.
2. `Agent.load_data()` merges runtime keyword arguments into template data.
3. `PromptProcessor` renders `system` and `user` prompts.
4. The configured provider generates a response through `BaseModel.generate()`.
5. `ParsingProcessor` parses the response when `parse_response_as` is set.
6. The agent returns `output`.

A `Cog` run follows this shape:

1. `Config` loads and validates Cog YAML.
2. `AgentRegistry` creates agent instances for Cog agent definitions.
3. `MemoryManager` creates configured memory nodes and optional chat history.
4. `TransitionResolver` starts at `flow.start` and determines each next agent.
5. `AgentRunner` executes each agent with `_ctx`, `_state`, and `_mem`.
6. `MemoryManager` performs configured pre-query and post-update operations.
7. `TrailRecorder` records execution data when enabled.
8. `Cog` returns the configured end result or full state.

## Extension Boundaries

Add new agent behavior by subclassing `Agent` and overriding focused extension points such as `load_additional_data`, `process_data`, `post_process_result`, or `build_output`.

Add new provider behavior by implementing a provider class under `src/agentforge/apis/` or a consumer custom API module. Keep provider-specific parameters, request shape, response extraction, and credential errors inside the provider boundary.

Add new Cog routing behavior in `TransitionResolver` only when it is a reusable workflow contract. Keep product-specific decisions in agent output and Cog YAML.

Add new memory behavior behind a memory class and config definition. Preserve consumer ownership of data, filters, and authority decisions.

When changing YAML schemas, update validation, dataclasses, setup files, docs, and tests together. Schema drift is expensive in this repo because many features are configured declaratively.

## Current Architecture Risks

- Package metadata now lives in `pyproject.toml`, but public install docs and local requirements still need a phase-closing alignment pass. Do not use one source as proof that the others are correct during cleanup.
- AgentForge does not currently install a public `agentforge` console command. Use `python -m agentforge.init_agentforge` for setup scaffolding unless a later workflow phase adds a real CLI.
- Some public docs still describe deprecated Tools/Actions. Preserve compatibility while future work defines the MCP-oriented replacement.
- Provider failures now have a first diagnostic baseline: unsupported modalities name requested/supported capabilities, missing API keys fail before network calls for key-based cloud providers, and malformed or empty provider responses use `ModelResponseError`. Live provider behavior is still unverified, so avoid adding new provider paths without focused failure tests and an explicit live-check decision.
