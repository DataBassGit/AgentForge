# Agent Class Reference

The `Agent` class is the core orchestrator in **AgentForge**, responsible for loading configuration, rendering prompts, invoking the LLM, and producing final outputs.

## 1. Constructor
```python
class Agent:
    def __init__(
        self,
        agent_name: Optional[str] = None,
        log_file: str = 'agentforge'
    ):
        self.agent_name = agent_name or self.__class__.__name__
        self.logger = Logger(self.agent_name, log_file)
        self.config = Config()
        self.prompt_processor = PromptProcessor()

        # Core data attributes
        self.agent_data: Dict[str, Any] = {}
        self.persona: Optional[Dict[str, Any]] = None
        self.model: Optional[BaseModel] = None
        self.prompt_template: Dict[str, Any] = {}
        self.template_data: Dict[str, Any] = {}
        self.prompt: Dict[str, str] = {}
        self.result: Optional[str] = None
        self.output: Optional[str] = None
        self.images: List[str] = []

        # Load and validate agent config
        self.initialize_agent_config()
```  
- **agent_name**: Identifies the agent and prompt file.  
- **logger**: Logs to console/file.  
- **config**: Loads merged settings and YAML data.  
- **prompt_processor**: Validates and renders prompts.  

## 2. Lifecycle: `run()`
```python
def run(self, **kwargs) -> Optional[str]:
    self.logger.info(f"{self.agent_name} - Starting")
    self.load_data(**kwargs)
    self.process_data()
    self.render_prompt()
    self.run_model()
    self.parse_result()
    self.post_process_result()
    self.build_output()
    self.logger.info(f"{self.agent_name} - Completed")
    return self.output
```  
1. **load_data**: Reloads config if `on_the_fly`, loads additional data, merges `kwargs`.  
2. **process_data**: Hook for preprocessing.  
3. **render_prompt**: Applies `template_data` to `prompt_template`.  
4. **run_model**: Calls `self.model.generate(...)`.  
5. **parse_result**: Hook for postprocessing.  
6. **post_process_result**: Hook for additional processing before output construction.
7. **build_output**: Formats final output.

> **Note:** Memory and storage functionality is managed exclusively by cogs. The Agent class has extension points for subclasses that need custom data handling.

## 3. Configuration Loading

Agent configuration is loaded from the `.agentforge/prompts/` folder and merged with system defaults. The initialization process includes:

```python
def initialize_agent_config(self):
    self.load_agent_data()
    self.load_prompt_template()
    self.load_persona_data()
    self.load_model()
```

- **load_agent_data**: Uses `Config().load_agent_data(agent_name)`.
- **load_prompt_template**: Validates prompt structure.
- **load_persona_data**: Loads persona context if enabled.
- **load_model**: Configures the LLM interface.

## 4. Prompt Rendering

The `render_prompt()` method combines the agent's prompt template with dynamic variables through these steps:

1. **Prompt Template Access**:
   ```python
   prompts = agent_data.get('prompts', {})
   self.prompt_template = {
       'system': prompts.get('system', {}),
       'user': prompts.get('user', {})
   }
   ```

2. **Template Variables**:
   ```python
   self.template_data = {
       'persona_fields': {...},       # From persona if enabled
       'kwargs': {...},               # From run() arguments
       'additional_data': {...}       # From load_additional_data()
   }
   ```

3. **Rendering**:
   ```python
   # Replace {placeholders} with actual values
   self.prompt = self.prompt_processor.render_prompts(
       self.prompt_template, self.template_data
   )
   ```

## 5. Extension Points

The Agent class provides several virtual methods meant to be overridden by subclasses:

```python
def load_additional_data(self): pass
def process_data(self): pass  
def parse_result(self): pass
def post_process_result(self): pass
def build_output(self): self.output = self.result
```

- **load_additional_data**: Add custom data to `template_data`.
- **process_data**: Process data before prompt rendering.
- **parse_result**: Process the LLM output after model execution.
- **post_process_result**: Perform additional processing or side effects after parsing.
- **build_output**: Format the final output returned by `run()`.

## 6. Usage Example

```python
from agentforge.agent import Agent

class MyCustomAgent(Agent):
    def load_additional_data(self):
        self.template_data["custom_var"] = "custom value"
    
    def parse_result(self):
        # Extract structured data from result
        self.extracted_data = json.loads(self.result)
    
    def post_process_result(self):
        # Perform side effects like logging metrics or external API calls
        log_processing_metrics(self.extracted_data)
    
    def build_output(self):
        self.output = f"Processed: {self.extracted_data['key']}"

agent = MyCustomAgent("TemplateFile")
result = agent.run(dynamic_var="value")
```

Where `.agentforge/prompts/TemplateFile.yaml` contains:
```yaml
prompts:
  system: "You are a helpful assistant."
  user: "The user asks: {dynamic_var}"
```

## 7. Related Documentation
- [Agents Overview](Agents.md)  
- [Prompt Templates](AgentPrompts.md)  
- [Custom Agents](CustomAgents.md)  
- [Model Overrides](../settings/models.md#specifying-model-overrides-in-agents)

---