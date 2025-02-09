# API Integrations in AgentForge

**AgentForge** is designed to work with a variety of Large Language Model (LLM) APIs out of the box. Thanks to a modular architecture built around the `BaseModel` class, integrating a new API is as simple as creating a new subclass and (optionally) adding an entry to your configuration files. If you want to use your own API interface that isn’t included with the package, **AgentForge** will automatically look for custom implementations in your project’s `.agentforge/custom_apis/` folder.

---

## Overview: The `BaseModel` Class

At the core of every API integration in **AgentForge** is the `BaseModel` class. It provides:

- **Unified Prompt Handling**: Formats and combines system and user messages into the proper structure for the target API.
- **Retry and Backoff Logic**: Automatically retries API calls if certain errors occur (such as rate limits or connection errors).
- **Logging**: Records prompts, responses, and errors in a consistent way.
- **Parameter Management**: Filters and merges parameters so that only the relevant ones are passed to the API.

A simplified version of `BaseModel` looks like this:

```python
class BaseModel:
    default_retries = 8
    default_backoff = 2

    def __init__(self, model_name, **kwargs):
        self.model_name = model_name
        self.num_retries = kwargs.get("num_retries", self.default_retries)
        self.base_backoff = kwargs.get("base_backoff", self.default_backoff)
        self.allowed_params = None
        self.excluded_params = None
        # Logger will be set later in generate()

    def generate(self, model_prompt, **params):
        self.logger = Logger(name=params.pop('agent_name', 'NamelessAgent'))
        self.logger.log_prompt(model_prompt)

        reply = None
        for attempt in range(self.num_retries):
            backoff = self.base_backoff ** (attempt + 1)
            try:
                reply = self._call_api(model_prompt, **params)
                self.logger.log_response(reply)
                break
            except (RateLimitError, APIConnectionError) as e:
                self.logger.log(f"Error: {str(e)}. Retrying in {backoff} seconds...", level="warning")
                time.sleep(backoff)
            except Exception as e:
                self.logger.log(f"Error: {str(e)}. Retrying in {backoff} seconds...", level="warning")
                time.sleep(backoff)

        if reply is None:
            self.logger.log("Error: All retries exhausted. No response received.", level="critical")
        return reply

    def _call_api(self, model_prompt, **params):
        prompt = self._prepare_prompt(model_prompt)
        filtered_params = self._prepare_params(**params)
        response = self._do_api_call(prompt, **filtered_params)
        return self._process_response(response)

    def _prepare_prompt(self, model_prompt):
        # Default implementation: expects model_prompt to be a dict with 'system' and 'user'
        return [
            {"role": "system", "content": model_prompt.get('system')},
            {"role": "user", "content": model_prompt.get('user')}
        ]

    def _prepare_params(self, **params):
        if self.allowed_params:
            return {k: v for k, v in params.items() if k in self.allowed_params}
        if self.excluded_params:
            return {k: v for k, v in params.items() if k not in self.excluded_params}
        return params

    def _do_api_call(self, prompt, **filtered_params):
        raise NotImplementedError("Subclasses must implement _do_api_call.")

    def _process_response(self, raw_response):
        return raw_response
```

Subclasses only need to implement `_do_api_call` (and optionally override `_process_response` or `_prepare_prompt`) to adapt to the specifics of their target API.

---

## Finding and Instantiating Models

Once all configuration and override settings have been merged, **AgentForge** instantiates the model using the `get_model` method in the `Config` class. The system will:

1. **Attempt to Import from the Built-In APIs**  
   It first looks for the API module in the built-in `agentforge/apis/` folder.

2. **Fallback to Custom APIs**  
   If the module isn’t found in the package, it automatically tries to load a custom API module from  
   `your_project_root/.agentforge/custom_apis/`.

3. **Instantiate the Model**  
   After loading the module, it retrieves the class by name and instantiates it with the model’s identifier.

---

## Adding a New API

To add a custom API, follow these steps:

1. **Create a Python Module**  
   Place a file named `yourapi.py` into the `.agentforge/custom_apis/` folder of your project:
   ```
   your_project_root/
   └── .agentforge/
       └── custom_apis/
           └── yourapi.py
   ```

2. **Subclass `BaseModel`**  
   Implement the methods required for your target API. For instance:

   ```python
   # yourapi.py
   from agentforge.apis.base_api import BaseModel

   class YourAPI(BaseModel):
       def _do_api_call(self, prompt, **filtered_params):
           # Use your custom API client here
           response = your_api_client.send_request(
               model=self.model_name,
               prompt=prompt,
               **filtered_params
           )
           return response

       def _process_response(self, raw_response):
           # Transform raw_response into the final text
           return raw_response.get('answer', '')
   ```

3. **Update `models.yaml`**  
   In your configuration, reference the new API and model under `model_library`. For example:

   ```yaml
   model_library:
     yourapi:
       YourAPI:
         models:
           custom_model:
             identifier: "your-custom-api-model-id"
             params:
               temperature: 0.6
         params:
           # Default params for this API
           temperature: 0.7
   ```

4. **Use It in an Agent**  
   In your agent’s YAML config file, specify overrides to select this API and model:

   ```yaml
   prompts:
     system: "You are a custom assistant."
     user: "Please discuss advanced topics."

   model_overrides:
     api: yourapi
     model: custom_model
     params:
       temperature: 0.5
   ```

With this in place, **AgentForge** will locate and instantiate your custom API class automatically.

---

## Customizing Prompt Handling and Parameters

If your API requires a different prompt structure or specific parameters, you can override `_prepare_prompt` or `_process_response` in your subclass. Additionally, you can define `self.allowed_params` or `self.excluded_params` to ensure only the correct parameters are passed to your API client.

---

## Conclusion

**AgentForge**’s flexible design makes integrating new APIs straightforward:
- **Subclass `BaseModel`** to capture the specifics of your service.
- **Place your module** under `.agentforge/custom_apis/` if it isn’t built-in.
- **Configure your new API** in YAML so that AgentForge can discover and instantiate it.
- **Use agent-level overrides** to fine-tune parameters or swap between multiple APIs with minimal effort.

By following these steps, you’ll keep your custom integrations clean, modular, and easy to maintain.

---

**Need Help?**  
If you have any questions or run into issues, feel free to reach out:

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)  
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)