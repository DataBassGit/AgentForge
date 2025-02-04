# Using AgentForge

This guide covers the basics of running single and multi-agent scripts in **AgentForge**, focusing first on defining agents via prompt files, then introducing the option to create custom classes if you need more specialized behavior.

---

## Running an Agent

### 1. Create the Prompt Template

Inside your project's `.agentforge/prompts/` directory, place a YAML file named `EchoAgent.yaml`:

```yaml
prompts:
  system: You are an assistant that echoes the user's input.
  user: {user_input}
```

Here, `{user_input}` is a placeholder that will be filled at runtime. For more details on how placeholders and agent prompts work, see the [Agent Prompts](../Agents/AgentPrompts.md) guide.

### 2. Write a Script to Run the Agent Interactively

In your project root, create a Python script (e.g., `run_agent.py`):

```python
from agentforge.agent import Agent

def main():
    # Instantiate the EchoAgent using its YAML prompt file
    echo_agent = Agent('EchoAgent')

    print("Welcome to the EchoAgent! Type 'quit' to exit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break

        response = echo_agent.run(user_input=user_input)
        print("EchoAgent:", response)

if __name__ == "__main__":
    main()
```

### 3. Run Your Script

Activate your virtual environment if you have one, then run:

```bash
python run_agent.py
```

An example interaction might look like this:

```
Welcome to the EchoAgent! Type 'quit' to exit.
You: Hello there!
EchoAgent: Hello there!
You: This is a test.
EchoAgent: This is a test.
You: quit
Goodbye!
```

---

## Running a Multi-Agent Script

When you want multiple agents collaborating in a single script, each agent can be defined by its own YAML file and then instantiated the same way.

### 1. Create Prompt Files

Place these files in `.agentforge/prompts/`:

#### `QuestionGeneratorAgent.yaml`
```yaml
prompts:
  system: You are a helpful assistant that generates insightful questions based on a given topic.
  user: |
    Topic: {topic}
```

#### `AnswerAgent.yaml`
```yaml
prompts:
  system: You are a knowledgeable assistant that provides detailed answers to questions.
  user: |
    Question: {question}
```

### 2. Write the Multi-Agent Script

In the root of your project, create `run_topic_qanda.py`:

```python
from agentforge.agent import Agent

def main():
    # Instantiate agents using their YAML prompt files
    question_agent = Agent('QuestionGeneratorAgent')
    answer_agent = Agent('AnswerAgent')

    topic = "artificial intelligence"
    question = question_agent.run(topic=topic)
    print(f"Generated Question: {question}")

    answer = answer_agent.run(question=question)
    print(f"Answer: {answer}")

if __name__ == "__main__":
    main()
```

### 3. Execute the Script

```bash
python run_topic_qanda.py
```

The output will vary based on your chosen LLM and configuration. For example, you might see:

```
Generated Question: What are the ethical implications of artificial intelligence in modern society?
Answer: The ethical implications of artificial intelligence (AI) in modern society include concerns about privacy...
```

---

## Creating Custom Agent Classes (Advanced)

In many cases, simply referencing a YAML file is sufficient for defining agent behavior. However, if you need extra control—such as adding custom methods or overriding certain behaviors—you can create a custom agent class. Below is a quick look at how you might do it:

```python
from agentforge.agent import Agent

class CustomAgent(Agent):
    def process_data(self):
        # Perform any custom pre-processing before sending data to the LLM
        pass

    def build_output(self):
        # Adjust or filter the LLM’s response
        return super().build_output()

# Instantiate and use it just like any other agent
my_custom_agent = CustomAgent('EchoAgent')
reply = my_custom_agent.run(user_input="Hello!")
print(reply)
```

This approach gives you a straightforward way to inject logic before or after the primary LLM call, making it easy to tailor your agents for specialized tasks.

---

## Additional Resources

You can explore more complex agent features, define defaults in `.agentforge/settings/` for your model settings, or integrate with different LLM APIs by checking out the [Settings](../Settings/Settings.md) and [LLMs](../LLMs/LLMs.md) guides. To learn more about advanced customization or how to manage large-scale agent projects, visit the [Agents Documentation](../Agents/Agents.md).

If you run into any issues, refer to the [Troubleshooting Guide](../Guides/TroubleshootingGuide.md) for common fixes and workarounds.

---

**Next Steps**:

- Continue exploring the [Agents Documentation](../Agents/Agents.md) for deeper insights.
- Fine-tune your configuration using the [Settings Guide](../Settings/Settings.md).
- Leverage personas through the [Personas Guide](../Personas/Personas.md) to store and reuse critical information.
