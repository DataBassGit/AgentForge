# First Real Model Run

This page is the second stop in the beginner documentation path.

The full real-provider walkthrough belongs here.

For now, this page records the credential boundary and expected continuation without adding the runnable provider example yet.

## What Changes After Debug Mode

Debug mode proves that AgentForge can load your project resources and run without provider credentials.

A real model run changes only the provider boundary: AgentForge will call the configured model instead of returning a simulated response.

## Current Scaffold Default

The current scaffold's default model points at Gemini.

That means a real cloud call requires `GOOGLE_API_KEY` unless you edit `.agentforge/settings/models.yaml` to choose a different provider or model.

OpenAI and Anthropic require their own API keys.

Ollama and LM Studio do not require cloud API keys, but they do require the matching local service and model to be running.

## Keep The First Provider Step Small

The beginner real-model guide should show one short continuation from the direct Agent quickstart, then mention provider alternatives without becoming a provider matrix.

For detailed settings reference, use [Model Settings](../settings/models.md) after the first real call works.

## Next

- Continue to [Core Concepts](core_concepts.md) to understand how prompts, settings, and Agents fit together.
- Use [Advanced Reference](advanced_reference.md) for custom APIs, model overrides, and provider-specific reference material.
