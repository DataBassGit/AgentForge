# API Integrations in AgentForge

**AgentForge** is designed to work with a variety of Large Language Model (LLM) APIs out of the box. Thanks to a modular architecture built around the `BaseModel` class, integrating a new API is as simple as creating a new subclass and (optionally) adding an entry to your configuration files. Even better, if you want to use your own API interface that isn’t included with the package, **AgentForge** will automatically look for custom implementations in your project’s `.agentforge/custom_apis/` folder.

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

Once all configuration and override settings have been merged, **AgentForge** instantiates the model using the `get_model` method of the `Config` class which works as follows:

1. **Attempt to Import from the Built-In APIs**:  
   It first looks for the API module in the built-in `agentforge/apis/` folder.

2. **Fallback to Custom APIs**:  
   If the module isn’t found in the package, it will then try to locate a custom API module in your project’s  
   `your_project_root/.agentforge/custom_apis/` folder.

3. **Instantiate the Model**:  
   Once the module is imported, the method retrieves the class by name and instantiates it with the model’s identifier.

Here’s the updated method:

```python
import importlib
import importlib.util
from pathlib import Path

class Config:
    # ... other methods ...

    @staticmethod
    def get_model(api_name: str, class_name: str, model_identifier: str) -> Any:
        """
        Dynamically imports and instantiates the Python class for the requested API/class/identifier.
        It first attempts to import from the built-in 'agentforge/apis/' folder. If not found,
        it falls back to looking in the project's '.agentforge/custom_apis/' folder.
        """
        try:
            module = importlib.import_module(f".apis.{api_name}", package=__package__)
        except ImportError as e:
            # Fallback: try loading from the custom_apis folder in the project root
            project_root = Config().project_root  # Get the project root (a pathlib.Path)
            custom_api_path = project_root / ".agentforge" / "custom_apis" / f"{api_name}.py"
            if not custom_api_path.exists():
                raise ImportError(
                    f"Cannot find API module '{api_name}' in built-in folder or at {custom_api_path}."
                ) from e
            spec = importlib.util.spec_from_file_location(api_name, str(custom_api_path))
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load spec for custom API module '{api_name}' from {custom_api_path}.")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

        model_class = getattr(module, class_name)
        return model_class(model_identifier)
```

**What This Means for You:**

- **Built-In Integrations**: The default API implementations are hidden in the package and automatically available.
- **Custom Integrations**: If you want to add or override an API, simply drop a Python file (named after your API, e.g., `myapi.py`) into  
  `your_project_root/.agentforge/custom_apis/` and ensure it defines the appropriate class.
- **Configuration**: In your `models.yaml`, you simply reference the API name as usual; **AgentForge** will handle the lookup automatically.

---

## Adding a New API

To add your own API integration, follow these steps:

1. **Create a Python Module**:  
   In your project root, create a file at  
   `your_project_root/.agentforge/custom_apis/yourapi.py`.

2. **Subclass `BaseModel`**:  
   Implement a class (e.g., `YourAPI`) that inherits from `BaseModel` and provides the required methods.

   ```python
   # your_project_root/.agentforge/custom_apis/yourapi.py

   from agentforge.apis.base_api import BaseModel

   class YourAPI(BaseModel):
       def _prepare_prompt(self, model_prompt):
           # Optionally override prompt formatting
           combined = f"{model_prompt.get('system', '')}\n\n{model_prompt.get('user', '')}"
           return [{"role": "user", "content": combined}]

       def _do_api_call(self, prompt, **filtered_params):
           # Implement the actual API call using your client library
           response = your_api_client.send_request(
               model=self.model_name,
               prompt=prompt,
               **filtered_params
           )
           return response

       def _process_response(self, raw_response):
           # Process the response as needed
           return raw_response.get('result', '')
   ```

3. **Update `models.yaml`**:  
   Add an entry for your API in the `model_library` section:

   ```yaml
   model_library:
     yourapi:
       YourAPI:
         models:
           custom_model:
             identifier: "yourapi-custom-model"
             params:
               temperature: 0.6
         params:
           # Default parameters for YourAPI
           temperature: 0.7
   ```

4. **Reference in an Agent**:  
   In your agent’s YAML prompt file, specify the overrides to use your API:

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

---

## Customizing Prompt Handling and Parameters

Sometimes your API might require a different prompt format. In that case, override `_prepare_prompt(...)` as shown in the example above.  
Similarly, if your API accepts only a subset of parameters, define `self.allowed_params` or `self.excluded_params` in your subclass. The base class automatically filters parameters passed to `_do_api_call`.

---

## Conclusion

Integrating a new API in **AgentForge** is designed to be straightforward:
- **Subclass `BaseModel`** to encapsulate the specifics of your API.
- **Update your configuration (`models.yaml`)** so that **AgentForge** can locate and instantiate your new class.
- **Use custom APIs** by placing them in the `.agentforge/custom_apis/` folder; if a built-in API isn’t found, AgentForge automatically looks there.

By following these guidelines, you can quickly expand **AgentForge**’s capabilities to include any LLM API, keeping your integration modular and maintainable.

---

**Need Help?**

If you have questions or need assistance, feel free to reach out:

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)  
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)
