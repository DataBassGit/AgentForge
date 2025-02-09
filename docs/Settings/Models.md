# Model Settings Guide

The `models.yaml` file centralizes all Model configurations used by your agents. This includes default model choices, a comprehensive library of possible APIs and models, and optional embedding libraries. Agents can either use these defaults or override them in their own YAML files.

---

## Location

```
your_project_root/.agentforge/settings/models.yaml
```

---

## Default Structure

A typical `models.yaml` might look like this:

```yaml
# Default model settings for all agents unless overridden
default_model:
  api: gemini_api
  model: gemini_flash

# Library of models and parameter defaults
model_library:
  openai_api:
    GPT:
      models:
        omni_model:
          identifier: gpt-4o
          params:
            max_new_tokens: 15000
        fast_model:
          identifier: gpt-3.5-turbo
      params:
        temperature: 0.8
        max_tokens: 10000
        n: 1

  gemini_api:
    Gemini:
      models:
        gemini_pro:
          identifier: gemini-1.5-pro
        gemini_flash:
          identifier: gemini-1.5-flash
      params:
        temperature: 0.8
        top_k: 40

  # ... Other API entries ...

# Embedding library
embedding_library:
  library: sentence_transformers
```

In broad strokes, **AgentForge** loads these configurations at startup and merges them into a single dictionary accessible at `agent_data['settings']['models']`.

---

## Key Sections

### 1. `default_model`

```yaml
default_model:
  api: gemini_api
  model: gemini_flash
```

- **`api`**: The name of the API your agents will use if they don’t specify an override (e.g., `gemini_api`, `openai_api`, etc.).  
- **`model`**: The default model within that API library. 

Any agent that doesn’t declare a `model_overrides` block will use this combination of `api` and `model`.

---

### 2. `model_library`

Under the `model_library` key, you’ll find one or more sections for each **API** your project supports. For instance, `openai_api`, `anthropic_api`, `gemini_api`, and so on. Each API section typically has one or more **classes** (like `GPT` or `Gemini`) that define multiple models.

```yaml
model_library:
  openai_api:
    GPT:
      models:
        fast_model:
          identifier: gpt-3.5-turbo
          params:
            max_new_tokens: 4000
        omni_model:
          identifier: gpt-4o
      params:
        temperature: 0.8
```

1. **API Name** (e.g., `openai_api`)  
   Corresponds to a Python module under `agentforge/apis/openai_api.py`.  

2. **Class Name** (e.g., `GPT`)  
   Typically the class used to instantiate or connect to the API from within that module.  

3. **`models`**  
   A dictionary where each key is a **model name** (like `fast_model` or `omni_model`), pointing to a configuration that includes:
   - **`identifier`**: The actual string your code uses to refer to the LLM (like `gpt-3.5-turbo`).  
   - **`params`**: (Optional) Parameter overrides specific to this model (e.g., custom `max_new_tokens`).  

4. **`params`**  
   A dictionary of **default parameters** for all models in this class. For example, if you define `temperature: 0.8` here, each model under `GPT` inherits that unless it’s overridden by the model’s own `params`.

**Merging Parameters**  
When **AgentForge** resolves which model to use, it merges parameters in the following order:
1. **API-level `params`** (if present).  
2. **Class-level `params`** (like the `params` block under `GPT`).  
3. **Model-level `params`** (the block nested under each specific model).  
4. **Agent-level overrides** if the agent’s YAML includes a `model_overrides` section.

---

### 3. `embedding_library`

```yaml
embedding_library:
  library: sentence_transformers
```

This section often appears in `models.yaml` for specifying which embedding toolkit you’re using system-wide. In most cases:

- **`library`**: The name of the Python module or method used to generate text embeddings.  
- Additional details can appear here if your embedding approach requires more nuance (though typically it’s handled in `storage.yaml` when specifying how embeddings are used to store data).

---

## Specifying Model Overrides in Agents

Agents can override the **API**, **model**, or **params** defined in `default_model` and `model_library`. Here’s how:

```yaml
# In your agent's .yaml
prompts:
  system: "You are a specialized summarizer."
  user: "Summarize: {text}"

model_overrides:
  api: openai_api
  model: fast_model
  params:
    temperature: 0.5
    max_new_tokens: 5000
```

When this agent loads:

1. It starts with the global `default_model` (e.g., `api: gemini_api`, `model: gemini_flash`).  
2. Sees the override: `api: openai_api` and `model: fast_model`.  
3. Merges parameters from `model_library.openai_api.GPT.params`, plus `fast_model.params`, plus `agent`-level overrides (`temperature: 0.5, max_new_tokens: 5000`).  

This final merged set of parameters is then used to instantiate the underlying model class.

---

## Adding New APIs or Models

If you’d like to integrate a new API or define a custom LLM, follow these steps:

1. **Create a Python module** in `your_project_root/.agentforge/custom_apis/<your_api_name>.py`.  
2. **Define a class** that handles the logic for generating text. For instance, if your API is named `myapi_api`, you might define a class `MyAPIClass` that calls the remote LLM.  
3. **Update `models.yaml`**  
   - Under `model_library`, add a key matching your API’s name.  
   - Under that key, add a key for the class name, then define your `models` dictionary.  
4. **Use your new API**  
   - In `default_model`, set `api` to `myapi_api`, and the model name to one of the keys you defined in that `models` dictionary. Or specify them in an agent’s `model_overrides` block.

This modular approach allows you to expand or swap out LLMs with minimal changes to your agent code. See the [APIs Guide](../APIs/APIs.md) for more detailed information on how to create your own custom API interface.

---

## Example Usage in Code

When your agent is instantiated, the system merges the chosen model’s config and creates a model object. For instance:

```python
from agentforge.agent import Agent

class SummarizeAgent(Agent):
    def run_llm(self):
        # Optionally inspect final parameters
        final_params = self.agent_data['params']
        self.logger.log(f"Using model params: {final_params}", "debug", "model_io")
        
        # The 'model' field is already an instantiated class from the relevant API module
        self.result = self.model.generate(self.prompt, **final_params)
```

Here, `self.model` is the Python object created from your `model_library` definitions, and `self.agent_data['params']` is the fully merged parameter dictionary.

---

## Best Practices

- **Leverage `default_model`** for common usage, and only override in agent YAML when needed.  
- **Keep parameter definitions minimal** at each level. If you only need to change `temperature`, specify that alone in your override.  
- **Use Clear Naming** in your `model_library`. For example, call the class `GPT` or `Gemini` to reflect the actual Python class used.  
- **Test new models** thoroughly by enabling debug logs at the `model_io` level (`model_io: debug`) to confirm you’re sending the correct parameters.

---

## Conclusion

By splitting model configuration into a **default** model and a **model_library**, **AgentForge** offers both convenience and flexibility. Most agents can rely on a universal default, while specialized agents can override exactly what they need. Meanwhile, new APIs or models can be added by simply creating a Python module and updating the `models.yaml` file accordingly.

For more details about how these model settings interact with system or storage configurations, check out:

- [Settings Overview](Settings.md)
- [System Settings Guide](System.md)  
- [Storage Settings Guide](Storage.md)
- [Personas Guide](../Personas/Personas.md)

---

**Need Help?**

If you have questions or need assistance, feel free to reach out:

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)  
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)
