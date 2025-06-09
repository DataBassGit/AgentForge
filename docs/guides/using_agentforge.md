# Using AgentForge

This guide introduces the modern AgentForge framework, focusing on YAML-first configuration, agent and cog orchestration, memory, personas, and settings. It is designed for new developers and reflects the latest best practices and conventions.

---

## 1. Overview: How AgentForge Works

AgentForge enables you to build powerful AI workflows by combining:
- **Agents**: Modular AI components defined by prompt templates and configuration.
- **Cogs**: Declarative YAML files that orchestrate multi-agent workflows, memory, and logic.
- **Memory**: Shared context and state, managed automatically in Cogs.
- **Personas**: Configurable agent identities and styles, referenced in prompts and memory.
- **Settings**: Centralized YAML configuration for models, system, and storage.

---

## 2. Defining Agents with Prompt Templates

Agents are defined by YAML prompt templates in `.agentforge/prompts/`. Each file corresponds to an agent and uses placeholders for dynamic variables.

**Example: `.agentforge/prompts/response_agent.yaml`**
```yaml
prompts:
  system:
    intro: |
      You are a response agent. Your job is to provide a clear, concise, and helpful reply to the user based on the provided analysis and rationale.
    persona_context: |
      ## Current Persona Understanding
      {_mem.persona_memory._narrative}
    chat_history: |
      ## Chat History
      {_mem.chat_history.history}
    scratchpad: |
      ## Scratchpad
      {_mem.scratchpad.readable}
  user:
    context: |
      ## User Message
      {_ctx}
    analysis: |
      ## Your Internal State
      {_state}
    instruction: |
      Using the information above, draft a concise, clear final response that directly addresses the user's needs or questions.
```

**Key Variables:**
- `{_ctx}`: Current external context (e.g., user input).
- `{_state}`: Outputs from previous agents in the workflow.
- `{_mem}`: Memory nodes (e.g., chat history, persona memory).
- `{persona.static.name}`: Persona fields (see below).

See the [Agent Prompts Guide](../agents/agent_prompts.md) for details on prompt variables and template structure.

---

## 3. Orchestrating Multi-Agent Workflows with Cogs

Cogs are YAML files in `.agentforge/cogs/` that define multi-agent workflows, memory, and flow logic—no Python required except the script to run the actual Cog.

**Example: `.agentforge/cogs/example_cog_with_memory.yaml`**
```yaml
cog:
  name: "ExampleCogWithMemory"
  description: "A sample decision workflow with memory."
  chat_memory_enabled: false

  agents:
    - id: analysis
      template_file: cog_analyze_agent
    - id: decision
      template_file: cog_decide_agent
    - id: response
      template_file: cog_response_agent

  memory:
    - id: general_memory
      query_before: analysis
      update_after: response
      query_keys: [user_input]
      update_keys: [user_input, response]

  flow:
    start: analysis
    transitions:
      analysis: decision
      decision:
        choice:
          "approve": response
          "reject": analysis
        fallback: response
        max_visits: 3
      response:
        end: true
```

**How to Run a Cog:**
```python
from agentforge.cogs import Cog
cog = Cog('example_cog_with_memory')
result = cog.run(user_input="Your message here")
print(result)
```

See the [Cogs Guide](../cogs/cogs.md) for full details on YAML schema, transitions, and advanced orchestration.

---

## 4. Memory: Sharing Context Across Agents

Memory nodes are declared in the `memory` section of your Cog YAML. They are managed automatically and made available to agents via the `_mem` variable in prompt templates.

- **Types:** General memory, PersonaMemory, ChatHistoryMemory, ScratchPad.
- **Access:** `{_mem.<node_id>.readable}` or other properties in your prompt templates.
- **Automatic Chat History:** Enabled by default unless `chat_memory_enabled: false`.

See the [Memory Guide](../memory/memory.md) for configuration and usage examples.

---

## 5. Personas: Configurable Agent Identity

Personas are YAML files in `.agentforge/personas/` that define agent identity, style, and context. They are referenced in prompt templates and used for memory namespacing.

**Example: `.agentforge/personas/alice.yaml`**
```yaml
static:
  name: Alice
  description: |
    A friendly assistant with a cheerful tone and a knack for storytelling.
  goal: Provide helpful, concise answers.
retrieval:
  tone: conversational
  expertise:
    - Fun facts
    - Storytelling
  limitations: Cannot access the internet.
  principles:
    - Helpfulness
    - Clarity
```

- Reference persona fields in prompts: `{persona.static.name}`, `{persona.retrieval.tone}`
- Specify persona in Cog or agent YAML: `persona: alice`

See the [Personas Guide](../personas/personas.md) for schema and usage.

---

## 6. Settings: Centralized Configuration

All framework settings are managed via YAML files in `.agentforge/settings/`:
- `system.yaml`: System-level options and paths.
- `models.yaml`: Model and API configuration.
- `storage.yaml`: Storage backend settings.

Settings are loaded and merged automatically. Agents and cogs can override global settings as needed.

See the [Settings Guide](../settings/settings.md) for details and best practices.

---

## 7. Custom Agent Classes (Advanced)

Most users will define agents via YAML prompt templates. For advanced use cases, you can subclass `Agent` to add custom methods or override behaviors.

**Example:**
```python
from agentforge.agent import Agent
class CustomAgent(Agent):
    def process_data(self):
        # Custom pre-processing
        pass
    def build_output(self):
        # Custom post-processing
        return super().build_output()
# Usage
my_custom_agent = CustomAgent('response_agent')
reply = my_custom_agent.run(user_input="Hello!")
print(reply)
```
See the [Custom Agents Guide](../agents/custom_agents.md) for more.

---

## 8. Additional Resources

- [Agents Overview](../agents/agents.md)
- [Cogs Guide](../cogs/cogs.md)
- [Memory Guide](../memory/memory.md)
- [Personas Guide](../personas/personas.md)
- [Settings Guide](../settings/settings.md)
- [Prompt Template Examples](../../src/agentforge/setup_files/prompts/)
- [Cog Configuration Examples](../../src/agentforge/setup_files/cogs/)

If you encounter issues, see the [Troubleshooting Guide](../guides/troubleshooting_guide.md).
