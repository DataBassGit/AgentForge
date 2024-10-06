# Installation Guide

This guide will walk you through the steps required to install **AgentForge** on your system.

---

## Installation Steps

### 1. Ensure Python is Installed

- **Python Version**: AgentForge requires **Python 3.11**.
- **Check Python Version**:

  ```shell
  python3 --version
  ```

  If Python is not installed or the version is lower than 3.11, download version 3.11 from the [official Python website](https://www.python.org/downloads/).

### 2. Set Up a Virtual Environment (Recommended)

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

Navigate to your project directory and initialize your AgentForge project:

```shell
python -m agentforge.init_agentforge
```

This command creates a new `.agentforge` folder in your project with sub-folders containing **YAML** files:

```
your_project/
  .agentforge/
    actions/
    personas/
    prompts/
    settings/
    tools/
```

Your project is now set up and ready to use the AgentForge framework.

### 5. Deactivate the Virtual Environment (Optional)

When you're done working, deactivate the virtual environment:

```shell
deactivate
```

Remember to activate the virtual environment (`source venv/bin/activate` or `venv\Scripts\activate`) whenever you return to work on your project.

---

**Next Steps**:

- Proceed to the [Using AgentForge Guide](UsingAgentForge.md) to learn how to run agents and build cognitive architectures.
- Review the [Prerequisites Guide](PrerequisitesGuide.md) if you haven't set up API keys or other necessary configurations.
- If you're having trouble with **AgentForge** please head over to the [Troubleshooting Guide](TroubleshootingGuide.md) for solutions to common issues.
