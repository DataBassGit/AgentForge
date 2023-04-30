# ETHOS
ETHOS - Evaluating Trustworthiness and Heuristic Objectives in Systems - is a groundbreaking project that addresses the critical issue of AI alignment. As AI continues to evolve and become increasingly sophisticated, it is becoming increasingly clear that alignment is one of the most significant challenges we face in developing this technology. Unaligned AI has the potential to cause catastrophic damage to society and humanity as a whole.

ETHOS is an API that provides a solution to this problem. It is designed to evaluate the trustworthiness and heuristic objectives of AI systems, from language models to autonomous agents and chatbots. The API allows for the real-time adjustment of responses, ensuring that AI systems remain aligned with the goals of humanity.

The need for AI alignment is becoming more urgent as AI systems become more prevalent in our daily lives. These systems are used in everything from social media algorithms to self-driving cars, and they have the potential to impact many different aspects of our lives. If these systems are not aligned with our values and goals, they could cause significant harm.

One of the most significant threats posed by unaligned AI is the potential for these systems to become adversarial. Adversarial AI is a form of AI that is intentionally designed to cause harm. This could take the form of cyberattacks, data breaches, or even physical harm to individuals or infrastructure. Adversarial AI could also be used to manipulate public opinion, disrupt democratic processes, or sow discord and chaos.

ETHOS provides a way to mitigate these risks by ensuring that AI systems are aligned with their intended purpose. By evaluating the trustworthiness of AI systems, ETHOS can detect when an AI system is deviating from its intended purpose and adjust its responses in real-time. This can prevent AI systems from becoming adversarial and ensure that they are working in the best interests of society.

## Installation
Refer to the HiAGI Installation Instructions below

## Usage
Run hi.py

```
python hi.py
```

This will start a server on the local machine allowing any bot to verify output against the heuristic imperative agents. These methods are called via API from a client endpoint. Refer to the API documentation in https://github.com/anselale/HiAGI-Dev/blob/main/About/APIDocumentation.md

We have provided with a version of BabyAGI which has been modified to send its outputs to the heuristic agents for verification and correction. The Modified BabyAGI repo can be found: LINK HERE

# HiAGI
HiAGI is an advanced AI-driven task automation system designed for generating, prioritizing, and executing tasks based on a specified objective. Utilizing state-of-the-art technologies such as ChromaDB, SentenceTransformer, and the OpenAI API for text generation, HiAGI aims to deliver efficient and reliable task management solutions.

The primary goal of this project is to establish a user-friendly, low-code/no-code framework that empowers users to rapidly iterate on cognitive architectures. Simultaneously, the framework is designed to accommodate developers with a seamless integration process for incorporating new logic modules as the AI landscape continues to evolve. By fostering a collaborative and accessible environment, HiAGI seeks to contribute to the advancement of AI research and development across various domains.

## Installation
1. Clone the repository:

```
git clone https://github.com/your_github_username/HiAGI.git
cd HiAGI
```

2. Install the required libraries:

```
pip install -r requirements.txt
```
3. Update the 'config.ini' file in the Config directory to indicate the DB, Language Model API, and evironment variables if you are using locally hosted API services.

4. Create a copy of '.env.example' in the Config folder named '.env' and add your API keys there.

5. Modify the 'default.json' file in the Personas directory with your objective and tasks. You can also adjust parameters and update the agent prompts here.

6. For web scraping, you will have installed Spacy, but you also need to install a model. By default, it uses the following model:

```
python -m spacy download en_core_web_sm 
```

## Usage
1. Run the main.py script to start HiAGI:

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