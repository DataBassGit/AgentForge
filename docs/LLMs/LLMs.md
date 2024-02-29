# LLM API Integration in AgentForge

## Seamless Connection with LLM APIs

**AgentForge** is engineered to interface effortlessly with a variety of Large Language Model (LLM) APIs. This flexibility is a cornerstone of our system, allowing users to plug in different language models as needed. The `get_llm` method plays a pivotal role in this process, leveraging the Python files designated for each API in the `llm` folder within our library package.

### How the `get_llm` Method Works

The `get_llm` method in the configuration class dynamically references the Python files corresponding to each API,
as specified in the `models.yaml` settings.
This method ensures that the chosen model and its parameters are loaded correctly for the agent to use.

For more information on configuring the `models.yaml` file, please refer to our detailed documentation on [Models and Model Overrides Documentation](../Settings/Models.md).

#### Breakdown of the `get_llm` Method:

1. **Configuration Retrieval**: The method begins by extracting the necessary information from the `models.yaml` settings. This includes the name of the model, the module where the API class is defined, and the class name that will be instantiated.

2. **Dynamic Module Import**: Using the built-in `importlib` library, the method dynamically imports the module that contains the API class.

3. **Class Retrieval**: It then retrieves the specific class from the imported module that is designed to handle interactions with the selected LLM API.

4. **Model Instantiation**: The method prepares any necessary arguments, then instantiates and returns an object of the model class.

5. **Exception Handling**: If any errors occur during this process (such as a missing module or class), the method prints an error message and re-raises the exception to alert the user.

```python
def get_llm(self, api: str, model: str):
    """
    Loads a specified language model based on API and model settings.

    Parameters:
        api (str): The API name.
        model (str): The model name.

    Returns:
        object: An instance of the requested model class.

    Raises:
        Exception: If there is an error loading the model.
    """
    try:
        # Retrieve the model name, module, and class from the 'models.yaml' settings.
        model_name = self.data['settings']['models']['ModelLibrary'][api]['models'][model]['name']
        module_name = self.data['settings']['models']['ModelLibrary'][api]['module']
        class_name = self.data['settings']['models']['ModelLibrary'][api]['class']

        # Dynamically import the module corresponding to the LLM API.
        module = importlib.import_module(f".llm.{module_name}", package=__package__)

        # Retrieve the class from the imported module that handles the LLM connection.
        model_class = getattr(module, class_name)

        # Prepare the arguments for the model class instantiation.
        args = [model_name]

        # Instantiate the model class with the provided arguments.
        return model_class(*args)

    # Handle any exceptions that occur during the model loading process.
    except Exception as e:
        print(f"Error Loading Model: {e}")
        raise
```
 
This approach empowers users to focus on crafting agents and defining their behavior, rather than the intricacies of LLM API configurations and connections.

--- 

### Directory Structure

In the `llm` [Directory](../../src/agentforge/llm), you will find Python files such as `openai.py`, `anthropic.py`, and `oobabooga.py`. Each file is tailored to interact with its respective LLM API.

### Key Functionality of API Files

Each API file contains a `generate_text` method. This method is crucial for processing prompts and handling parameters. It abstracts the complexities of API interactions, presenting a unified method signature across different models.

#### Example of `generate_text` Method Usage:

```python
class Agent:
    # ... other methods ...

     def run_llm(self):
        """
        Executes the language model generation with the generated prompt(s) and any specified parameters.
        """
        try:
            model: LLM = self.agent_data['llm']
            params = self.agent_data.get("params", {})
            params['agent_name'] = self.agent_name
            self.result = model.generate_text(self.prompt, **params).strip()
        except Exception as e:
            self.logger.log(f"Error running LLM: {e}", 'error')
            self.result = None
```

### Integrating New LLM APIs

Integrating a new LLM API involves creating a corresponding Python file in the `llm` directory. This file must implement the `generate_text` method, adhering to the established interface pattern. The system will then be able to use this new API file to communicate with the associated LLM.

### Special Note on Oobabooga API

The `oobabooga_api` requires a unique configuration due to its external hosting:

```yaml
oobabooga_api:
  # ... configuration details ...
  params:
    host_url: "127.0.0.1:5000" # The host server URL for the Oobabooga model
```

For the `oobabooga_api`, the host URL is defined as the model is hosted externally and accessed via this URL.

For more information on the Oobabooga implementation and other models, please see our [Models documentation](../Settings/Models.md).
