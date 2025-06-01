# Custom Agents Guide

Subclassing `Agent` lets you inject custom logic without rewriting core workflows. Use your subclass to override specific hooks:

---

## 1. Basic Subclass
```python
from agentforge.agent import Agent

class EchoAgent(Agent):
    def build_output(self):
        # Use the raw LLM result as-is
        self.output = self.result
```
- **Prompt File**: `.agentforge/prompts/EchoAgent.yaml`
  ```yaml
  prompts:
    system: "You echo back the user input."
    user: "Echo: {user_input}"
  ```
- **Usage**:
  ```python
  agent = EchoAgent()
  print(agent.run(user_input="Hello"))  # "Echo: Hello"
  ```

---

## 2. Overriding Hooks
| Hook             | When Called                | Custom Use Case                       |
|------------------|----------------------------|---------------------------------------|
| `process_data`   | After loading `kwargs`     | Clean or transform input data         |
| `parse_result`   | After LLM response         | Parse JSON, extract fields           |
| `save_to_storage`| After parsing              | Persist conversation or results       |
| `build_output`   | Last step before return    | Format final user-facing output      |

### Example: JSON Parser Agent
```python
import json
from agentforge.agent import Agent

class JSONAgent(Agent):
    def parse_result(self):
        try:
            data = json.loads(self.result)
        except json.JSONDecodeError:
            data = {"text": self.result}
        self.template_data['parsed'] = data

    def build_output(self):
        # Present parsed data as formatted string
        self.output = f"Parsed Data:\n{self.template_data['parsed']}"
```
- **Prompt File**: `JSONAgent.yaml` with a prompt asking for JSON output.

---

## 3. Switching Prompt Files
By default, `AgentName()` loads `AgentName.yaml`. To use a different prompt file:
```python
# Use DetailedPrompt.yaml for the same class
agent = EchoAgent(agent_name="DetailedPrompt")
```  
Ensure `.agentforge/prompts/DetailedPrompt.yaml` exists with your desired prompts.

---

## 4. Advanced Integration
- **Inject Tools or APIs**: Instantiate helpers in `__init__`, then call them in hooks.
- **Multi-pass Workflows**: Chain calls in `process_data` or `parse_result` to interact with other agents or services.
- **Persona Overrides**: Modify `self.template_data` in `load_persona_data` or `process_data` for dynamic persona logic.

---

## 5. Best Practices
- Only override the methods you need—lean subclasses are easier to maintain.  
- Keep prompt file names in sync with your class or `agent_name`.  
- Use `debug.mode` with `simulated_response` to test logic without API calls.  
- Validate your final prompts using `PromptProcessor` in isolation if needed.

---

## Related Documentation
- [Agent Class](AgentClass.md)  
- [Prompt Templates](AgentPrompts.md)  
- [Agents Overview](Agents.md)  
- [Model Overrides](../settings/models.md#specifying-model-overrides-in-agents)

---

**Need Help?**  
- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)  
- **Discord**: [Join our Discord Server](https://discord.gg/ttpXHUtCW6)