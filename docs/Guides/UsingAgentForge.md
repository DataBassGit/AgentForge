# Using AgentForge

## Introduction

This guide will help you get started with running agents, creating custom agents, and building cognitive architectures using **AgentForge**.

---

## Running an Agent

### 1. Define the Agent Class

Create a Python file named `echo_agent.py` in your project root:

```python
from agentforge import Agent

class EchoAgent(Agent):
    pass  # The agent_name is automatically set to 'EchoAgent'
```

### 2. Create the Prompt Template (`EchoAgent.yaml`)

Inside the `.agentforge/agents/` directory, create a **YAML** file named `EchoAgent.yaml`:

```yaml
Prompts:
  System: You are an assistant that echoes the user's input.
  User: {user_input}
```
> Note: This prompt template uses a variable placeholder `{user_input}`. This variable will be replaced with actual data at runtime. To understand how agent prompts are rendered within **AgentForge**, see the [Agent Prompts](../Agents/AgentPrompts.md) guide.

### 3. Write a Script to Run the Agent

Create a separate Python script (e.g., `run_agent.py`) in your project root to import and run your custom agent:

```python
from echo_agent import EchoAgent

# Initialize the agent
agent = EchoAgent()

# Run the agent with an input message
response = agent.run(user_input="Hello, AgentForge!")
print(response)
```

### 4. Execute the Script

Ensure your virtual environment is activated and run the script:

```bash
python run_agent.py
```

### 5. **Example Response**

Assuming the agent is connected to an LLM, the output might be:

```
Hello, AgentForge!
```

*Note: The actual response will depend on the LLM used and its configuration.*

---

## Running a Multi Agent Script

To create a script that uses multiple agents working together, we'll create two agents: `QuestionGeneratorAgent` and `AnswerAgent`.

### 1. Define the Agent Classes

#### `question_generator_agent.py`

Create a Python file named `question_generator_agent.py` in your project root:

```python
from agentforge import Agent

class QuestionGeneratorAgent(Agent):
    pass  # The agent_name is automatically set to 'QuestionGeneratorAgent'
```

#### `answer_agent.py`

Create another Python file named `answer_agent.py` in your project root:

```python
from agentforge import Agent

class AnswerAgent(Agent):
    pass  # The agent_name is automatically set to 'AnswerAgent'
```

### 2. Create the Prompt Templates

#### `QuestionGeneratorAgent.yaml`

Inside the `.agentforge/agents/` directory, create a **YAML** file named `QuestionGeneratorAgent.yaml`:

```yaml
Prompts:
  System: You are a helpful assistant that generates insightful questions based on the user's topic.
  User: |
    Topic: {topic}
```

#### `AnswerAgent.yaml`

Also in the `.agentforge/agents/` directory, create a **YAML** file named `AnswerAgent.yaml`:

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

*Note: The actual output will depend on the LLM used and its configuration.*

---

## Custom Agents

With **AgentForge**, you have the flexibility to create any number of custom agents tailored to your specific needs.

### Organizing Agents

- **Directory Structure**:

  - Agents are stored in the `.agentforge/agents/` directory.
  - You can organize agents in subdirectories as needed.

- **Agent Discovery**:

  - **AgentForge** automatically discovers agent **YAML** files within the `.agentforge/agents/` directory and its subdirectories.

---

## Additional Resources

- **Settings**:

  - Customize model settings in `.agentforge/settings/`.
  - Specify default LLMs, temperature, max tokens, and more.

- **Personas**:

  - Use personas to encapsulate information accessible to agents.
  - Store personas in `.agentforge/personas/`.

---

**Next Steps**:

- Explore the [Agents Documentation](../Agents/Agents.md) for more advanced agent configurations.
- Learn about integrating different LLM APIs in the [LLM API Integration Guide](../LLMs/LLMs.md).

