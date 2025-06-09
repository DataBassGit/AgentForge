# Agent Class Reference

The `Agent` class is the core orchestrator in AgentForge. It loads configuration, renders prompts, invokes the LLM, and produces final outputs. Agents can be subclassed for custom logic.

## Constructor and Attributes
```python
class Agent:
    def __init__(self, agent_name: Optional[str] = None, log_file: Optional[str] = 'agentforge'):
        self.agent_name: str
        self.logger: Logger
        self.config: Config
        self.prompt_processor: PromptProcessor
        self.parsing_processor: ParsingProcessor
        self.agent_config: AgentConfig
        self.prompt_template: dict
        self.template_data: dict
        self.prompt: dict
        self.result: Optional[str]
        self.parsed_result: Optional[Any]
        self.output: Optional[str]
        self.persona: Optional[dict]
        self.images: list
        self.model: Optional[BaseModel]
        self._initialize_data_attributes()
        self._initialize_agent_config()
```
- `agent_name` determines which prompt/config file to load.
- `logger` handles logging.
- `config` loads and manages all configuration.
- `prompt_processor` and `parsing_processor` handle prompt rendering and result parsing.
- `agent_config` holds all loaded config, including model, params, prompts, persona, and custom fields.
- `prompt_template` and `template_data` are used for prompt rendering.
- `images` can be attached to model calls if supported.

## Lifecycle: `run()`
```python
def run(self, **kwargs) -> Optional[str]:
    self.logger.info(f"{self.agent_name} - Running...")
    self._execute_workflow(**kwargs)
    self.logger.info(f"{self.agent_name} - Done!")
    return self.output
```
The workflow includes:
- Loading and merging config and runtime data
- Processing data (optional hook)
- Rendering prompts
- Running the model
- Parsing and post-processing results
- Building the final output

## Configuration Loading
Configuration is loaded from the `.agentforge/prompts/` folder and merged with system defaults. The agent loads:
- `prompts`: System and user prompt templates
- `params`: Model parameters
- `persona`: Persona data if enabled
- `settings`: System and agent settings
- `simulated_response`: Used if debug mode is enabled
- `parse_response_as`: Format for parsing model output (e.g., `json`)
- `custom_fields`: Any extra fields from the YAML config

## Prompt Rendering
Prompts are rendered by substituting variables from `template_data` into the `prompt_template` using `PromptProcessor`. If any required variable is missing or empty, the corresponding prompt section is skipped.

## Extension Points
The following methods are designed to be overridden in subclasses:
```python
def load_additional_data(self):
    pass

def process_data(self):
    pass

def parse_result(self):
    self.parsed_result = self.parsing_processor.parse_by_format(self.result, self.agent_config.parse_response_as)

def post_process_result(self):
    pass

def build_output(self):
    self.output = self.parsed_result
```
- `load_additional_data`: Add custom data to `template_data`.
- `process_data`: Preprocess data before prompt rendering.
- `parse_result`: Parse the LLM output after model execution.
- `post_process_result`: Additional processing after parsing.
- `build_output`: Format the final output returned by `run()`.

## Usage Example
```python
from agentforge.agent import Agent
import json

class MyCustomAgent(Agent):
    def load_additional_data(self):
        self.template_data["custom_var"] = "custom value"
    def parse_result(self):
        try:
            self.parsed_result = json.loads(self.result)
        except Exception:
            self.parsed_result = {"text": self.result}
    def build_output(self):
        self.output = f"Processed: {self.parsed_result.get('key', self.result)}"

agent = MyCustomAgent("template_file")
result = agent.run(dynamic_var="value")
```
Where `.agentforge/prompts/template_file.yaml` contains:
```yaml
prompts:
  system: "You are a helpful assistant."
  user: "The user asks: {dynamic_var}"
```

## Supported Config Keys
- `prompts`: System and user prompt templates
- `params`: Model parameters
- `persona`: Persona data (optional)
- `settings`: System and agent settings
- `simulated_response`: Used for debug mode
- `parse_response_as`: Format for parsing model output (e.g., `json`)
- `custom_fields`: Any extra fields from the YAML config

---
- [Agents Overview](agents.md)
- [Prompt Templates](agent_prompts.md)
- [Custom Agents](custom_agents.md)
- [Model Overrides](../settings/models.md#specifying-model-overrides-in-agents)
