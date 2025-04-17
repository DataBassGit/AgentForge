# Agent Class Reference

The `Agent` class is the core orchestrator in **AgentForge**, responsible for loading configuration, rendering prompts, invoking the LLM, handling storage, and producing final outputs.

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
    self.save_to_storage()
    self.build_output()
    self.logger.info(f"{self.agent_name} - Completed")
    return self.output
```  
1. **load_data**: Reloads config if `on_the_fly`, loads storage, merges `kwargs`.  
2. **process_data**: Hook for preprocessing.  
3. **render_prompt**: Applies `template_data` to `prompt_template`.  
4. **run_model**: Calls `self.model.generate(...)`.  
5. **parse_result**: Hook for postprocessing.  
6. **save_to_storage**: Persists data if enabled.  
7. **build_output**: Formats final output.

## 3. Configuration Loading
- **initialize_agent_config()**: Calls loading steps:
  ```python
  load_agent_data()
  load_prompt_template()
  load_persona_data()
  load_model()
  resolve_storage()
  ```
- **load_agent_data()**: Merges `system`, `models`, `storage`, `prompts`, `params` via `Config.load_agent_data()`.  
- **load_prompt_template()**: Validates presence of `prompts` (`system`/`user`).  
- **load_persona_data()**: Injects persona fields if enabled.  
- **load_model()**: Instantiates LLM using `resolve_model_overrides`.  
- **resolve_storage()**: Attaches storage instance (`self.agent_data['storage']`) or `None`.

## 4. Prompt Rendering
- Prompts loaded from YAML contain nested `system` and `user` keys (see Prompt Templates).  
- `PromptProcessor` flattens and concatenates sub-keys in order, substituting all `{variable}` placeholders.  
- Optional sections with missing variables are automatically skipped.

## 5. Custom Hooks
Override these methods in subclasses to inject custom logic:
- **process_data(self)**: Transform or validate `template_data` before prompt.  
- **parse_result(self)**: Parse or extract structure from `self.result`.  
- **save_to_storage(self)**: Custom storage interactions.  
- **build_output(self)**: Assemble final `self.output`.

## 6. Related Documentation
- [Agents Overview](Agents.md)  
- [Prompt Templates](AgentPrompts.md)  
- [Custom Agents](CustomAgents.md)  
- [Model Overrides](../Settings/Models.md#specifying-model-overrides-in-agents)

---