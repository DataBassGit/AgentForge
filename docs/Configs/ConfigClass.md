# Config Class

Welcome to the Config Class documentation! Here, we delve deep into the inner workings of the `Config` class. This class is the backbone of our system's configuration management, ensuring settings are fetched, parsed, and made available seamlessly.

---

## 📌 Key Insight: The Backbone of Configuration

The `Config` class serves a dual purpose:

1. **Central Configuration Source**: Instead of scattering settings across multiple modules or hard-coding them, the `Config` class centralizes them. This ensures uniform access and streamlined updates.
   
2. **Efficient Performance**: Designed as a Singleton, the class ensures there's just one instance of itself throughout the system's lifecycle. This prevents unnecessary reloads of configurations, optimizing performance.

The class fetches its configurations from the `YAML` files located in the various directories under the `/.agentforge/` path. It then populates its attributes with the pertinent data.

---

## Methods
1. [Initialization](#initialization)
2. [Load](#load)
3. [Chromadb](#chromadb)
4. [Get Config Element](#get-config-element)
5. [Get File Path](#get-file-path)
6. [Get LLM](#get-llm)
7. [Load Agent](#load-agent)
8. [Load Configs](#load-configs)
9. [Load From Folder](#load-from-folder)
10. [Load Actions](#load-actions)
11. [Load Tools](#load-tools)
12. [Load Persona](#load-persona)
13. [Get YAML Data](#get-yaml-data)
14. [Reload](#reload)
15. [Get Storage API](#get-storage-api)

---

## Initialization

### `__init__(self, config_path=None)`

**Purpose**: The constructor sets the path to the configuration directory and initializes placeholders for various configuration categories.

**Arguments**:
- `config_path`: Specifies the path to the configuration directory. Defaults to `.agentforge` or can be overridden by the `AGENTFORGE_CONFIG_PATH` environment variable.

**Workflow**:
1. Determine the configuration directory path.
2. Initialize attributes for various configuration categories like persona, actions, agents, tools, and settings.
3. Load the configurations from the respective `YAML` files.

```python
    def __init__(self, config_path=None):
        self.config_path = config_path or os.environ.get("AGENTFORGE_CONFIG_PATH", ".agentforge")

        # Placeholders for the data the agent needs which is located in each respective YAML file
        self.persona = {}
        self.actions = {}
        self.agent = {}
        self.tools = {}
        self.settings = {}

        # Here is where we load the information from the YAML files to their corresponding attributes
        self.load()
```

---

## Load

### `load(self)`

**Purpose**: Coordinates the entire configuration loading process. It calls various loading methods sequentially to fetch and populate configurations.

**Workflow**:
1. Load general setting configurations.
2. Load action configurations.
3. Load tool configurations.
4. Load persona configurations.

```python
def load(self):
    self.load_settings()
    self.load_actions()
    self.load_tools()
    self.load_persona()
```

---

## Chromadb

### `chromadb(self)`

**Purpose**: Retrieves the path and embedding details for the ChromaDB storage from the settings.

**Returns**:
- `db_path` (`str`): The path to the ChromaDB storage.
- `db_embed` (`str`): The embedding details for ChromaDB.

**Workflow**:
1. Fetch the `persist_directory` and `embedding` details from the `settings` attribute, specifically from the `ChromaDB` storage settings.
2. Return the path and embedding details.

```python
def chromadb(self):
    db_path = self.settings['storage'].get('ChromaDB', {}).get('persist_directory', None)
    db_embed = self.settings['storage'].get('ChromaDB', {}).get('embedding', None)

    return db_path, db_embed
```

---

## Get Config Element

### `get_config_element(self, case)`

**Purpose**: Provides access to specific configuration elements based on the provided case.

**Arguments**:
- `case` (`str`): Specifies the configuration category (e.g., "Persona", "Tools", "Actions").

**Returns**:
- A dictionary containing the configuration details for the specified category.

**Workflow**:
1. Use the switch-case mechanism to determine the configuration category.
2. Return the corresponding configuration data or "Invalid case" if the case doesn't match any known categories.

```python
def get_config_element(self, case):
    switch = {
        "Persona": self.persona,
        "Tools": self.tools,
        "Actions": self.actions
    }
    return switch.get(case, "Invalid case")
```

---

## Get File Path

### `get_file_path(self, file_name)`

**Purpose**: Constructs the full file path based on the given file name.

**Arguments**:
- `file_name` (`str`): The name of the file for which the path needs to be constructed.

**Returns**:
- The full path to the specified file.

**Workflow**:
1. Use the `pathlib` module to join the `config_path` with the provided `file_name`.
2. Return the constructed path.

```python
def get_file_path(self, file_name):
    return pathlib.Path(self.config_path) / file_name
```

---

## Get LLM

### `get_llm(self, api)`

**Purpose**: Configures and returns the Large Language Model (LLM) instance based on the specified API.

**Arguments**:
- `api` (`str`): Specifies the API library for the LLM.

**Returns**:
- An instance of the specified LLM.

**Workflow**:
1. Determine the model name based on the agent's settings or default model settings.
2. Define the available models and their configurations.
3. Fetch the model configuration based on the provided `api`.
4. Import the required module and class for the model.
5. Instantiate and return the model class with the necessary arguments.

```python
def get_llm(self, api):
    model_name = self.agent.get('Model', self.settings['models']['ModelSettings']['Model'])
    model_name = self.settings['models']['ModelLibrary'].get(model_name)

    models = {
        "claude_api": {
            "module": "anthropic",
            "class": "Claude",
            "args": [model_name],
        },
        "oobabooga_api": {
            "module": "oobabooga",
            "class": "Oobabooga",
        },
        "oobabooga_v2_api": {
            "module": "oobabooga",
            "class": "OobaboogaV2",
        },
        "openai_api": {
            "module": "openai",
            "class": "GPT",
            "args": [model_name],
        },
    }

    model = models.get(api)
    if not model:
        raise ValueError(f"Unsupported Language Model API library: {api}")

    module_name = model["module"]
    module = importlib.import_module(f".llm.{module_name}", package=__package__)
    class_name = model["class"]
    model_class = getattr(module, class_name)
    args = model.get("args", [])
    return model_class(*args)
```

---

## Load Agent

### `load_agent(self, agent_name)`

**Purpose**: Loads the agent-specific configurations from the respective YAML file.

**Arguments**:
- `agent_name` (`str`): Specifies the name of the agent whose configurations need to be loaded.

**Workflow**:
1. Use the provided `agent_name` to construct the path to the corresponding YAML file within the `agents` folder.
2. Load the YAML data from the file into the `agent` attribute.

```python
def load_agent(self, agent_name):
    self.agent = self.get_yaml_data(f"agents/{agent_name}.yaml")
```

---

## Load Setings

### `load_settings(self)`

**Purpose**: Initiates the loading of configurations from the `settings` folder.

**Workflow**:
1. Call the `load_from_folder` method with "settings" as the argument to load configurations from the `settings` folder.

```python
def load_settings(self):
    self.load_from_folder("settings")
```

---

## Load From Folder

### `load_from_folder(self, folder)`

**Purpose**: Loads configurations from a specified folder and organizes the data based on file names.

**Arguments**:
- `folder` (`str`): Specifies the folder from which configurations need to be loaded.

**Workflow**:
1. Determine the path to the specified folder.
2. Initialize the folder's attribute as a dictionary if it doesn't exist.
3. Iterate through each file in the folder, focusing on `.yaml` and `.yml` files.
4. Load the data from each file and organize it under the folder's dictionary based on file names and item names.

```python
def load_from_folder(self, folder):
    # Get the path for the provided folder name
    folder_path = self.get_file_path(folder)

    # If the folder attribute doesn't exist, initialize it as an empty dictionary
    if not hasattr(self, folder):
        setattr(self, folder, {})

    # Reference to the folder's dictionary
    folder_dict = getattr(self, folder)

    # Iterate over each file in the specified folder
    for file in os.listdir(folder_path):
        # Only process files with a .yaml or .yml extension
        if file.endswith(".yaml") or file.endswith(".yml"):
            # Load the YAML data from the current file
            data = self.get_yaml_data(os.path.join(folder, file))

            # Get the filename without the extension
            filename = os.path.splitext(file)[0]

            # Check if filename exists under the folder's dictionary, if not, initialize it as a dict
            if filename not in folder_dict:
                folder_dict[filename] = {}

            # Reference to the file name's dictionary
            file_dict = folder_dict[filename]

            for item_name, data_item in data.items():
                # Extract the name and store the data under that name in the file name's dictionary
                if item_name:
                    file_dict[item_name] = data_item

```

---

## Load Actions

### `load_actions(self)`

**Purpose**: Initiates the loading of action configurations from the `actions` folder.

**Workflow**:
1. Call the `load_from_folder` method with "actions" as the argument to load configurations from the `actions` folder.

```python
def load_actions(self):
    self.load_from_folder("actions")
```

---

## Load Tools

### `load_tools(self)`

**Purpose**: Starts the loading of tool configurations from the `tools` folder.

**Workflow**:
1. Call the `load_from_folder` method with "tools" as the argument to load configurations from the `tools` folder.

```python
def load_tools(self):
    self.load_from_folder("tools")
```

---

## Load Persona

### `load_persona(self)`

**Purpose**: Loads the persona configurations based on the directives set in the settings.

**Workflow**:
1. Determine the `persona_name` from the `settings` attribute.
2. Use the `persona_name` to construct the path to the corresponding YAML file within the `personas` folder.
3. Load the YAML data from the file into the `persona` attribute.

```python
def load_persona(self):
    persona_name = self.settings.get('directives', None).get('Persona', None)
    self.persona = self.get_yaml_data(f"personas/{persona_name}.yaml")
```

---

## Get YAML Data

### `get_yaml_data(self, file_name)`

**Purpose**: Fetches the data from a specified YAML file.

**Arguments**:
- `file_name` (`str`): Specifies the YAML file from which data needs to be fetched.

**Returns**:
- A dictionary containing the data from the specified YAML file.

**Workflow**:
1. Construct the full path to the specified file.
2. Try to open the file and load its contents as a dictionary.
3. If the file is not found or there's an error in the YAML format, handle the exceptions gracefully and return an empty dictionary.

```python
def get_yaml_data(self, file_name):
    file_path = self.get_file_path(file_name)
    try:
        with open(file_path, 'r') as yaml_file:
            return yaml.safe_load(yaml_file)
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return {}
    except yaml.YAMLError:
        print(f"Error decoding YAML from {file_path}")
        return {}
```

---

## Reload

### `reload(self, agent_name)`

**Purpose**: Reloads all configurations, including agent-specific, actions, tools, and persona configurations.

**Arguments**:
- `agent_name` (`str`): Specifies the agent whose configurations need to be reloaded.

**Workflow**:
1. Reload the specified agent's configurations.
2. Reload actions, tools, and persona configurations.

```python
def reload(self, agent_name):
    self.load_agent(agent_name)
    self.load_actions()
    self.load_tools()
    self.load_persona()
```

---

## Get Storage API

### `get_storage_api(self)`

**Purpose**: Retrieves the storage API details from the settings.

**Returns**:
- The storage API configurations from the `settings` attribute.

```python
def get_storage_api(self):
    return self.settings['storage']['StorageAPI']
```

---