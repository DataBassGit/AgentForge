# BigBoogaAGI
BigBoogaAGI is an advanced AI-driven task automation system designed for generating, prioritizing, and executing tasks based on a specified objective. Utilizing state-of-the-art technologies such as ChromaDB, SentenceTransformer, and the OpenAI API for text generation, BabyBoogaAGI aims to deliver efficient and reliable task management solutions.

The primary goal of this project is to establish a user-friendly, low-code/no-code framework that empowers users to rapidly iterate on cognitive architectures. Simultaneously, the framework is designed to accommodate developers with a seamless integration process for incorporating new logic modules as the AI landscape continues to evolve. By fostering a collaborative and accessible environment, BigBoogaAGI seeks to contribute to the advancement of AI research and development across various domains.

## Installation
1. Clone the repository:

```
git clone https://github.com/your_github_username/BigBoogaAGI.git
cd BigBoogaAGI
```

2. Install the required libraries:

```
pip install -r requirements.txt
```
3. Update the 'config.ini' file in the Config directory to indicate the DB, Language Model API, and evironment variables if you are using locally hosted API services.

4. Create a copy of '.env.example' in the Config folder named '.env' and add your API keys there.

5. Modify the 'default.json' file in the Personas directory with your objective and tasks. You can also adjust parameters and update the agent prompts here.


## Usage
1. Run the main.py script to start BigBoogaAGI:

```
python main.py
```
This script will initialize the AI system, generate tasks, prioritize them, and execute the tasks based on the given objective.

2. Select whether you want to use auto or manual mode. Automode will run continuously. This is dangerous if you are using a paid LLM API. If you select manual mode, you will be able to add additional context or instructions to the prompt sent ot the Execution Agent.

3. Monitor the output to see the tasks being generated and executed.

## Contributing
Feel free to open issues or submit pull requests with improvements or bug fixes. Your contributions are welcome!

## License
This project is licensed under the MIT License. See LICENSE for more details.
