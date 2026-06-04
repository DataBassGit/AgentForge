[![GitHub - License](https://img.shields.io/github/license/DataBassGit/AgentForge?logo=github&style=plastic&color=green)](https://github.com/DataBassGit/AgentForge/blob/dev/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/agentforge?logo=pypi&style=plastic&color=blue)](https://pypi.org/project/agentforge/)
[![Documentation](https://img.shields.io/badge/Docs-GitHub-blue?logo=github&style=plastic&color=green)](https://github.com/DataBassGit/AgentForge/tree/dev/docs)
[![Python Version](https://img.shields.io/badge/Python-%3E%3D3.10-blue?style=plastic&logo=python)](https://www.python.org/)
[![Homepage](https://img.shields.io/badge/Homepage-agentforge.net-green?style=plastic&logo=google-chrome)](https://agentforge.net/)

![AgentForge Logo](./docs/images/AF-Banner.jpg)

# AgentForge

**AgentForge** is a low-code framework for rapid development, testing, and iteration of AI-powered autonomous agents and cognitive architectures. Its core concepts - flexible **Agents**, declarative **Cogs**, and optional **Memory** - support both simple first runs and sophisticated multi-agent orchestration.

Compatible with a range of LLM models—including OpenAI, Google's Gemini, Anthropic's Claude, and local models via [Ollama](https://ollama.com) or [LMStudio](https://lmstudio.ai)—AgentForge lets you run different models for different agents as needed.

If you are new to AgentForge, start with the public docs hub before opening schemas, memory, storage, subclassing, utilities, or legacy Tools/Actions references.

---

## Table of Contents

1. [Start Here](#start-here)
2. [Features](#features)
3. [Documentation](#documentation)
4. [Contributing](#contributing)
5. [Contact Us](#contact-us)
6. [License](#license)

---

## Start Here

Start with **[AgentForge Documentation](docs/README.md)**.

The docs hub gives the recommended order for the first smoke test, the first real Codex-backed model run, the beginner Cog examples, and the advanced references.

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

---

## Documentation

- **[Docs Hub](docs/README.md)**: Canonical public navigation for first runs and reference material.
- **[Quickstart](docs/guides/quickstart.md)**: Install, scaffold `.agentforge/`, and run a no-credential debug smoke test.
- **[First Real Model Run](docs/guides/first_real_model_run.md)**: Use the default Codex OAuth model path or choose another provider.
- **[Advanced Reference](docs/guides/advanced_reference.md)**: Find Agents, Cogs, settings, APIs, memory, storage, utilities, and legacy Tools/Actions references after the beginner path is clear.

---

## Contributing

We welcome issues and pull requests with improvements or bug fixes!

---

## Contact Us

- **Email**: contact@agentforge.net
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)

---

## License

This project is licensed under the **GNU General Public License v3.0**. See [LICENSE](LICENSE) for more details.
