# **Models and Model Overrides Documentation**

## **Overview of Models Configuration**

The `models.yaml` file configures settings for Large Language Models (LLM) used within the system. It is located under the `settings` directory within the main project folder. This file includes settings for various models, APIs, and default parameters. It also supports model-specific settings, offering customization for different use cases.

### **Locating the Configuration File**

To access and modify the `models.yaml` file, navigate to the following path in your project directory:

```
your_project_root/.agentforge/settings/models.yaml
```

Here, `your_project_root` is the root directory of the project. Inside the `settings` folder, you will find the `models.yaml` file, which you can edit to configure model settings according to your needs.

### **Formatting Guidelines**

- The file is structured into sections, each corresponding to specific model configurations.
- Model-specific settings within each API allow for tailored parameters for individual models.
- Default parameters set under `ModelSettings` serve as a fallback if no specific settings are defined.

### **Sample Models Configuration**

```yaml
# Default settings for all models unless overridden
ModelSettings:
  API: openai_api
  Model: fast_model
  Params: # Default parameter values 
    max_new_tokens: 3000
    temperature: 0.8
    # ... more values ...

# Library of Models and Parameter Defaults Override
ModelLibrary:
  openai_api:
    module: "openai"
    class: "GPT"
    models:
      omni_model:
        name: gpt-4o
        params: # Optional: Override specific parameters for the model
          max_new_tokens: 3500
      # ... Other model configurations ...
  # ... Other API configurations ...

# Embedding Library (Not much to see here)
EmbeddingLibrary:
  library: sentence_transformers
```

#### **Note on Model-specific Parameters**
- The `params` attribute under each model in `ModelLibrary` is optional. When overriding or adding parameters, there is no need to retype all existing parameters. Simply include the specific parameters you wish to change or add. If `params` is not specified, the model will use the default parameters from `ModelSettings`.

---

## Special Configuration for LM Studio API

### **Understanding LM Studio API Integration**

The `lm_studio_api` is a distinct implementation within the `ModelLibrary` that interacts with an externally hosted model. Unlike other models where a model name must be specified, the LM Studio model is hosted and accessed through a specific URL.

#### **Configuration for LM Studio**

Here's an example of how the LM Studio model is configured within the `ModelLibrary`:

```yaml
ModelLibrary:
  # ... Other Model APIs ...
  lm_studio_api:
    module: "LMStudio"
    class: "LMStudio"
    models:
      LMStudio:
        name: lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF
        params:
          host_url: "http://localhost:1234/v1/chat/completions" # Points to the LM Studio host server URL
          allow_custom_value: True
```

**Key Points to Note:**

- **Model Name**: The `name` attribute specifies the model hosted by LM Studio, which in this case is `lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF`. While the name attribute is not strictly required, it is recommended.
- **Host URL**: The `host_url` parameter is crucial as it specifies the URL and port where the LM Studio model is hosted. This can be a local address (as shown in the example) or a remote server address.
- **Custom Value Allowance**: The `allow_custom_value` parameter is set to `True`, enabling the use of custom values within the model configuration.

### **Implications of LM Studio Configuration**

When integrating with the `lm_studio_api`:

- Ensure that the `host_url` is correctly defined to match the hosting location of the LM Studio model. The script will connect to the given URL and port to communicate with the model.
- Adjust the `host_url` based on whether LM Studio is hosted locally or on a remote server, ensuring the system can reliably access the model.

> **Note**: The LM Studio model requires this specific configuration due to its external hosting setup. Ensure that the connection details are accurate to facilitate smooth communication with the model.

---

## **Overriding Default LLM Configurations**

Agents can override the default LLM settings specified in the `models.yaml` file. This feature allows agents to use specific models or parameters tailored to their unique tasks and requirements.

### **Format for Overrides**

To override the default settings for an agent, define a `ModelOverrides` attribute within the agent's `YAML` file. The structure should mirror that of the `models.yaml` file.

### Example of Agent-specific Overrides:

```yaml
Prompts: 
  # Agent prompts

ModelOverrides:
  API: openai_api
  Model: smart_model
  Params:
    # Optional: Override specific parameters or add new ones
```

#### **Note on Agent-specific Parameter Overrides**
- In `ModelOverrides`, the `Params` attribute is also optional. For overriding or adding parameters, it's unnecessary to list all parameters again. Just add or override the specific ones you need. If `Params` is not defined, the agent will use the model's parameters as defined in `ModelLibrary`, or default parameters if none are specified.

---

## **Overriding Default LLM Configurations**

Agents can override the default LLM settings specified in the `models.yaml` file. This feature allows agents to use specific models or parameters tailored to their unique tasks and requirements.

### **Format for Overrides**

To override the default settings for an agent, define a `ModelOverrides` attribute within the agent's `YAML` file. The structure should mirror that of the `models.yaml` file.

### Example of Agent-specific Overrides:

```yaml
Prompts: 
  # Agent prompts

ModelOverrides:
  API: openai_api
  Model: smart_model
  Params:
    # Optional: Override specific parameters or add new ones
```

#### **Note on Agent-specific Parameter Overrides**
- In `ModelOverrides`, the `Params` attribute is also optional. For overriding or adding parameters, it's unnecessary to list all parameters again. Just add or override the specific ones you need. If `Params` is not defined, the agent will use the model's parameters as defined in `ModelLibrary`, or default parameters if none are specified.

### **Usage and Implications**

By including `ModelOverrides` in an agent's `YAML` file,
you can specify different settings from those in the primary `models.yaml`.
This is especially useful when an agent requires a more advanced model or different parameters.

> **Note**: While agent-level overrides provide granular control, it's crucial to ensure compatibility of the chosen model and parameters within the overall framework. Always validate any overrides for seamless integration and operation.

---
