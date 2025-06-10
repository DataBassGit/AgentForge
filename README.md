[![GitHub - License](https://img.shields.io/github/license/DataBassGit/AgentForge?logo=github&style=plastic&color=green)](https://github.com/DataBassGit/AgentForge/blob/dev/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/agentforge?logo=pypi&style=plastic&color=blue)](https://pypi.org/project/agentforge/)
[![Documentation](https://img.shields.io/badge/Docs-GitHub-blue?logo=github&style=plastic&color=green)](https://github.com/DataBassGit/AgentForge/tree/dev/docs)
[![Python Version](https://img.shields.io/badge/Python-3.11-blue?style=plastic&logo=python)](https://www.python.org/)
[![Homepage](https://img.shields.io/badge/Homepage-agentforge.net-green?style=plastic&logo=google-chrome)](https://agentforge.net/)

![AgentForge Logo](./docs/images/AF-Banner.jpg)

# AgentForge

**AgentForge** is a low-code framework for rapid development, testing, and iteration of AI-powered autonomous agents and cognitive architectures. Its core concepts—flexible **Agents**, declarative **Cogs**, and integrated **Memory**—enable both simple agent implementations and sophisticated multi-agent orchestration with minimal code.

Compatible with a range of LLM models—including OpenAI, Google's Gemini, Anthropic's Claude, and local models via [Ollama](https://ollama.com) or [LMStudio](https://lmstudio.ai)—AgentForge lets you run different models for different agents as needed.

Whether you're new to AI agents or building advanced cognitive systems, **AgentForge** provides the tools to craft intelligent, model-agnostic, and database-flexible autonomous agents.

---

## Table of Contents

1. [Features](#features)
2. [Documentation](#documentation)
3. [Contributing](#contributing)
4. [Contact Us](#contact-us)
5. [License](#license)

---

## Features

Build agents and cognitive architectures (multi-agent systems) with:

- **Declarative Cogs**: Orchestrate multi-agent workflows, branching logic, and memory using simple YAML files. Cogs are the primary way to compose agents into complex, reusable workflows.
- **Customizable Agents**: Define agents using YAML prompt templates and configuration.
- **Integrated Memory**: Add contextual memory to agents and cogs for coherent, context-aware interactions. Memory nodes are declared in Cogs and made available to agents automatically.
- **Personas**: Configure agent identity, style, and context using persona YAML files.
- **Dynamic Prompt Templates**: Use flexible prompt templates that adapt to various contexts and memory.
- **LLM Agnostic**: Run different agents with different LLMs as needed.
- **On-The-Fly Prompt Editing**: Modify prompts in real-time without restarting the system.
- **OpenAI, Google & Anthropic API Support**: Integrate with popular LLM APIs.
- **Open-Source Model Support**: Leverage local models through [Ollama](https://ollama.com) and [LMStudio](https://lmstudio.ai).

> **Note:** Actions and tools are deprecated as of this release and will be replaced in a future version with a new system based on the MCP standard.

---

## Documentation

Comprehensive documentation is available to help you get started and go deeper:

### **Getting Started**

- **[Installation Guide](docs/guides/installation_guide.md)**: Step-by-step instructions to install **AgentForge**.
- **[Using AgentForge](docs/guides/using_agentforge.md)**: Learn how to run agents, create custom agents, and build cognitive architectures with examples.
- **[Prerequisites Guide](docs/guides/prerequisites_guide.md)**: Details all pre-installation requirements and dependencies.
- **[Troubleshooting Guide](docs/guides/troubleshooting_guide.md)**: Find solutions to common issues and platform-specific problems.

### **Core Concepts**

- **[Agents](docs/agents/agents.md)**: Create and customize individual AI agents for various tasks.
- **[Cogs](docs/cogs/cogs.md)**: Design multi-agent workflows with branching logic and memory using YAML configuration. Cogs are the main way to build and run multi-agent systems in AgentForge.
- **[Memory](docs/memory/memory.md)**: Add contextual memory to your agents and cogs for more coherent, context-aware interactions. Memory is managed declaratively in Cogs and accessed in agent prompts.
- **[API Integration](docs/apis/apis.md)**: Understand how **AgentForge** connects with various Large Language Model (LLM) APIs.
- **[Personas](docs/personas/personas.md)**: Use personas to encapsulate agent identity, style, and reusable knowledge.
- **[Settings](docs/settings/settings.md)**: Configure models, storage, and system behavior.
- **[Storage](docs/storage/chroma_storage.md)**: **AgentForge** uses ChromaDB as its vector store implementation for memory.
- **[Tools & Actions](docs/tools_and_actions/overview.md)**: *Deprecated*—will be replaced by an MCP-based system in a future release.
- **[Utilities](docs/utils/utils_overview.md)**: Explore utility functions and tools that enhance the system's capabilities.

---

## Contributing

We welcome issues and pull requests with improvements or bug fixes!

### Special Note
We’re looking for a volunteer UI/UX collaborator—ideally someone who’s genuinely passionate about open-source—to help us develop a front-end for **AgentForge**. To be clear, this isn’t a paid position or formal job; we’re just a couple of backend folks looking to team up with someone interested in contributing their front-end skills for the love of the project and learning together. If you’re interested in collaborating, see [Contact Us](#contact-us) below.

---

## Contact Us

- **Email**: contact@agentforge.net
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)

---

## License

This project is licensed under the **GNU General Public License v3.0**. See [LICENSE](LICENSE) for more details.
