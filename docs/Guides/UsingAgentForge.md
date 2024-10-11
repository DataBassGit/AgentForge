# Using AgentForge

This guide will help you get started with running agents and multi-agent scripts using **AgentForge**.

---

## Running an Agent

### 1. Define an Agent Class

Create a Python file named `echo_agent.py` in your project root:

```python
from agentforge.agent import Agent

class EchoAgent(Agent):
    pass  # The agent name is automatically set to 'EchoAgent'
```

### 2. Create the Prompt Template (`EchoAgent.yaml`)

Inside the `.agentforge/prompts/` directory, create a **YAML** file named `EchoAgent.yaml`:

```yaml
Prompts:
  System: You are an assistant that echoes the user's input.
  User: {user_input}
```

> **Note**: This prompt template uses a variable placeholder `{user_input}`. This variable will be replaced with actual data at runtime. To understand how agent prompts are rendered within **AgentForge**, see the [Agent Prompts](../Agents/AgentPrompts.md) guide.

### 3. Write a Script to Run the Agent Interactively

Create a separate Python script (e.g., `run_agent.py`) in your project root to import and run your custom agent:

```python
from echo_agent import EchoAgent

def main():
    # Initialize the EchoAgent
    agent = EchoAgent()

    print("Welcome to the EchoAgent! Type 'quit' to exit.")
    while True:
        # Prompt the user for input
        user_input = input("You: ")

        # Exit the loop if the user types 'quit'
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break

        # Run the agent with the user's input and print the response
        response = agent.run(user_input=user_input)
        print("EchoAgent:", response)

if __name__ == "__main__":
    main()
```

### 4. Execute the Script

Ensure your virtual environment is activated and run the script:

```bash
python run_agent.py
```

### 5. **Example Interaction**

Assuming the agent is connected to an LLM, the interaction might look like:

```
Welcome to the EchoAgent! Type 'quit' to exit.
You: Hello, EchoAgent!
EchoAgent: Hello, EchoAgent!
You: How are you today?
EchoAgent: How are you today?
You: This is a test.
EchoAgent: This is a test.
You: quit
Goodbye!
```

### 6. Deactivate the Virtual Environment (Optional)

When you're done working, deactivate the virtual environment:

```shell
deactivate
```

Remember to activate the virtual environment (`source venv/bin/activate` or `venv\Scripts\activate`) whenever you return to work on your project.

---

## Running a Multi Agent Script

To create a script that uses multiple agents working together, we'll create two agents: `QuestionGeneratorAgent` and `AnswerAgent`.

### 1. Define the Agent Classes

#### `question_generator_agent.py`

Create a Python file named `question_generator_agent.py` in your project root:

```python
from agentforge.agent import Agent

class QuestionGeneratorAgent(Agent):
    pass  # The agent name is automatically set to 'QuestionGeneratorAgent'
```

#### `answer_agent.py`

Create another Python file named `answer_agent.py` in your project root:

```python
from agentforge.agent import Agent

class AnswerAgent(Agent):
    pass  # The agent name is automatically set to 'AnswerAgent'
```

### 2. Create the Prompt Templates

#### `QuestionGeneratorAgent.yaml`

Inside the `.agentforge/prompts/` directory, create a **YAML** file named `QuestionGeneratorAgent.yaml`:

```yaml
Prompts:
  System: You are a helpful assistant that generates insightful questions based on the user's topic.
  User: |
    Topic: {topic}
```

#### `AnswerAgent.yaml`

Also in the `.agentforge/prompts/` directory, create a **YAML** file named `AnswerAgent.yaml`:

```yaml
Prompts:
  System: You are a knowledgeable assistant that provides detailed answers to questions.
  User: |
    Question: {question}
```

### 3. Write a Script to Manage Agent Interactions

Create a Python script (e.g., `run_topic_qanda.py`) in your project root:

```python
from question_generator_agent import QuestionGeneratorAgent
from answer_agent import AnswerAgent

# Initialize agents
question_agent = QuestionGeneratorAgent()
answer_agent = AnswerAgent()

# Agent 1 generates a question based on a topic
topic = "artificial intelligence"
question = question_agent.run(topic=topic)
print(f"Generated Question: {question}")

# Agent 2 answers the question
answer = answer_agent.run(question=question)
print(f"Answer: {answer}")
```

### 4. Execute the Script

Ensure your virtual environment is activated and run the script:

```bash
python run_topic_qanda.py
```

### 5. **Example Output**

Assuming the agents are connected to an LLM, the output might be:

```
Generated Question: What are the ethical implications of artificial intelligence in modern society?
Answer: The ethical implications of artificial intelligence (AI) in modern society include concerns about privacy, job displacement due to automation, decision-making transparency, bias in AI algorithms, and the potential for AI to be used in harmful ways such as surveillance or autonomous weapons. Addressing these issues requires careful regulation, ethical guidelines, and ongoing public dialogue to ensure that AI technologies benefit society as a whole.
```

>*Note: The actual output will depend on the LLM used and its configuration.*

---

## Additional Resources

- **Custom Agents Guide**:
  - Learn how to create and customize agents in detail. [Custom Agents Guide](../Agents/CustomAgents.md)

- **Settings**:
  - Customize model settings in `.agentforge/settings/`.
  - Specify default LLMs, temperature, max tokens, and more.
  - Learn more in the [Settings Guide](../Settings/Settings.md).

- **Personas**:
  - Use personas to encapsulate information accessible to agents.
  - Store personas in `.agentforge/personas/`.
  - Learn more in the [Personas Guide](../Personas/Personas.md).
  
---

**Next Steps**:

- Explore the [Agents Documentation](../Agents/Agents.md) for more advanced agent configurations.
- Learn about integrating different LLM APIs in the [LLM API Integration Guide](../LLMs/LLMs.md).
