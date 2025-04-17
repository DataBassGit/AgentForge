# Prompt Templates

**AgentForge** uses YAML-based prompt templates to drive agent behaviors. All prompt files live under:
```
<project_root>/.agentforge/prompts/
```
Each file must match the agent's name (case‑sensitive) and have a `.yaml` extension.

---

## 1. File Structure
```yaml
prompts:
  system:        # High-level context and instructions
    intro: "You are an assistant."
    task: "Focus on {task}."
  user:          # User message template
    query: "Process: {user_input}"
```
- **Top-level `prompts`** key (lowercase).
- **`system`** and **`user`** keys (lowercase) define roles.
- Nested sub-keys under `system`/`user` are concatenated with newline in definition order.

## 2. Dynamic Variables
- Placeholders in `{braces}` map to `template_data` passed via `agent.run(**kwargs)`.
- Valid identifiers only (e.g. `{user_input}`, `{task}`).
- Undefined placeholders cause their sub-section to be skipped.
- Invalid placeholders will be considered plain text and be rendered as is.

## 3. Rendering Logic
```python
from agentforge.utils.prompt_processor import PromptProcessor
rendered = PromptProcessor().render_prompts(
    template=agent.prompt_template,
    data=agent.template_data
)
# Output: {'system': '...', 'user': '...'}
```
- Sections with missing variables are dropped.  
- Final prompts are validated for structure and non-empty content.

## 4. Recursion & Subfolders
- `.agentforge/prompts/` is searched recursively for YAML files.  
- You can organize prompts in subdirectories for clarity.

## 5. Examples
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
- If `feedback` not provided, the `feedback` block is omitted.

## 6. Best Practices
- Keep keys lowercase and descriptive.  
- Order sub-keys for logical flow.  
- Use optional blocks for conditional instructions.  
- Test with `debug.mode` and `simulated_response` for quick iterations.

---
**Related:** 
  - [Agents Overview](Agents.md)
  - [Agent Class](AgentClass.md)
  - [Custom Agents](CustomAgents.md)
