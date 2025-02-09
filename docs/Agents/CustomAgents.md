# Advanced Custom Agents 

Welcome to the **Advanced Custom Agents** guide! This document showcases several examples of subclassing and extending the base `Agent` class for more complex or specialized use cases. If you need a refresher on how agents work, refer to the main [Agent](AgentClass.md) documentation.

---

## Overview

All the examples below assume you’ve already reviewed the basics of creating and configuring agents in **AgentForge**. Here, we focus on how to leverage subclassing to:

1. Incorporate **custom logic** that processes data before sending it to the LLM.  
2. Override result parsing or output building for specialized formatting or post-processing.  
3. Demonstrate **subclass inheritance**, so your agents can share logic but diverge in specialized tasks or prompts.

---

## 1. Summarizing Agent

This example demonstrates how to:

- Override `parse_result` to handle JSON responses from the LLM.
- Customize `build_output` to present a user-facing summary.

**Prompt File** (e.g., `.agentforge/prompts/SummarizeAgent.yaml`):

```yaml
prompts:
  system: "You are an assistant that summarizes text concisely."
  user: |
    Please provide a summary in JSON format with a 'summary' key:

    {text}
```

**Custom Agent Code** (`summarize_agent.py`):

```python
import json
from agentforge.agent import Agent

class SummarizeAgent(Agent):
    def parse_result(self):
        # Attempt to parse the LLM's response as JSON
        try:
            parsed = json.loads(self.result)
            self.template_data['parsed_result'] = parsed
        except json.JSONDecodeError:
            self.template_data['parsed_result'] = {'summary': self.result}

    def build_output(self):
        summary = self.template_data['parsed_result'].get('summary', 'No summary found.')
        self.output = f"Summary:\n{summary}"
```

**Usage**:

```python
if __name__ == "__main__":
    agent = SummarizeAgent()  # Agent subclasses will automatically select the YAML file with the same class name
    long_text = "AgentForge is a powerful framework..."
    result = agent.run(text=long_text)
    print(result)
```

You can point the **same** subclass to a different YAML file (e.g., `DetailedSummarizer.yaml`) simply by changing how you instantiate it:

```python
# Using a different agent name to load a different prompt
detailed_agent = SummarizeAgent("DetailedSummarizer")
detailed_response = detailed_agent.run(text=long_text)
```

---

## 2. Problem Solver

Here, the agent does multiple passes on the user’s data. We override `process_data` to illustrate how you might chain or transform data before rendering the final prompt.

**Prompt File** (e.g., `.agentforge/prompts/MultiStepAgent.yaml`):

```yaml
prompts:
  system: |
    You are a multi-step problem solver.
    Step 1: Analyze the question.
    Step 2: Provide a final answer.

  user: {formatted_question}
```

**Custom Agent Code** (`multi_step_agent.py`):

```python
from agentforge.agent import Agent

class MultiStepAgent(Agent):
    def process_data(self):
        """
        Perform multiple transformations or checks on the user input
        before rendering the prompt.
        """
        # Suppose we take the raw 'user_input' and split it into steps
        user_input = self.template_data.get('user_input', '').strip()
        
        # Example transformation: reformat the question
        formatted_question = f"Analyzed Question: {user_input}"
        
        # Store the reformatted text so it replaces {formatted_question} in the prompt
        self.template_data['formatted_question'] = formatted_question

    def parse_result(self):
        # (Optional) If we want to look for certain keywords, or split the output into multiple sections...
        # By default, do nothing.
        pass
```

**Usage**:

```python
if __name__ == "__main__":
    agent = MultiStepAgent()
    question = "How does AgentForge handle multi-step reasoning?"
    response = agent.run(user_input=question)
    print(response)
```

In this scenario, the agent manipulates the data in `process_data` before sending it to the LLM. You could expand this by chaining external APIs, running validations, or adding placeholders for sub-prompts.

---

## 3. Subclass Inheritance

This example illustrates how you can structure multiple levels of custom agents where each subclass builds on logic inherited from its parent.

**Base Agent** (`parent_agents.py`):

```python
from agentforge.agent import Agent

class BaseProcessorAgent(Agent):
    def process_data(self):
        # Basic text cleanup
        raw_input = self.template_data.get('user_input', '')
        self.template_data['cleaned_input'] = raw_input.strip()

        super().process_data()  # Call parent logic if needed

class FeedbackAgent(BaseProcessorAgent):
    def parse_result(self):
        # Check for certain keywords to see if feedback is needed
        if "ERROR" in self.result:
            self.template_data['feedback'] = "Review the error in your output."
        super().parse_result()

    def build_output(self):
        # Include feedback in the output if present
        if 'feedback' in self.template_data:
            self.output = f"{self.result}\n\nFeedback: {self.template_data['feedback']}"
        else:
            self.output = self.result
```

**Prompt File** for `FeedbackAgent` (e.g., `.agentforge/prompts/FeedbackAgent.yaml`):

```yaml
prompts:
  system: |
    You are a feedback-driven assistant. If the result contains errors, provide guidance.
  user: {cleaned_input}
```

**Usage**:

```python
if __name__ == "__main__":
    agent = FeedbackAgent()
    response = agent.run(user_input="Please generate some content with an intentional error.")
    print(response)
```

**Key Points**:

1. **`BaseProcessorAgent`** handles initial data cleanup (trimming whitespace).  
2. **`FeedbackAgent`** inherits that logic and adds extra steps in `parse_result` and `build_output`.  
3. You can keep extending this chain for more specialized agents, each layering on new behaviors.

---

## Final Thoughts

The examples above illustrate how subclassing the `Agent` class can give you:

- **Layered logic** through inheritance.  
- **Custom data processing** before prompt rendering (e.g., `process_data`).  
- **Specialized output building** or post-LLM parsing (`build_output`, `parse_result`).  
- **Prompt flexibility** by instantiating the same subclass with different agent names (pointing to different YAML files).

For details on overriding methods, configuring prompts, or managing personas, revisit the core [Agent](AgentClass.md) documentation and related guides.  

Enjoy building richer, more sophisticated agents with **AgentForge**!

---

**Need Help?**  
- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)  
- **Discord**: [Join our Discord Server](https://discord.gg/ttpXHUtCW6)