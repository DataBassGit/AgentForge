# API Integrations in AgentForge

This is an advanced provider integration reference.

Use [First Real Model Run](../guides/first_real_model_run.md) before creating custom APIs.

AgentForge provides a unified interface for integrating with a variety of Large Language Model (LLM) APIs. All API integrations are built on the `BaseModel` class, which standardizes prompt handling, retries, logging, and parameter management. Adding a new API is as simple as subclassing `BaseModel` and registering your model in configuration.

---

## Core API Integration: `BaseModel`

All API classes inherit from `BaseModel`, which provides:

- **Unified Prompt and Media Handling**: Supports text, image, audio-input, and audio-output modalities when the selected provider class implements them.
- **Retry and Backoff Logic**: Automatic retries for rate limits and connection errors.
- **Consistent Logging**: All prompts, responses, and errors are logged.
- **Parameter Filtering**: Only relevant parameters are passed to the API.

**Key Methods and Attributes:**

```python
class BaseModel:
    default_retries = 3
    default_backoff = 2
    supported_modalities = {"text"}

    def __init__(self, model_name, **kwargs):
        self.model_name = model_name
        self.num_retries = kwargs.get("num_retries", self.default_retries)
        self.base_backoff = kwargs.get("base_backoff", self.default_backoff)
        self.allowed_params = None
        self.excluded_params = None

    def generate(self, model_prompt=None, *, images=None, **params):
        # Main entry point for generating responses (text and/or images)
        ...

    def _do_api_call(self, prompt, **filtered_params):
        # Subclasses must implement this method
        raise NotImplementedError

    def _process_response(self, raw_response):
        # Subclasses may override to post-process API responses
        return raw_response
```

- To add image/multimodal support, set `supported_modalities` and implement `_prepare_image_payload` as needed.
- See [Vision and Multimodal Support](./vision.md) for details.

---

## Built-in API Integrations

AgentForge ships with the following built-in API classes. Each is configured via YAML and can be used in agents or cogs by specifying the appropriate API and model.

| API Class | Config Key | Description |
| --- | --- | --- |
| `GPT` | `openai_api` | OpenAI chat models |
| `O1Series` | `openai_api` | OpenAI reasoning-series models |
| `STT` | `openai_api` | OpenAI speech-to-text models |
| `TTS` | `openai_api` | OpenAI text-to-speech models |
| `Codex` | `openai_api` | OpenAI Codex via OAuth |
| `Ollama` | `ollama_api` | Ollama local LLM API |
| `LMStudio` | `lm_studio_api` | LM Studio local LLM API |
| `LMStudioVision` | `lm_studio_api` | LM Studio image-capable API |
| `OpenRouter` | `openrouter_api` | OpenRouter API |
| `Gemini` | `gemini_api` | Google Gemini API |
| `GeminiVision` | `gemini_api` | Google Gemini with image support |
| `Claude` | `anthropic_api` | Anthropic Claude API |
| `GroqAPI` | `groq_api` | Groq API |
| `LiteLLM` | `litellm_api` | LiteLLM routing for configured endpoints |
| `VLLM` | `vllm_api` | vLLM-compatible local/server API |

---

## Adding a Custom API

1. **Create a Python module** in `.agentforge/custom_apis/` and subclass `BaseModel`.
2. **Implement** `_do_api_call` (required) and override `_process_response` or `_prepare_prompt` as needed.
3. **Register your API** in YAML under `model_library.<api_key>.<ClassName>.models.<model_key>.identifier`.
4. **Select your API** with `default_model` or `model_overrides` using the `api` key and model key; AgentForge discovers the provider class from `model_library`.

The `api_key` maps to the provider module, and `ClassName` must be an exported class from that module.
Keep the class layer in the YAML even when an API has only one class.

---

## Example Agent Configuration

```yaml
model_library:
  my_custom_api:
    MyCustomModel:
      models:
        my_model:
          identifier: provider-model-name
          params:
            temperature: 0.7
      params:
        temperature: 0.7

default_model:
  api: my_custom_api
  model: my_model
```

---

## Need Help?

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)
- **Discord**: [Join our Discord Server](https://discord.gg/ttpXHUtCW6)
