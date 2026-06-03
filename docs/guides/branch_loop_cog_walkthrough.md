# Branch/Loop Cog Walkthrough

This guide continues after the [Beginner Cog Walkthrough](beginner_cog_walkthrough.md).

It runs a tiny no-memory Cog that drafts an answer, reviews it, revises it, and then finishes through a loop guard.

The example uses debug mode so the branch and loop behavior is deterministic and does not need provider credentials.

## Start From A Scaffolded Project

Use a project that already has `.agentforge/` from the [Quickstart](quickstart.md).

Turn debug mode on if it is not already enabled:

```shell
python -c "from pathlib import Path; p = Path('.agentforge/settings/system.yaml'); text = p.read_text(); p.write_text(text.replace('mode: false', 'mode: true', 1))"
```

## The Cog File

The scaffold includes `.agentforge/cogs/beginner_branch_loop_cog.yaml`:

```yaml
cog:
  name: "BeginnerBranchLoopCog"
  description: "A tiny no-memory workflow that drafts, reviews, revises, and finishes with a loop guard."
  chat_memory_enabled: false

  agents:
    - id: draft
      template_file: beginner_draft_agent

    - id: review
      template_file: beginner_review_agent

    - id: revise
      template_file: beginner_revise_agent

    - id: final
      template_file: beginner_final_agent

  flow:
    start: draft
    transitions:
      draft: review
      review:
        choice:
          "approve": final
          "revise": revise
        fallback: final
        max_visits: 2
      revise: review
      final:
        end: true
```

The first step is direct: `draft` moves to `review`.

The `review` node returns a parsed JSON object with a `choice` field.

If `choice` is `"approve"`, the Cog moves to `final`.

If `choice` is `"revise"`, the Cog moves to `revise`, then loops back to `review`.

`max_visits: 2` lets `review` route twice before the third review uses `fallback: final`.

## The Review Prompt

The scaffold includes `.agentforge/prompts/beginner_review_agent.yaml`:

```yaml
parse_response_as: json
simulated_response: '{"choice": "revise", "rationale": "Make the reply more concrete for a beginner."}'
```

Debug mode returns that simulated response every time, so this walkthrough intentionally follows the loop until `max_visits` sends the flow to `final`.

The revise and final prompts can read the review rationale with `{_state.review.rationale}`.

## Run The Cog

Create `run_branch_loop_cog.py` in your project root:

```python
from agentforge.cog import Cog

result = Cog("beginner_branch_loop_cog").run(user_input="Explain AgentForge in one sentence.")
print(result)
```

Run it:

```shell
python run_branch_loop_cog.py
```

With debug mode on, the final output should be:

```text
AgentForge helps you turn prompts into small agent workflows. This branch/loop Cog drafted, reviewed, revised, and finished through its fallback after max_visits.
```

## What To Notice

- `choice` is the decision key used by the `review` transition.
- `"approve"` and `"revise"` are branch values matched against the review output.
- `fallback: final` gives the Cog a safe next step when a decision does not match or the loop guard trips.
- `max_visits: 2` prevents the `review -> revise -> review` loop from running forever.
- `chat_memory_enabled: false` keeps this example independent from automatic chat history memory.

## Next

- Use [Cogs](../cogs/cogs.md) for the full schema reference.
- Use [Advanced Reference](advanced_reference.md) later for memory, personas, storage-backed workflows, custom APIs, custom Agents, utilities, and legacy Tools/Actions.
