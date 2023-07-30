# AgentForge
AgentForge - is an advanced AI-driven task automation system designed for generating, prioritizing, and executing tasks based on a specified objective.
Utilizing state-of-the-art technologies such as ChromaDB, SentenceTransformer, and the OpenAI API for text generation, AgentForge aims to deliver efficient and reliable task management solutions.

The primary goal of this project is to establish a user-friendly, low-code/no-code framework that empowers users to rapidly iterate on cognitive architectures.
Simultaneously, the framework is designed to accommodate developers with a seamless integration process for incorporating new logic modules as the AI landscape continues to evolve.
By fostering a collaborative and accessible environment, AgentForge seeks to contribute to the advancement of AI research and development across various domains.

![Salience.py](/docs/SalienceVisualization.png)

## Installation
To install AgentForge, follow these steps:

Clone the GitHub repository:

```shell
git clone https://github.com/DataBassGit/AgentForge.git
```

Install the required dependencies:

```shell
pip install -e .
```

Navigate to `/tests/examples/.agentforge`, and copy the .env.example to create a .env file that contains your api keys.

## Usage

Modify the agent prompts in `/tests/examples/.agentforge/default.json`. At the top of the file you will edit the name, objective, and tasks.
This should be enough to start.

Navigate to `/tests/examples/` in your console and run

```shell
python salience_old.py
```

You will be asked if you would like to run in manual mode or auto mode. Choose manual mode for now.
Before each round of execution, you will be asked to continue.
The agent will automatically provide feedback after each execution.
This will add the feedback to the execution prompt.
You can also type whatever feedback you would like to provide to the bot manually.

## Contributing
Feel free to open issues or submit pull requests with improvements or bug fixes. Your contributions are welcome!

## License
This project is licensed under the GNU General Public License. See `LICENSE` for more details.
