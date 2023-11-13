# **Models and Model Overrides Documentation**

## **Overview of Models Configuration**

The `models.yaml` file configures settings for Large Language Models (LLM) used within the system. It is located under the `settings` directory within the main project folder, typically found at `your_project_root/agentforge/settings/models.yaml`. This file includes settings for various models, APIs, and default parameters. It also supports model-specific settings, offering customization for different use cases.

### **Locating the Configuration File**

To access and modify the `models.yaml` file, navigate to the following path in your project directory:

```
agentforge/settings/models.yaml
```

Here, `agentforge` is the root directory of the project. Inside the `settings` folder, you will find the `models.yaml` file, which you can edit to configure model settings according to your needs.

### **Formatting Guidelines**

- The file is structured into sections, each corresponding to specific model configurations.
- Model-specific settings within each API allow for tailored parameters for individual models.
- Default parameters set under `ModelSettings` serve as a fallback if no specific settings are defined.

### **Sample Models Configuration**

```yaml
EmbeddingLibrary:
  library: sentence_transformers

ModelLibrary:
  openai_api:
    module: "openai"
    class: "GPT"
    models:      
      fast_model:
        name: gpt-3.5-turbo
      smart_model:
        name: gpt-4
        params: { ... } # Optional: Override specific parameters or add new ones
      # ... Other model configurations ...
  # ... Other API configurations ...

# Default settings for all models unless overridden
ModelSettings:
  API: openai_api
  Model: fast_model
  Params:
    # ... Default parameter values ...
```

#### **Note on Model-specific Parameters**
- The `params` attribute under each model in `ModelLibrary` is optional. When overriding or adding parameters, there is no need to retype all existing parameters. Simply include the specific parameters you wish to change or add. If `params` is not specified, the model will use the default parameters from `ModelSettings`.

## **Overriding Default LLM Configurations**

Agents can override the default LLM settings specified in the `models.yaml` file. This feature allows agents to use specific models or parameters tailored to their unique tasks and requirements.

### **Format for Overrides**

To override the default settings for an agent, define a `ModelOverrides` attribute within the agent's `YAML` file. The structure should mirror that of the `models.yaml` file.

Example of Agent-specific Overrides:

```yaml
Prompts: 
  # Agent sub-prompts
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
