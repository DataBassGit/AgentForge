Great! Thanks for sharing the updated code for the `Config` class. I'll now help you revise your markdown documentation to reflect these changes.

---

# Config Class

Welcome to the Config Class documentation!
This class is the backbone of our system's configuration management,
ensuring settings are fetched, parsed, and made available seamlessly.

---

## 📌 Key Insight: The Backbone of Configuration

The `Config` class serves as the central hub for configuration management,
ensuring uniform access and efficient performance.
It fetches its configurations from `YAML` files located under the `/.agentforge/` path,
populating its attributes with the pertinent data.

---

## Methods Overview
1. [Initialization](#initialization)
2. [Load](#load)
3. [Chromadb](#chromadb)
4. [Find File in Directory](#find-file-in-directory)
5. [Get Config Element](#get-config-element)
6. [Get File Path](#get-file-path)
7. [Get LLM](#get-llm)
8. [Load Agent](#load-agent)
9. [Load Settings](#load-settings)
10. [Load From Folder](#load-from-folder)
11. [Load Actions](#load-actions)
12. [Load Tools](#load-tools)
13. [Load Persona](#load-persona)
14. [Reload](#reload)
15. [Get YAML Data](#get-yaml-data)

---

## Initialization

### `__init__(self, config_path=None)`

**Purpose**: Initializes the configuration path and placeholders for various configuration categories.

**Arguments**:
- `config_path`: Optional path to the configuration directory.

**Workflow**:
1. Determine the configuration directory path.
2. Initialize attributes for configuration categories.
3. Load the configurations.

```python
def __init__(self, config_path=None):
    self.config_path = config_path or os.environ.get("AGENTFORGE_CONFIG_PATH", ".agentforge")

    # Placeholders for the data the agent needs which is located in each respective YAML file
    self.persona_name = {}
    self.personas = {}
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

**Purpose**: Coordinates the configuration loading process, fetching and populating settings.

**Workflow**:
1. Load settings, actions, tools, and persona configurations.

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

**Purpose**: Retrieves ChromaDB storage path and embedding details.

**Returns**:
- `db_path`: Path to the ChromaDB storage.
- `db_embed`: Embedding details for ChromaDB.

```python
def chromadb(self):
    db_path = self.settings['storage'].get('ChromaDB', {}).get('persist_directory', None)
    db_embed = self.settings['storage'].get('ChromaDB', {}).get('embedding', None)

    return db_path, db_embed
```

---

## Find File in Directory

### `find_file_in_directory(self, directory, filename)`

**Purpose**: Searches for a file in a directory and its subdirectories.

**Arguments**:
- `directory`: The directory to search in.
- `filename`: The name of the file to find.

**Returns**:
- Full path to the found file or `None`.

```python
def find_file_in_directory(self, directory, filename):
    """
    Recursively searches for a filename in a directory and its subdirectories.
    Returns the full path if found, or None otherwise.
    """
    directory = pathlib.Path(self.get_file_path(directory))

    for file_path in directory.rglob(filename):
        return file_path
    return None
```

---

## Get Config Element

### `get_config_element(self, case)`

**Purpose**: Accesses specific configuration elements based on the provided case.

**Arguments**:
- `case`: The configuration category (e.g., "Persona", "Tools", "Actions").

**Returns**:
- Configuration details for the specified category or "Invalid case" if not found.

```python
def get_config_element(self, case):
    switch = {
        "Persona": self.personas[self.persona_name],
        "Tools": self.tools,
        "Actions": self.actions
    }
    return switch.get(case, "Invalid case")
```

---

## Get File Path

### `get_file_path(self, file_name)`

**Purpose**: Constructs the full path for a given file.

**Arguments**:
- `file_name`: The name of the file.

**Returns**:
- Full path to the specified file.

```python
def get_file_path(self, file_name):
    return pathlib.Path(self.config_path) / file_name
```

---

## Get LLM

### `get_llm(self, api, model)`

**Purpose**: Configures and returns an instance of a Large Language Model.

**Arguments**:
- `api`: The API library for the LLM.
- `model`: The model name.

**Returns**:
- An instance of the specified LLM.

```python
def get_llm(self, api, model):
    try:
        model_name = self.settings['models']['ModelLibrary'][api]['models'][model]['name']
        module_name = self.settings['models']['ModelLibrary'][api]['module']
        class_name = self.settings['models']['ModelLibrary'][api]['class']
    
        module = importlib.import_module(f".llm.{module_name}", package=__package__)
        model_class = getattr(module, class_name)
        args = [model_name]
        return model_class(*args)

    except Exception as e:
        print(f"Error Loading Model: {e}")
        raise
```

---

## Load Agent

### `load_agent(self, agent_name)`

**Purpose**: Loads agent-specific configurations.

**Arguments**:
- `agent_name`: The name of the agent.

**Workflow**:
1. Finds and loads the agent's YAML configuration.

```python
def load_agent(self, agent_name):
    path_to_file = self.find_file_in_directory("agents", f"{agent_name}.yaml")
    if path_to_file:
        self.agent = get_yaml_data(path_to_file)
    else:
        raise FileNotFoundError(f"Agent {agent_name}.yaml not found.")
```

---

## Load Settings

### `load_settings(self)`

**Purpose**: Initiates the loading of general settings.

**Workflow**:
1. Loads settings configurations from the `settings` folder.

```python
def load_settings(self):
    self.load_from_folder("settings")
```

---

## Load From Folder

### `load_from_folder(self, folder)`

**Purpose**: Loads configurations from a specified folder.

**Arguments**:
- `folder`: The folder to load configurations from.

**Workflow**:
1. Loads and organizes data from YAML files in the specified folder.

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
            pathy = os.path.join(folder_path, file)
            data = get_yaml_data(pathy)

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

**Purpose**: Initiates the loading of action configurations.

**Workflow**:
1. Loads action configurations from the `actions` folder.

```python
def load_actions(self):
    self.load_from_folder("actions")
```

---

## Load Tools

### `load_tools(self)`

**Purpose**: Starts the loading of tool configurations.

**Workflow**:
1. Loads tool configurations from the `tools` folder.

```python
def load_tools(self):
    self.load_from_folder("tools")
```

---

## Load Persona

### `load_persona(self)`

**Purpose**: Loads persona configurations.

**Workflow**:
1. Determines and loads the specified persona configuration.

```python
def load_persona(self):
    self.persona_name = self.settings.get('directives', None).get('Persona', None)
    self.load_from_folder("personas")
```

---

## Reload

### `reload(self, agent_name)`

**Purpose**: Reloads all configurations, including agent-specific configurations.

**Arguments**:
- `agent_name`: The agent to reload configurations for.

**Workflow**:
1. Reloads the specified agent's configurations and others.

```python
def reload(self, agent_name):
    self.load_agent(agent_name)
    self.load_actions()
    self.load_tools()
    self.load_persona()
```

---

## Get YAML Data

### `get_yaml_data(self, file_name)`

**Purpose**: Fetches data from a YAML file.

**Arguments**:
- `file_name`: The YAML file to fetch data from.

**Returns**:
- Data from the specified YAML file.

```python
def get_yaml_data(self, file_name):
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