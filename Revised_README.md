# AgentForge

AgentForge is an advanced AI-driven task automation system designed for generating, prioritizing, and executing tasks based on specified objectives.
Utilizing state-of-the-art technologies such as ChromaDB, SentenceTransformer, and the OpenAI API for text generation, AgentForge aims to deliver efficient and reliable task management solutions.

## Table of Contents
1. [Features](#features)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Contributing](#contributing)
5. [License](#license)
6. [Contact](#contact)
7. [FAQ](#faq)

## Features
- User-friendly, low-code/no-code framework
- Seamless integration for new logic modules
- Collaboration-friendly environment

![Salience.py](/docs/SalienceVisualization.png)

## Installation

### Prerequisites
- Python 3.x
- Git

To install AgentForge, follow these steps:

1. Clone the GitHub repository:
    ```shell
    git clone https://github.com/DataBassGit/AgentForge.git
    ```

2. Install the required dependencies:
    ```shell
    pip install -e .
    ```

3. Navigate to `/tests/examples/.agentforge`, and use the .env.example to create a `.env` file containing your API keys.

## Usage

Modify the agent prompts in `/tests/examples/.agentforgedefault.json`. At the top of the file, you will edit the name, objective, and tasks.
Navigate to `/tests/examples/` in your console and run:

```shell
python salience_old.py
```

### Modes
- **Manual Mode**: You will be asked to continue before each round of execution.
- **Auto Mode**: The agent will automatically provide feedback after each execution.

## Contributing
Feel free to open issues or submit pull requests with improvements or bug fixes. For more details, check [CONTRIBUTING.md](./CONTRIBUTING.md).

## License
This project is licensed under the GNU General Public License. See `LICENSE` for more details.

## Contact
For more information or support, contact us at [support@example.com](mailto:support@example.com).

## FAQ
- **Q**: What do I do if I encounter a bug?
  - **A**: Open an issue with the bug details.
- **Q**: How can I contribute?
  - **A**: Check our [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.
