# Beginner Cog Walkthrough

This guide continues after the direct Agent path works.

It runs a tiny no-memory Cog that does two things: `summarize -> respond`.

The example uses debug mode so you can prove the Cog wiring without provider credentials.

## Start From A Scaffolded Project

Use a project that already has `.agentforge/` from the [Quickstart](quickstart.md).

If you followed [First Real Model Run](first_real_model_run.md), turn debug mode back on for deterministic output.
Open `.agentforge/settings/system.yaml` and set:

```yaml
debug:
  mode: true
```

## The Cog File

The scaffold includes `.agentforge/cogs/beginner_summary_cog.yaml`:

```yaml
cog:
  name: "BeginnerSummaryCog"
  description: "A tiny no-memory workflow that summarizes a user message and drafts a reply."
  chat_memory_enabled: false

  agents:
    - id: summarize
      template_file: beginner_summary_agent

    - id: respond
      template_file: beginner_response_agent

  flow:
    start: summarize
    transitions:
      summarize: respond
      respond:
        end: true
```

The `agents` list gives each node an ID and points it at a prompt file under `.agentforge/prompts/`.

The `flow` starts with `summarize`, then moves directly to `respond`.

The `respond` transition uses `end: true`, so `Cog.run(...)` returns the response agent's output.

`chat_memory_enabled: false` keeps this first Cog independent from automatic chat history memory.

## The Prompt Files

The summary agent reads the runtime input from `_ctx.user_input`:

```yaml
prompts:
  system: |
    You summarize user messages for a response agent.

  user: |
    Summarize this user message in one sentence:
    {_ctx.user_input}
```

The response agent reads the original input and the first agent's output from `_state.summarize`:

```yaml
prompts:
  system: |
    You write concise replies using a summary from another agent.

  user: |
    Original user message:
    {_ctx.user_input}

    Summary from the first agent:
    {_state.summarize}

    Write a friendly two-sentence answer.
```

In a Cog prompt, `_ctx` is the context passed to `Cog.run(...)`, and `_state` stores earlier agent outputs by node ID.

## Run The Cog

Create `run_beginner_cog.py` in your project root:

```python
from agentforge.cog import Cog

result = Cog("beginner_summary_cog").run(user_input="What can AgentForge help me build?")
print(result)
```

Run it:

```shell
python run_beginner_cog.py
```

With debug mode on, the final output should be:

```text
AgentForge helps you compose agents into small workflows. This beginner Cog ran summarize -> respond and returned this final reply.
```

## What To Notice

- Cogs live under `.agentforge/cogs/`.
- Cog agent nodes point at prompt YAML files under `.agentforge/prompts/`.
- The first prompt uses `_ctx.user_input` from the Python call.
- The second prompt uses `_state.summarize` from the first node.
- This Cog has no branching, loops, memory nodes, personas, storage setup, custom Agent subclasses, or custom APIs.

## Navigation

- Previous: [Core Concepts](core_concepts.md)
- Start: [AgentForge Documentation](../README.md)
- Use [Cogs](../cogs/cogs.md) for the full schema reference after this simple flow works.
- Continue to [Branch/Loop Cog Walkthrough](branch_loop_cog_walkthrough.md) when you are ready for decisions, fallbacks, and `max_visits`.
- Use [Advanced Reference](advanced_reference.md) later for memory, personas, storage-backed workflows, custom APIs, custom Agents, utilities, and legacy Tools/Actions.
