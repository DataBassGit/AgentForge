# Model Settings Guide

`models.yaml` is loaded from `.agentforge/settings/models.yaml` and merged into `Config().data['settings']['models']`.

## Location

```
<project_root>/.agentforge/settings/models.yaml
```

## Schema Overview

```yaml
# Default model selection for agents without overrides
default_model:
  api: gemini_api      # API key in model_library
  model: gemini_flash  # Model key under the chosen API's classes

# Detailed library of APIs, classes, models, and parameters
model_library:
  openai_api:         # Corresponds to agentforge/apis/openai_api.py
    params:           # API-level params (applies to all classes under this API)
      ...
    GPT:              # Python class exported by that module
      models:
        gpt55_model:
          identifier: gpt-5.5
        gpt55_pro_model:
          identifier: gpt-5.5-pro
        gpt4o_model:
          identifier: gpt-4o
        gpt41_model:
          identifier: gpt-4.1
      params:         # Default parameters for all GPT models
        temperature: 0.8
        max_completion_tokens: 10000
    Codex:
      models:
        codex_gpt55:
          identifier: gpt-5.5
        codex_gpt53_codex:
          identifier: gpt-5.3-codex
      params:
        reasoning:
          effort: medium
        timeout: 60
        verify_ssl: true
        host_url: https://chatgpt.com/backend-api/codex/responses

  gemini_api:
    Gemini:
      models:
        gemini_flash:
          identifier: gemini-3.5-flash
        gemini_pro:
          identifier: gemini-3.1-pro-preview
        gemini_flash_lite:
          identifier: gemini-3.1-flash-lite
      params:
        temperature: 1.0
        top_k: 40

  # ...additional API entries (anthropic_api, lm_studio_api, ollama_api, openrouter_api, groq_api, etc.)...

# Selective embedding library for specialized tasks
embedding_library:
  library: sentence_transformers
```

### default_model
- **api** (string): Key matching an entry under `model_library`.
- **model** (string): Model key under one of the classes in that API section.

Any agent without a `model_overrides` block uses this selection.

### model_library
A mapping of **API keys** → **Class names** → settings:

- **API key** (e.g., `openai_api`): Loads via `agentforge/apis/<api_key>.py` or custom APIs.
- **params** (optional map): API-level parameters applied to all classes/models under this API.
- **Class name** (e.g., `GPT`): Python class used to instantiate calls.
- **models**: Map of **model names** →
  - **identifier** (string): The actual LLM identifier your code passes to the API.
  - **params** (optional map): Overrides for this specific model.
- **params** (optional map): Default parameters applied to every model under this class.

> **Note**: Parameters are merged in this order: API-level → class-level → model-level → agent-level (`model_overrides.params`).

### embedding_library
- **library** (string): Name of the embedding toolkit used for specialized embedding tasks.

### Parameter Merging
**AgentForge** merges model parameters in the following order:
1. **API-level** (`model_library.<api_key>.params`)
2. **Class-level** (`model_library.<api_key>.<class>.params`)
3. **Model-level** (`model_library.<api_key>.<class>.models.<model_name>.params`)
4. **Agent-level** (`model_overrides.params` in your agent YAML)

```python
from agentforge.config import Config
# Returns (api_name, class_name, identifier, merged_params)
api, cls, ident, final_params = Config().resolve_model_overrides(agent_yaml_dict)
```

## Codex Parameters (`openai_api.Codex`)

- `top_p`, `reasoning`, `text`: Supported response body parameters.
- `host_url`, `timeout`, `verify_ssl`: Transport controls for the Codex HTTP/SSE endpoint.

## Agent-Level Overrides
Add a `model_overrides` section to your agent's YAML to change API, model, or parameters:

```yaml
model_overrides:
  api: openai_api
  model: gpt55_model
  params:
    temperature: 0.5
    max_completion_tokens: 5000
```

## Available Models & APIs

AgentForge supports a wide range of APIs and models, including OpenAI, Anthropic, Gemini, LM Studio, Ollama, OpenRouter, Groq, and more. The packaged list of supported APIs, classes, and models is in the template at:

```
src/agentforge/setup_files/settings/models.yaml
```

Refer to this file for the packaged options and identifiers.

## Accessing Model Settings in Code

```python
config = Config()
models_cfg = config.data['settings']['models']
def_model = models_cfg['default_model']
lib = models_cfg['model_library']
emb_lib = models_cfg['embedding_library']
```

## Related Guides

- [Settings Overview](settings.md)
- [System Settings Guide](system.md)
- [Storage Settings Guide](storage.md)
- [APIs Guide](../apis/apis.md)
