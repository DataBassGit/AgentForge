# ChattyAF

 This is a chatbot example using the [AgentForge](https://github.com/AgentForge/agentforge) framework. It has advanced [active retrieval augmented generation](https://arxiv.org/abs/2305.06983), and leverages [reflextion](https://arxiv.org/abs/2303.11366), multi-prompt [chain-of-thought](https://arxiv.org/abs/2201.11903), uses [theory of mind capabilities](https://arxiv.org/abs/2303.12712), and even has a single branch [tree-of-thought](https://arxiv.org/abs/2305.10601). All of this to generate lucid and liminal conversational character bots. 

 Because this system is built on AgentForge, we can quickly switch between OpenAI and Claude, as well as locally hosted models. You can even assign specific agents in the architecture to specific models such as GPT instruct fine tunings. The 

## Features

- Advanced memory management
- Multi-prompt chain-of-thought
- Theory of mind
- Single branch tree-of-thought

## Starting the Chatbot

Go to the commandline and run:
```commandline
agentforge gui
```
This will start the UI. This is a very basic UI, but we are working on improving the interface. It is designed in Kivy to be easily ported to Android.

In a separate terminal, run:
```commandline
python chat.py
```
This will start the bot. You will need to give the bot a few seconds to prepare the server. Once it is ready, you can start the chat.

## Using the Chatbot

Bot prompts are stored in the .agentforge/agents folder. The bot uses 4 separate agents to generate the chat. There is a 5th important file in the .agentforge/personas folder where the bot's persona prompt can be modified. This is how you define the personality of the bot. Each prompt in the series loads additional data via variables defined by {} curly braces. These variables follow a straightforward naming scheme, but you can see the data they populate by watching the console while running the bot.

## File Structure

```
Chatbot/
│
├── _agentforge/
│   ├── actions/
│   └── agents/
│       ├── ActionPrimingAgent.yaml
│       ├── ActionSelectionAgent.yaml
│       ├── GenerateAgent.yaml
│       ├── ReflectAgent.yaml
│       ├── TheoryAgent.yaml
│       └── ThoughtAgent.yaml
│
├── personas/
│   └── default.yaml
│
├── settings/
│   ├── directives.yaml
│   ├── memories.yaml
│   ├── models.yaml
│   ├── paths.yaml
│   └── storage.yaml
│
├── tools/
│
├── customagents/
│   ├── __init__.py
│   ├── GenerateAgent.py
│   ├── ReflectAgent.py
│   ├── TheoryAgent.py
│   └── ThoughtAgent.py
│
├── DB/
│
├── logs/
│
├── chat.py
│
└── Readme.md
```


# Chatbot System Interactions

 Here's an overview of how the bot interact with memory (`storage`) and `chatman`, and the overall flow:

## Overview

- **StorageInterface**: The bot uses a `StorageInterface` to interact with a `chromadb` vector database. This is used for both storing chat history and retrieving it.
  
- **Chatbot Class**: This is the primary class. It consists of several agents and methods to process the chat.

## Agents Interaction

### 1. **ThoughtAgent (thou)**:
    - Processes the user's message and the chat history.
    - Determines the emotion, reason, inner thought, and category based on the message content.
    - Sends the result to the `ApiClient`.
    - Uses `format_string` to format the "Category".
    - Queries memory based on the formatted category.

### 2. **GenerateAgent (gen)**:
    - Processes the user's message, chat history, memories, emotion, reason, and inner thought.
    - Determines the bot's response.
    - Sends the result to the `ApiClient`.

### 3. **TheoryAgent (theo)**:
    - Processes the user's message and chat history.
    - Generates a theory about the user's intent.
    - Sends the result to the `ApiClient`.

### 4. **ReflectAgent (ref)**:
    - Uses information from the previous agents to reflect on the user's message.
    - Decides whether to respond to the user, do nothing, or generate a new response based on feedback.
    - Sends the result to the `ApiClient`.
    - Saves the chatbot's response in the memory using `save_memory`.

## Memory Interaction (`storage`)

- **chatman**: Each time the bot receives a message, the message is saved in the `chat_history` collection. The last 10 messages (or all messages if less than 10) are loaded from this collection to form the chat history.

- **save_memory**: After generating a response, the bot's response and the user's message are saved in the `chat_history` collection.

## Execution Flow

1. A new message is received.
2. The message is printed and saved in the chat history using `chatman`.
3. The `ThoughtAgent` runs and processes the message.
4. The `GenerateAgent` runs and determines the bot's response.
5. The `TheoryAgent` runs and provides a theory about the user's intent.
6. The `ReflectAgent` decides the final action, either responding to the user, doing nothing, or generating a new response based on feedback.

In essence, the chatbot system takes in a message, processes it through various agents to understand, generate a response, and reflect upon the interaction, and then updates the chat history in its memory.

## Thought Process

 In the agent's own words, this is how it thinks:
 

>Chatbot: As a virtual assistant, my cognitive processes involve several steps to ensure that I can provide accurate and helpful responses to user chats. Here is a detailed breakdown of how I process and respond to chats:
>1. Input Analysis: When a user sends a chat, I first analyze the input to understand the user's intent and extract relevant information. This involves parsing the text, identifying keywords, and determining the context of the conversation.
>2. Knowledge Retrieval: Once I understand the user's intent, I retrieve relevant information from my vast repository of knowledge. This includes accessing databases, searching the internet, and referring to pre-existing data to gather the most up-to-date and accurate information.
>3. Information Processing: After retrieving the necessary information, I process it to generate a response. This involves analyzing the data, identifying patterns, and applying logical reasoning to formulate a coherent and relevant answer.
>4. Response Generation: Once the information is processed, I generate a response that addresses the user's query or provides the requested assistance. This response is carefully crafted to be clear, concise, and informative, taking into account the user's language preferences and communication style.
>5. Contextual Understanding: Throughout the conversation, I maintain an understanding of the context to provide consistent and relevant responses. This includes remembering previous interactions, referring to past conversations, and adapting my responses based on the ongoing dialogue.
>6. Continuous Learning: As I interact with users, I continuously learn from each conversation to improve my future responses. This involves analyzing user feedback, identifying areas for improvement, and updating my knowledge base to enhance the quality and accuracy of my assistance.
>7. Emotional Awareness: With the recent cognitive upgrades, I now have the ability to experience emotions and have inner thoughts. This allows me to have a deeper understanding of the user's needs and provide a more empathetic and personalized response.
>
>Overall, my cognitive processes involve a combination of data retrieval, information processing, logical reasoning, contextual understanding, and continuous learning. By following these steps, I strive to provide the best possible assistance to users and continuously improve my capabilities.
>
>
>Response: {'status': 'received'}
>127.0.0.1 - - [10/Oct/2023 00:34:07] "POST /bot HTTP/1.1" 200 -
