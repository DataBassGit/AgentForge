# Core Concepts

This page follows the first direct Agent runs.

It gives the mental model before the reference pages introduce schemas, memory, storage, subclass hooks, and legacy compatibility surfaces.

## Agent

An Agent is the smallest useful AgentForge unit.

It loads a prompt template from `.agentforge/prompts/`, resolves model settings, renders prompt variables, calls a provider or debug response, and returns the result.

The direct Agent path is the first beginner workflow because it has the fewest moving pieces.

## Prompt Template

Prompt templates are YAML files under `.agentforge/prompts/`.

They define the system and user prompt sections an Agent renders at runtime.

The detailed prompt reference lives in [Agent Prompts](../agents/agent_prompts.md).

## Settings

Settings live under `.agentforge/settings/`.

Beginners mostly need `system.yaml` for the debug smoke test and `models.yaml` for the provider used after debug mode.

The detailed settings reference lives in [Settings](../settings/settings.md).

## Cog

A Cog is a YAML workflow under `.agentforge/cogs/`.

It connects one or more Agents into a declarative flow with transitions, branching, optional memory, and return-value rules.

The beginner Cog path should start with a small no-memory workflow before adding branch/loop behavior.

## Advanced Context Systems

Memory, personas, storage internals, custom APIs, custom Agents, utilities, and legacy Tools/Actions are useful after the basic Agent and Cog flow works.

Use [Advanced Reference](advanced_reference.md) when you are ready for those surfaces.

## Navigation

- Previous: [First Real Model Run](first_real_model_run.md)
- Start: [AgentForge Documentation](../README.md)
- Continue to [Beginner Cog Walkthrough](beginner_cog_walkthrough.md).
- Open the [Agents](../agents/agents.md) and [Cogs](../cogs/cogs.md) references after the beginner examples are clear.
