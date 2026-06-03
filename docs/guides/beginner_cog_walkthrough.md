# Beginner Cog Walkthrough

This page is the fourth stop in the beginner documentation path.

The full beginner Cog example belongs here.

For now, this page establishes the expected learning order without adding the runnable Cog walkthrough yet.

## What The First Cog Should Teach

The first Cog should show how AgentForge moves from one direct Agent to a small declarative workflow.

It should stay no-memory and avoid personas, storage tuning, subclass hooks, custom APIs, and legacy Tools/Actions.

A good first shape is a simple two-step flow such as `summarize -> respond` or `classify -> respond`.

## What A Beginner Should Notice

- Cogs live under `.agentforge/cogs/`.
- Cog nodes point at prompt templates under `.agentforge/prompts/`.
- A short Python script imports `Cog`, creates the named workflow, calls `run(...)`, and prints the result.
- Branching, loops, memory, and return-value rules can wait until the simple flow works.

## Next

- Use [Cogs](../cogs/cogs.md) for the full schema reference after the beginner walkthrough exists.
- Use [Advanced Reference](advanced_reference.md) when you are ready for branch/loop Cogs, memory, personas, and storage-backed workflows.
