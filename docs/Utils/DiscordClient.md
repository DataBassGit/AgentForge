# DiscordClient Utility Guide

## Introduction

The `DiscordClient` utility in **AgentForge** allows developers to integrate their agents or systems with Discord by connecting to a Discord bot. This utility provides methods to interact with Discord servers, channels, and users, enabling agents to send and receive messages, manage roles, and perform other Discord-related operations.

---

## Overview

By using the `DiscordClient`, you can:

- **Connect to Discord**: Establish a connection to Discord using your bot's token.
- **Send Messages**: Send messages to channels, threads, or directly to users (DMs).
- **Receive Messages**: Process incoming messages and react accordingly.
- **Manage Roles**: Add or remove roles for users within a guild (server).
- **Handle Threads**: Create and reply to threads within channels.
- **Send Embeds**: Send rich embed messages with formatted content and images.

**Note**: To use the `DiscordClient`, you need to set up your own Discord bot and obtain a bot token. Refer to [Discord's Developer Documentation](https://discord.com/developers/docs/intro) for instructions on how to create and configure a Discord bot.

---

## Setting Up

Before using the `DiscordClient`, ensure you have the following:

1. **Discord Bot Token**: Obtain this from the [Discord Developer Portal](https://discord.com/developers/applications).

2. **Environment Variable**: Set the `DISCORD_TOKEN` environment variable with your bot's token.

   ```bash
   export DISCORD_TOKEN='your-discord-bot-token-here'
   ```

3. **Discord Intents**: Configure the necessary intents for your bot, such as `message_content`, to allow the bot to read message content.

---

## Using the DiscordClient

### Initialization

Create an instance of the `DiscordClient`:

```python
from agentforge.utils.DiscordClient import DiscordClient

# Initialize the Discord client
discord_client = DiscordClient()
```

### Running the Client

Start the Discord client to begin listening for events and messages:

```python
discord_client.run()
```

This method runs the Discord client in a separate thread to avoid blocking your main application.

### Stopping the Client

To stop the Discord client:

```python
discord_client.stop()
```

---

## Key Methods

### 1. `run()`

**Purpose**: Starts the Discord client and begins processing events.

**Usage**:

```python
discord_client.run()
```

**Notes**:

- Runs the client in a separate thread.
- Must be called to start listening for messages and events.

---

### 2. `stop()`

**Purpose**: Stops the Discord client and cleans up resources.

**Usage**:

```python
discord_client.stop()
```

**Notes**:

- Stops the client and joins the thread.
- Should be called when you want to gracefully shut down the bot.

---

### 3. `send_message(channel_id, content)`

**Purpose**: Sends a message to a specified Discord channel.

**Parameters**:

- `channel_id` (int): The ID of the Discord channel to send the message to.
- `content` (str): The content of the message to send.

**Usage**:

```python
channel_id = 123456789012345678  # Replace with your channel ID
message = "Hello, Discord!"
discord_client.send_message(channel_id, message)
```

**Notes**:

- Supports sending long messages by chunking content appropriately.
- Messages are sent asynchronously in the Discord client's event loop.

---

### 4. `send_dm(user_id, content)`

**Purpose**: Sends a direct message (DM) to a specific Discord user.

**Parameters**:

- `user_id` (int): The ID of the Discord user to send the DM to.
- `content` (str): The content of the direct message.

**Usage**:

```python
user_id = 123456789012345678  # Replace with the user's ID
message = "Hello, this is a direct message!"
discord_client.send_dm(user_id, message)
```

**Notes**:

- Handles exceptions if the bot cannot send DMs to the user (e.g., due to privacy settings).
- Messages are sent asynchronously.

---

### 5. `process_channel_messages()`

**Purpose**: Retrieves and processes messages from the message queue.

**Usage**:

```python
for channel_id, messages in discord_client.process_channel_messages():
    for message_data in messages:
        author = message_data['author']
        content = message_data['message']
        print(f"{author} said: {content}")
```

**Notes**:

- Yields tuples containing `channel_id` and a list of `message_data` dictionaries.
- `message_data` includes details like `channel`, `message`, `author`, `timestamp`, etc.
- Use this method to process incoming messages in your application.

---

### 6. `send_embed(channel_id, title, fields, color='blue', image_url=None)`

**Purpose**: Sends an embed message to a specified Discord channel.

**Parameters**:

- `channel_id` (int): The ID of the channel to send the embed message to.
- `title` (str): The title of the embed message.
- `fields` (list of tuples): A list of `(name, value)` pairs for the embed fields.
- `color` (str, optional): The color of the embed (default is `'blue'`).
- `image_url` (str, optional): URL of an image to include in the embed.

**Usage**:

```python
fields = [
    ("Field 1", "Value 1"),
    ("Field 2", "Value 2")
]
discord_client.send_embed(
    channel_id=123456789012345678,
    title="Embed Title",
    fields=fields,
    color='green',
    image_url='https://example.com/image.png'
)
```

**Notes**:

- Colors can be `'blue'`, `'red'`, `'green'`, etc.
- Embeds allow for rich content with formatting and images.

---

### 7. `create_thread(channel_id, message_id, name, auto_archive_duration=1440, remove_author=True)`

**Purpose**: Creates a new thread in a specified channel attached to a message.

**Parameters**:

- `channel_id` (int): The ID of the channel where the thread will be created.
- `message_id` (int): The ID of the message to which the thread is attached.
- `name` (str): The name of the thread.
- `auto_archive_duration` (int, optional): Auto-archive duration in minutes (default is 1440 minutes or 24 hours).
- `remove_author` (bool, optional): Whether to remove the message author from the thread (default is `True`).

**Usage**:

```python
thread_id = discord_client.create_thread(
    channel_id=123456789012345678,
    message_id=987654321098765432,
    name="New Discussion Thread"
)
```

**Notes**:

- Returns the ID of the created thread.
- Useful for organizing conversations.

---

### 8. `reply_to_thread(thread_id, content)`

**Purpose**: Sends a reply to a specific thread.

**Parameters**:

- `thread_id` (int): The ID of the thread to reply to.
- `content` (str): The content of the reply message.

**Usage**:

```python
thread_id = 123456789012345678  # The thread ID obtained earlier
reply_message = "This is a reply to the thread."
discord_client.reply_to_thread(thread_id, reply_message)
```

**Notes**:

- Supports sending long messages by chunking content.
- Returns `True` if the reply was sent successfully.

---

### 9. `add_role(guild_id, user_id, role_name)`

**Purpose**: Adds a role to a user in a guild (server).

**Parameters**:

- `guild_id` (int): The ID of the guild.
- `user_id` (int): The ID of the user to whom the role will be added.
- `role_name` (str): The name of the role to add.

**Usage**:

```python
guild_id = 123456789012345678
user_id = 987654321098765432
role_name = "Member"
result = discord_client.add_role(guild_id, user_id, role_name)
print(result)
```

**Notes**:

- Returns a message indicating the result of the operation.
- The bot must have the necessary permissions to manage roles.

---

### 10. `remove_role(guild_id, user_id, role_name)`

**Purpose**: Removes a role from a user in a guild.

**Parameters**:

- `guild_id` (int): The ID of the guild.
- `user_id` (int): The ID of the user from whom the role will be removed.
- `role_name` (str): The name of the role to remove.

**Usage**:

```python
result = discord_client.remove_role(guild_id, user_id, role_name)
print(result)
```

**Notes**:

- Returns a message indicating the result of the operation.
- The bot must have the necessary permissions.

---

### 11. `has_role(guild_id, user_id, role_name)`

**Purpose**: Checks if a user has a specific role in a guild.

**Parameters**:

- `guild_id` (int): The ID of the guild.
- `user_id` (int): The ID of the user.
- `role_name` (str): The name of the role to check.

**Usage**:

```python
has_role = discord_client.has_role(guild_id, user_id, role_name)
print(f"User has role: {has_role}")
```

**Notes**:

- Returns `True` if the user has the role, `False` otherwise.

---

### 12. `list_roles(guild_id, user_id=None)`

**Purpose**: Lists all roles in a guild and optionally the roles of a specific user.

**Parameters**:

- `guild_id` (int): The ID of the guild.
- `user_id` (int, optional): The ID of the user to list roles for.

**Usage**:

```python
roles_info = discord_client.list_roles(guild_id, user_id)
print(roles_info)
```

**Notes**:

- Returns a formatted string listing the roles.
- Useful for debugging or displaying role information.

---

## Practical Application

### Integrating with an Agent

Here's how you might integrate the `DiscordClient` within an agent to send and receive messages:

```python
from agentforge.agent import Agent
from agentforge.utils.DiscordClient import DiscordClient

class DiscordAgent(Agent):
    def __init__(self):
        super().__init__()
        self.discord_client = DiscordClient()
        self.discord_client.run()

    def process_messages(self):
        for channel_id, messages in self.discord_client.process_channel_messages():
            for message_data in messages:
                content = message_data['message']
                author = message_data['author']
                # Process the message as needed
                response = self.generate_response(content)
                # Send a reply
                self.discord_client.send_message(channel_id, response)

    def generate_response(self, message):
        # Your logic to generate a response
        return f"Echo: {message}"

    def stop(self):
        self.discord_client.stop()

# Instantiate and use the agent
agent = DiscordAgent()
try:
    while True:
        agent.process_messages()
        # Add sleep or other logic as needed
except KeyboardInterrupt:
    agent.stop()
```

**Notes**:

- In this example, the agent listens for messages and echoes them back.
- Ensure you handle exceptions and implement proper shutdown procedures.

---

## Best Practices

- **Permissions**: Ensure your bot has the necessary permissions in your Discord server to perform actions like sending messages, managing roles, and creating threads.
- **Rate Limits**: Be mindful of Discord's rate limits to avoid being temporarily blocked. The `DiscordClient` handles some rate limiting, but you should design your application to respect these limits.
- **Error Handling**: Always check for exceptions, especially when interacting with Discord's API, as operations can fail due to permissions or network issues.
- **Secure Your Token**: Never expose your bot's token in source code or version control. Use environment variables or secure storage.
- **Bot Intents**: Configure the correct intents for your bot to receive the necessary events. For example, to read message content, enable the `MESSAGE CONTENT INTENT`.

---

## Conclusion

The `DiscordClient` utility in **AgentForge** provides a powerful interface for integrating your agents with Discord. By leveraging this utility, you can create interactive bots that communicate within Discord servers, enhancing user engagement and extending the capabilities of your agents.

Whether you're building a customer support bot, a game assistant, or any interactive application, the `DiscordClient` offers the tools needed to connect your systems to the vibrant Discord community.

---

**Need Help?**

If you have questions or need assistance, feel free to reach out:

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)

---
