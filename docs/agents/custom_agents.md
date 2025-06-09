# Custom Agents Guide

Subclassing `Agent` lets you add custom logic to any part of the agent workflow. Override only the methods you need for your use case.

---

## 1. Basic Subclass
```python
from agentforge.agent import Agent

class EchoAgent(Agent):
    def build_output(self):
        self.output = self.result
```
- **Prompt File**: `.agentforge/prompts/echo_agent.yaml`
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
| Hook               | When Called                | Custom Use Case                       |
|--------------------|---------------------------|---------------------------------------|
| `process_data`     | After loading data        | Clean or transform input data         |
| `parse_result`     | After LLM response        | Parse JSON, extract fields            |
| `post_process_result` | After parsing           | Additional processing or side effects |
| `build_output`     | Last step before return   | Format final user-facing output       |

### Example: JSON Parser Agent
```python
import json
from agentforge.agent import Agent

class JSONAgent(Agent):
    def parse_result(self):
        try:
            self.parsed_result = json.loads(self.result)
        except Exception:
            self.parsed_result = {"text": self.result}
    def build_output(self):
        self.output = f"Parsed Data:\n{self.parsed_result}"
```
- **Prompt File**: `.agentforge/prompts/json_agent.yaml` with a prompt asking for JSON output.

---

## 3. Switching Prompt Files
By default, `AgentClass()` loads a prompt file matching the class name (e.g., `echo_agent.yaml`). To use a different prompt file:
```python
agent = EchoAgent(agent_name="detailed_prompt")
```
Ensure `.agentforge/prompts/detailed_prompt.yaml` exists with your desired prompts.

---

## 4. Advanced Integration
- Inject tools or APIs by instantiating them in `__init__` and using them in hooks.
- Chain calls in `process_data` or `parse_result` to interact with other agents or services.
- Modify `self.template_data` in any hook to pass dynamic variables to prompts.

---

## 5. Best Practices
- Override only the methods you need—lean subclasses are easier to maintain.
- Keep prompt file names in sync with your class or `agent_name`.
- Use `debug.mode` and `simulated_response` in config to test logic without model calls.
- Use `self.template_data` to pass all variables needed for prompt rendering.

---

## Related Documentation
- [Agent Class](agent_class.md)  
- [Prompt Templates](agent_prompts.md)  
- [Agents Overview](agents.md)  
- [Model Overrides](../settings/models.md#specifying-model-overrides-in-agents)

---

**Need Help?**  
- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)  
- **Discord**: [Join our Discord Server](https://discord.gg/ttpXHUtCW6)