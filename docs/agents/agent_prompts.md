# Prompt Templates

AgentForge uses YAML-based prompt templates to drive agent behaviors. All prompt files live under:
```
<project_root>/.agentforge/prompts/
```
Each file should match the agent's name (case-sensitive, snake_case recommended) and have a `.yaml` extension. You can override the prompt file by passing a different `agent_name` to the agent constructor.

---

## File Structure
```yaml
prompts:
  system:        # High-level context and instructions
    intro: "You are an assistant."
    task: "Focus on {task}."
  user:          # User message template
    query: "Process: {user_input}"
```
- The top-level `prompts` key is required.
- `system` and `user` keys define roles and are required.
- Nested sub-keys under `system`/`user` are concatenated in definition order.

## Dynamic Variables
- Placeholders in `{braces}` map to keys in `template_data` (populated from `agent.run(**kwargs)` and hooks).
- Only valid Python identifiers are allowed (e.g., `{user_input}`, `{task}`).
- If any required variable in a prompt section is missing or empty, the entire section is skipped.
- Invalid placeholders are rendered as plain text.

## Rendering Logic
```python
from agentforge.utils.prompt_processor import PromptProcessor
rendered = PromptProcessor().render_prompts(
    prompts=agent.prompt_template,
    data=agent.template_data
)
# Output: {'system': '...', 'user': '...'}
```
- Sections with missing variables are dropped.
- Final prompts are validated for structure and non-empty content.

## Recursion & Subfolders
- `.agentforge/prompts/` is searched recursively for YAML files.
- You can organize prompts in subdirectories for clarity.

## Examples
### Basic Echo
```yaml
prompts:
  system: "You echo the user input."
  user: "Echo: {user_input}"
```
```python
result = agent.run(user_input="Hello")  # "Echo: Hello"
```

### Optional Section
```yaml
prompts:
  system:
    base: "You are an assistant."
    feedback: |
      Reviewer feedback:
      {feedback}
  user: "Question: {question}"
```
- If `feedback` is not provided, the `feedback` block is omitted.

## Best Practices
- Use lowercase, descriptive keys.
- Order sub-keys for logical flow.
- Use optional blocks for conditional instructions.
- Test with `debug.mode` and `simulated_response` for quick iterations.
- Pass all dynamic variables via `template_data` (from `run()` or hooks).

---
- [Agents Overview](agents.md)
- [Agent Class](agent_class.md)
- [Custom Agents](custom_agents.md)
