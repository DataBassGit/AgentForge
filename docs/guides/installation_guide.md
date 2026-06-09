# Installation Guide

This support guide gives installation and environment details for **AgentForge**.

If you are doing your first no-credential run, start with [Quickstart](quickstart.md); return here when you need extra setup detail.

---

## Installation Steps

### 1. Ensure Python is Installed

- **Python Version**: AgentForge requires **Python 3.12 or newer**. Python 3.14 is the recommended target when choosing a fresh interpreter.
- **Check Python Version**:

  ```shell
  python3 --version
  ```
  
  If Python is not installed or is older than **3.12**, download a supported version from the official [Python website](https://www.python.org/downloads/).

### 2. Set Up a Virtual Environment (Optional But Recommended)

Using a virtual environment helps avoid conflicts with system-wide packages.

- **Create a Virtual Environment**:

  ```shell
  python3 -m venv venv
  ```

- **Activate the Virtual Environment**:

  - On **Unix/macOS**:

    ```shell
    source venv/bin/activate
    ```

  - On **Windows**:

    ```shell
    venv\Scripts\activate
    ```

### 3. Install AgentForge

With the virtual environment activated, install **AgentForge** using pip:

```shell
pip install agentforge
```

### 4. Initialize Your Project

Navigate to the root of the project that should own your **AgentForge** resources and initialize the project:

```shell
python -m agentforge.init_agentforge
```

This command creates a `.agentforge` folder in your current project with YAML settings, prompts, cogs, tools, actions, and personas:

```
your_project/
  .agentforge/
    actions/
    cogs/
    custom_apis/
    personas/
    prompts/
    settings/
    tools/
```

Some scaffolded folders are advanced or compatibility surfaces. Beginners can start with settings and prompts, then return to cogs, tools, actions, personas, and custom APIs later.

#### Project Root Discovery

AgentForge finds the active project root in this order:

1. An explicit `Config(root_path=...)` or `Config.reset(root_path=...)` call.
2. The `AGENTFORGE_ROOT` environment variable.
3. Auto-discovery walking upward from the running script until it finds `.agentforge/`.

For a beginner project, keep your script inside the project that contains `.agentforge/`.

Set `AGENTFORGE_ROOT=/path/to/your/project` when your script lives somewhere else or you want the project root to be unambiguous.

Explicit `Config(root_path=...)` and `Config.reset(root_path=...)` are advanced deterministic setup options used most often in tests or tools.

### 5. Initialize Codex OAuth For The Default Real Model

Provider credentials are not required for the no-credential debug-mode first run.

The shipped scaffold defaults real model calls to OpenAI Codex through OAuth.
Run the OAuth login command after project initialization when you are ready to use the default real-model path:

```shell
python -m agentforge.init_codex_oauth
```

This stores OAuth credentials used by the `Codex` provider.
Codex OAuth is separate from `OPENAI_API_KEY`.

Use [First Real Model Run](first_real_model_run.md) for the beginner real-provider path before treating this section as reference detail.

### 6. Set Up Optional API Keys Or Local Services

Depending on the language model service you plan to use with **AgentForge**, you may need to set up environment variables with your API keys before a real model call. If you're using local models like **LM Studio** or **Ollama**, you do **not** need to set up environment variables for API keys, but you do need the local service running.

You can set environment variables in one of two ways:

#### **Option 1: Export Environment Variables Directly**

For example, for OpenAI:

```bash
export OPENAI_API_KEY='your-openai-api-key'
```

For Anthropic:

```bash
export ANTHROPIC_API_KEY='your-anthropic-api-key'
```

For Google Gemini:

```bash
export GOOGLE_API_KEY='your-google-api-key'
```

#### **Option 2: Use a `.env` File**

Create a file named `.env` in your project directory and add your API keys like this:

```env
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GOOGLE_API_KEY=your-google-api-key
```

To load these variables in your Python scripts, install the `python-dotenv` package:

```shell
pip install python-dotenv
```

Then, add the following lines at the top of your main script (before you use the environment variables):

```python
from dotenv import load_dotenv
load_dotenv()
```

This will automatically load the variables from your `.env` file into the environment for your script.

---

## Using AgentForge

After project setup, continue with the [Quickstart](quickstart.md), [First Real Model Run](first_real_model_run.md), and [Using AgentForge Guide](using_agentforge.md).

---

## Next Steps

- Review [First Real Model Run](first_real_model_run.md) first, then use the [Prerequisites Guide](prerequisites_guide.md) if you are preparing API keys or local model services.

- If you're having trouble with **AgentForge**, please head over to the [Troubleshooting Guide](troubleshooting_guide.md) for solutions to common issues.
