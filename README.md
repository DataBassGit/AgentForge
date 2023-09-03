# AgentForge
AgentForge is a low-code framework tailored for the rapid development, testing, and iteration of AI-powered autonomous agents. Compatible with a range of LLM models — currently supporting OpenAI, Anthropic's Claude, and Oobabooga — it offers the flexibility to run different models for different agents based on your specific needs.

Whether you're a newbie looking for a user-friendly entry point or a seasoned developer aiming to build complex cognitive architectures, this framework has you covered.

Our database-agnostic framework is designed for seamless extensibility. While [ChromaDB](https://www.trychroma.com/) is our go-to database, integration with other databases is straight-forward, making it an ideal playground and solid foundation for various AI projects.

In summary, AgentForge is your beta-testing ground and future-proof hub for crafting intelligent, model-agnostic, and database-flexible autonomous agents.

## Table of Contents
1. [Features](#features)
2. [Requisites](#requisites)
3. [Pre-Installation](#pre-installation)
4. [Installation](#installation)
5. [Dev-build Installation](#dev-build-installation)
6. [Usage](#usage)
7. [Documentation](#documentation)
8. [Contributing](#contributing)
9. [Contact Us](#contact-us)
10. [License](#license)

---
## Features

* Rapidly build and test cognitive architectures
* Directly customize how agents handle memory
* Open source model support
* Easily edit prompts
* Different LLM for each prompt
* Build Custom Agents

### Coming Soon

* Custom Tools/Actions
* Knowledge Graphs
* Edit prompts live! (You can even have multiple prompt templates and switch!)

## Requisites

**Note**: If you already have all the requisites below, you can skip ahead to the [Pre-Installation](#pre-installation) section.

Make sure you have the following set up:

### Python
- Python must be installed, and the PATH variable should be configured accordingly.

### Microsoft C++ Build Tools
1. [ChromaDB](https://www.trychroma.com/) requires [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
2. Once downloaded, mark the 'Desktop Development with C++' for installation. It should automatically select these optional packages for you.
   ![Cpp_Setup](/docs/Images/Cpp_Setup.png)
3. When installation is complete, you'll see a message that says 'All installations are up-to-date.'
   ![Cpp_Completion](/docs/Images/Cpp_Completion.png)
4. Done! Close the Visual Studio installer.

---

## Pre-Installation

Before you get started with AgentForge, there are a few things you should know:

### LLM Models
- **Local:** AgentForge can run using self-hosted models via the Oobabooga implementation. You'll need to host the model either locally yourself or on a cloud server as the Oobabooga implementation in AgentForge only handles the connection to the server created by Oobabooga; it doesn't load or install any models.
- **Cloud-Based:** To use cloud-based LLM models like OpenAI, you'll need to obtain and set up API keys in your user environment variables.

### LLM API Keys
- You don't need API keys for both Claude and OpenAI if you plan on using just one. No API keys are needed if you're using the Oobabooga implementation. The model you wish to use can be specified in the [Configuration]() file.

### Other Services
- If you're planning to use Google Search functionalities, you'll need both a Google API key and a Google Search Engine ID key.

### Environment Variables
Set your **User Environment Variables** names to the following:

- **Claude**: ANTHROPIC_API_KEY 
- **OpenAI**: OPENAI_API_KEY
- **Google**: GOOGLE_API_KEY
- **Google Search Engine ID**: SEARCH_ENGINE_ID

![Environment Variables](/docs/Images/EnvKeys.png)

### 3rd-Party API Documentation
- We haven't provided guides for obtaining these API keys as it's outside the scope of this project. Plenty of resources are available online to guide you through the process.

---

## Installation

1. Install AgentForge:

```shell
pip install agentforge
```

2. Navigate to where you want your bot's project folder:

```shell
cd c:\bot
```

3. Run the initialization script:

```shell
agentforge init
```

Additionally, if you want to try our demo architecture, run the following command to copy our bot script to your project folder:

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

```shell+
pip install -e .
```

---

## Usage

Each bot or architecture you create should contain an `.agentforge` folder that holds its [Persona](docs/Persona/) folder along with other configuration files.

**Important**: Before running any bot, we need to make sure that the configuration files have the correct LLM settings. If you've selected an OpenAI model, for example, the system will look for the corresponding API key in your environment variables. This applies not only to the default settings but also to individual [SubAgents](docs/Agents/SubAgents/), as they can override these settings and call different models if needed.


### For Custom Agents

To get started with custom agents, navigate to `Examples/CustomAgents/`. Inside, you'll find the `.agentforge/` folder with its configuration files as well as an `Agent` folder which contains an example of a custom [SubAgent](docs/Agents/SubAgents/). To know more about how to use and create your own agents, check out the [Agents Page](/docs/Agents/AgentSuperClass.md).

### For SalienceBot Example

If you've installed our Salience example, head over to `Examples/SalienceBot/.agentforge/` to find its configuration files.

To run the SalienceBot demo, go to `Examples/SalienceBot/` in your console and run:

```shell
python salience.py
```

This will execute a simple bot script that uses our default [SubAgents](docs/Agents/SubAgents/) to complete an objective by breaking it down into tasks, subsequently executing them and checking for completion.

For a more detailed break-down of our `Salience` example please refer to the [Salience Page]()

**Important** : Whenever a bot or architecture runs, it will first initialize ChromaDB (or whichever database is used) as it will act as the memory for the agents. The first time Chroma is initialized on a system it needs to download a few language models for sentence embedding, so it is normal for it to take several minutes to run the first time. Any subsequent runs will not have this issue as long as Chroma has previously downloaded the models.

---

## Documentation

For more in-depth documentation, please refer to the following sections:

**Note**: The documentation outlined in this section is a work in progress, some links and files may not be correctly linked nor available yet.

- **[Agent](docs/Config/AgentSuperClass.md)**: Comprehensive guides on how Agents work.
- **[Config](docs/Config/)**: Documentation on system related configurations.
- **[LLM](docs/LLM/)**: All you need to know about integrating LLM models.
- **[Persona](docs/Persona/)**: How to configure and use personas.
- **[SubAgents](docs/Agents/SubAgents/)**: Creating and customizing SubAgents.
- **[Tools & Actions](docs/Tools&Actions/)**: How tools and actions are defined and executed by Agents.
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
