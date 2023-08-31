# AgentForge
AgentForge is a low-code framework tailored for the rapid development, testing, and iteration of AI-powered autonomous agents. Compatible with a range of LLM models — currently supporting OpenAI, Anthopic's Claude, and Oobabooga — it offers the flexibility to run different models for different agents based on your specific needs.

Whether you're a newbie looking for a user-friendly entry point or a seasoned developer aiming to build complex cognitive architectures, this framework has you covered.

Our database-agnostic framework is designed for seamless extensibility. While [ChromaDB](https://www.trychroma.com/) is our go-to database, integration with other databases is straight-forward, making it an ideal playground and solid foundation for various AI projects.

In summary, AgentForge is your beta-testing ground and future-proof hub for crafting intelligent, model-agnostic, and database-flexible autonomous agents.

## Table of Contents
1. [Pre-Installation](#pre-installation)
2. [Installation](#installation)
3. [Dev-build Installation](#dev-build-installation)
4. [Usage](#usage)
5. [Documentation](#documentation)
6. [Contributing](#contributing)
7. [Contact Us](#contact-us)
8. [License](#license)

---

## Pre-Installation

Before you get started with AgentForge, there are a few things you should know:

### LLM Models
- **Local:** AgentForge can run using local models via the Oobabooga implementation. You'll need to host the model locally yourself as the Oobabooga implementation in AgentForge only handles the connection to the local server created by Oobabooga; it doesn't load or install any models.
- **Cloud-Based:** To use cloud-based LLM models like OpenAI, you'll need to obtain and set up API keys in your user environment variables.

### Other Services
- If you're planning to use Google Search functionalities, you'll need both a Google API key and a Google Search Engine ID key. 

### 3rd-Party API Documentation
- We haven't provided guides for obtaining these API keys as it's outside the scope of this project. Plenty of resources are available online to guide you through the process.

### Environment Variables
Set your **User Environment Variables** names to the following:

- **Claude**: ANTHROPIC_API_KEY 
- **OpenAI**: OPENAI_API_KEY
- **Google**: GOOGLE_API_KEY
- **Google Search Engine ID**: SEARCH_ENGINE_ID

![Environment Variables](/docs/Images/EnvKeys.png)

---

## Installation

1. Install AgentForge:

```shell
pip install agentforge
```

2. Navigate to where you want your bot's project folder:

```shell
cd c:\bot\folder
```

3. Run the initialization script:

```shell
agentforge init
```

Additionally, if you want to try our demo agent, run the following command to copy our bot script to your project folder:

```shell
agentforge salience
```

---

## Dev-build Installation

If you want to install the build from the dev branch and help with development, follow these instructions instead:

Clone the GitHub repository:

```shell
git clone https://github.com/DataBassGit/AgentForge.git
```

Install the required dependencies:

```shell
pip install -e .
```

---

## Usage

Each bot or architecture you create should contain an `.agentforge` folder that holds its configuration files, including `default.json` which currently represents the persona and contains each agent's prompts.

### For Custom Agents

To get started with custom agents, navigate to `Examples/CustomAgents/.agentforge/`. Inside, you'll find a `default.json` file where you can edit the persona's name, objective, and tasks. To know more about how to use and create your own agents, check out the [Agents Page](/docs/Agents/AgentClass.md).

### For SalienceBot Example

If you've installed our Salience example, head over to `Examples/SalienceBot/.agentforge/` to find its `default.json` and other configuration files.

To run the SalienceBot demo, go to `Examples/SalienceBot/` in your console and run:

```shell
python salience.py
```

This will execute a simple bot script that uses our default SubAgents to complete an objective by breaking it down into tasks, subsequently executing them and checking for completion.

For a more detailed break-down of our `Salience` example please refer to the [Salience Page]()

**Note**: We're planning to expand how personas work to offer more flexibility in future releases.

---

## Documentation

For more in-depth documentation, please refer to the following sections:

**Note**: The documentation outlined in this section is a work in progress some links and files may not be correctly linked nor available yet.

- **[Agent](docs/Config/AgentClass.md)**: Comprehensive guides on how Agents work.
- **[Config](docs/Config/)**: Documentation on system related configurations.
- **[LLM](docs/LLM/)**: All you need to know about integrating LLM models.
- **[Persona](docs/Persona/)**: How to configure and use personas.
- **[SubAgents](docs/Agents/SubAgents/)**: Creating and customizing SubAgents.
- **[Tools](docs/Tools&Actions/)**: How tools and actions are defined and executed by Agents.
- **[Utils](docs/Utils/)**: Miscellaneous utilities.

---

## Contributing

Feel free to open issues or submit pull requests with improvements or bug fixes. Your contributions are welcome!

### Special Note
We're on the lookout for a UI/UX collaborator who's passionate about open-source and wants to join the team to help develop a front-end for this framework. This isn't a job offer, but rather an invitation to be a part of something cool. Interested? We'd love to chat! (See the [Contact Us](#contact-us) section below for details.)

---

## Contact Us

If you're keen on contributing or just want to reach out to us, here's how to get in touch:

- **Email**: contact@agentforge.net
- **Discord**: We're evaluating opening our Discord server to the public. For now, we're extending direct invites to community members who are active in the AI and Autonomous Agents space.

---

## License
This project is licensed under the GNU General Public License. See [LICENSE](LICENSE) for more details.
