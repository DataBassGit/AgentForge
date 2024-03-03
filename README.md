[![GitHub - License](https://img.shields.io/github/license/DataBassGit/AgentForge?logo=github&style=plastic&color=green)](https://github.com/DataBassGit/AgentForge/blob/dev/LICENSE)[![PyPI](https://img.shields.io/pypi/v/agentforge?logo=pypi&style=plastic&color=blue)](https://pypi.org/project/agentforge/)[![Documentation](https://img.shields.io/badge/Docs-GitHub-blue?logo=github&style=plastic&color=green)](https://github.com/DataBassGit/AgentForge/tree/dev/docs)[![Python Version](https://img.shields.io/badge/Python-3.11-blue?style=plastic&logo=python)](https://www.python.org/)

[![Homepage](https://img.shields.io/badge/Homepage-agentforge.net-green?style=plastic&logo=google-chrome)](https://agentforge.net/)

# AgentForge 0.2.X
AgentForge is a low-code framework tailored for the rapid development, testing, and iteration of AI-powered autonomous agents and Cognitive Architectures. Compatible with a range of LLM models — currently supporting OpenAI, Google's Gemini, Anthropic's Claude, and Oobabooga (local) — it offers the flexibility to run different models for different agents based on your specific needs.

Whether you're a newbie looking for a user-friendly entry point or a seasoned developer aiming to build complex cognitive architectures, this framework has you covered.

Our database-agnostic framework is designed for seamless extensibility. While [ChromaDB](https://www.trychroma.com/) is our go-to database, integration with other databases is straight-forward, making it an ideal playground and solid foundation for various AI projects.

In summary, AgentForge is your beta-testing ground and future-proof hub for crafting intelligent, model-agnostic, and database-flexible autonomous agents.

---

## Table of Contents
1. [Features](#features)
2. [Documentation](#documentation)
3. [Contributing](#contributing)
4. [Contact Us](#contact-us)
5. [License](#license)

---

## Features

* Build Custom Agents And Cognitive Architectures Easily (Multi-Agent Scripts)
* Customizable Agent Memory Management
* Customizable Agent Template
* Customizable Tools & Actions
* LLM Agnostic Agents (Each Agent can call different LLMs if needed)
* On-The-Fly Prompt Editing
* OpenAI, Google & Anthropic API Support
* Open-Source Model Support ([Oobabooga](https://github.com/oobabooga/text-generation-webui))

### Partially Implemented Features
* Knowledge Graphs:
  * Document Consumption
  * Knowledge Traversal and Retrieval

> **Note**: While the basic implementation is there, these features still need more work before we consider them to be completed.

---

## Documentation

Welcome to the **AgentForge** framework documentation. This comprehensive guide will support you whether you're just getting started or diving deep into custom configurations and advanced features. Here, you'll find detailed insights into the various components that make up our system.

### **Installation and Usage:**

- **[Getting Started with AgentForge](docs/Guides/InstallationGuide.md)**: Begin your journey with a straightforward setup guide, covering everything from initial installation to launching your first bot.

### **Core Concepts:**

- **[Agents](docs/Agents/Agents.md)**: Dive deep into the agents' world. Learn how they operate, respond, and can be customized.

- **[Modules](docs/Modules/Modules.md)**: Explore multi-agent scripts, the hierarchies above agents. Understand how Modules coordinate various agents and manage the flow of information to achieve specific goals.

- **[LLM API Integration](docs/LLMs/LLMs.md)**: Understand how AgentForge connects with various Large Language Model (LLM) APIs.

- **[Settings](docs/Settings/Settings.md)**: Delve into the model, storage and system configurations – tweak the behavior of the system.

- **[Personas](docs/Personas/Personas.md)**: Personas encapsulate information accessible to the agents. Acting as a resource of knowledge for the system/agent, they are not limited to defining agents' personalities but can include any kind of information that could be utilized by the agents as needed.

- **[Tools & Actions](docs/ToolsAndActions/Overview.md)**: The system's utility belt. Understand the tools available and how they can be choreographed into actionable sequences.

- **[Utilities](docs/Utils/UtilsOverview.md)**: Explore the array of utility functions and tools that supercharge the system's capabilities.  (Note: Documentation not implemented yet)

> **Note**: Our documentation is a living entity, continuously evolving. Some links or features may still be under development. We appreciate your patience and welcome your feedback to improve the documentation.

---

## Contributing

Feel free to open issues or submit pull requests with improvements or bug fixes. Your contributions are welcome!

### Special Note
We're on the lookout for a UI/UX collaborator who's passionate about open-source and wants to join the team to help develop a front-end for this framework. This isn't a job offer, but rather an invitation to be a part of something cool. Interested? We'd love to chat! (See the [Contact Us](#contact-us) section below for details.)

---

## Contact Us

If you're keen on contributing or just want to reach out to us, here's how to get in touch:

- **Email**: contact@agentforge.net
- **Discord**: Feel Free to drop by our [Discord Server](https://discord.gg/ttpXHUtCW6)

---

## License
This project is licensed under the GNU General Public License. See [LICENSE](LICENSE) for more details.
