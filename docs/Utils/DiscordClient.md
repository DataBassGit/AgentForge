# Discord Integration Guide

## Overview

**AgentForge** offers a Discord integration that lets you run a bot in a separate thread and exchange messages with users in real time. This functionality resides in two modules within `agentforge/utils/discord`:

1. **`discord_client.py`**: Defines the main `DiscordClient` class, which manages the bot's connection, event handling, message queue, and slash commands.  
2. **`discord_utils.py`**: Contains helper methods in `DiscordUtils` for sending messages, embeds, direct messages, threads, and chunking large texts.

Together, these classes provide:

- A **separate thread** for the Discord bot so it doesn’t block the main application.  
- An **asynchronous** event loop for receiving messages, slash commands, and updates.  
- **Utility methods** for chunking large messages, creating threads, sending embeds, and more.

---

## Prerequisites

1. **Discord Bot Token**: You must have a Discord bot token set as an environment variable named `DISCORD_TOKEN`.  
2. **Installation**: Ensure you have the `discord.py` (version 2.0 or higher) dependency installed.  

---

## Quick Start

Here’s a minimal snippet showing how you might integrate the Discord client into an **AgentForge**-based application:

```python
from agentforge.utils.discord.discord_client import DiscordClient
import time

# 1. Instantiate the client
client = DiscordClient()

# 2. Run the client in a separate thread
client.run()

# 3. Periodically process incoming messages
try:
    while True:
        for channel_id, messages in client.process_channel_messages():
            for message_data in messages:
                print(f"Received message from {message_data['author']}: {message_data['message']}")
                # Respond to the user
                client.send_message(channel_id, f"Hello, {message_data['author']}! You said: {message_data['message']}")
        time.sleep(3)
except KeyboardInterrupt:
    print("Shutting down Discord client...")
    # 4. Stop the client gracefully
    client.stop()
```

**Flow**:

1. **Create** a `DiscordClient` instance.  
2. **Run** it in a separate thread using `client.run()`.  
3. **Listen** for messages by calling `process_channel_messages()` periodically.  
4. **Reply** with methods like `send_message()` or `send_dm()`.  
5. **Stop** the client gracefully when your application ends.

---

## The `DiscordClient` Class

**File**: `agentforge/utils/discord/discord_client.py`  
This class is responsible for handling the lifecycle of the Discord bot:

```python
class DiscordClient:
    def __init__(self):
        self.token = str(os.getenv('DISCORD_TOKEN'))
        self.client = discord.Client(intents=...)        # main Discord client
        self.logger = Logger('DiscordClient', 'DiscordClient')
        self.tree = discord.app_commands.CommandTree(self.client)
        self.message_queue = {}
        self.running = False
        self.discord_thread = None
        self.utils = DiscordUtils(self.client, self.logger)

        # Register Discord events
        @self.client.event
        async def on_ready():
            await self.tree.sync()
            self.logger.info(f'{self.client.user} has connected to Discord!')

        @self.client.event
        async def on_message(message):
            # Convert mentions, build message_data, push to queue, etc.

        # Load slash commands
        self.load_commands()
```

### Key Attributes

- **`token`**: Read from the `DISCORD_TOKEN` environment variable.  
- **`client`**: A `discord.Client` instance with the appropriate intents (message content, etc.).  
- **`tree`**: For slash commands (`/commands`).  
- **`message_queue`**: A dictionary mapping `channel_id` -> list of message objects waiting to be processed.  
- **`utils`**: An instance of `DiscordUtils` providing helper functions (e.g., `send_message`, `send_embed`).

### Running and Stopping the Client

- **`run()`**  
  Starts the Discord client in a new thread to avoid blocking the main application.  
- **`stop()`**  
  Closes the Discord connection and waits for the thread to finish.

### Receiving Messages

- **`on_message` (Discord Event)**  
  Triggered whenever a user sends a message in a channel the bot can access.  
  The event handler transforms the Discord message into a dictionary (`message_data`) and appends it to `message_queue`.

- **`process_channel_messages()`**  
  A generator method that yields `(channel_id, [list_of_messages])` from the `message_queue`.  
  You can call this in your main application loop to fetch incoming messages and handle them.

### Sending Messages

- **`send_message(channel_id, content)`**: Sends a text message to the specified channel.  
- **`send_dm(user_id, content)`**: Sends a direct message to a user by their ID.  
- **`send_embed(channel_id, title, fields, color, image_url)`**: Sends an embed to a channel with optional fields and image.  
- **`set_typing_indicator(channel_id, is_typing)`** *(Async)*: Toggles the “typing...” indicator in a channel.  

### Threads and Slash Commands

- **Threads**  
  - **`create_thread(channel_id, message_id, name, auto_archive_duration=1440, remove_author=True)`**  
    Creates a new thread attached to a message.  
  - **`reply_to_thread(thread_id, content)`**  
    Sends a reply in a thread, chunking large messages if necessary.

- **Slash Commands**  
  - A single default slash command is defined: `@app_commands.command(name='bot', description='send a command to the bot')`.  
  - When invoked, a dictionary is added to `message_queue` with `function_name` and `arg`. You can expand this mechanism to build a more complex slash command system.

---

## The `DiscordUtils` Class

**File**: `agentforge/utils/discord/discord_utils.py`  
This companion class handles lower-level tasks like chunking large messages, retrieving channels, or sending direct messages. It’s used internally by `DiscordClient`, but you can also use it directly if needed.

### Notable Methods

- **`send_message(channel_id, content)`**  
  Splits the content into semantic chunks (via `semantic_chunk`) and sends each chunk to the specified channel.

- **`send_dm(user_id, content)`**  
  Fetches the user by ID and sends them a direct message.

- **`send_embed(channel_id, title, fields, color='blue', image_url=None)`**  
  Creates and sends a `discord.Embed` object, adding multiple fields.

- **`create_thread(channel_id, message_id, name, auto_archive_duration=1440, remove_author=True)`**  
  Creates a thread off of a message. If `remove_author=True`, removes the original message’s author from the thread.

- **`reply_to_thread(thread_id, content)`**  
  Splits the content into chunks and sends them as messages inside a thread.

---

## Key Concepts

### Message Queue

The **message queue** is a pivotal part of how Discord messages flow into your agent logic. Each new user message is appended to `message_queue[channel_id]`. You pull them out by calling `process_channel_messages()` in your main loop, letting your application handle the data before acknowledging it or replying.

### Thread Safety and Async Calls

- The Discord bot runs in its own thread (started by `DiscordClient.run()`).  
- When you call methods like `send_message`, they schedule asynchronous tasks in the Discord client’s loop using `asyncio.run_coroutine_threadsafe`. This approach ensures non-blocking, thread-safe interactions.

### Chunking Large Messages

Both `send_message` and `send_dm` use a `semantic_chunk` function to break up content into ~1900-character pieces. This prevents errors from Discord’s 2000-character limit. If a chunk still ends up too big, it re-chunks it further.

### Slash Commands

A basic slash command system is illustrated with the `/bot` command. Expanding this can involve adding more commands with:

```python
@discord.app_commands.command(name='something', description='Do something else')
async def command_callback(interaction: discord.Interaction, ...):
    ...
self.tree.add_command(command_callback)
```

---

## Best Practices

1. **Separate Thread**  
   Keep the Discord client isolated from your main logic, as shown in the example. This prevents the async loop from blocking.  
2. **Poll `process_channel_messages()`**  
   Decide on a frequency for polling so your agent can respond to users promptly but also not hog CPU cycles.  
3. **Handle Mentions and Slash Commands**  
   Consider how you want to parse mentions (the code does some mention rewriting) and slash commands.  
4. **Logging and Debugging**  
   The client logs all incoming messages. Look at `self.logger` output if you need to debug content or events.  
5. **Permissions**  
   Make sure your bot has the required permissions (send messages, manage threads, etc.) in your Discord server.  
6. **Privacy**  
   Understand that any message content your bot receives might contain private information—store, handle, and process it responsibly.

---

## Conclusion

**AgentForge**’s Discord integration provides a threaded client that can parse and queue incoming messages, respond, send DMs, embed messages, and manage threads. For developers building chat-oriented agents, it offers a straightforward path to real-time user interaction on Discord.

If you need more complex slash commands or event handling, you can expand the provided structure. By leveraging `DiscordClient` and `DiscordUtils`, your agents can seamlessly fit into Discord communities, respond to user queries, or even gather context for advanced LLM-driven tasks.

---

**Need Help?**

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)  
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)

[//]: # (# DiscordClient Utility Guide)

[//]: # ()
[//]: # (## Introduction)

[//]: # ()
[//]: # (The `DiscordClient` utility in **AgentForge** allows developers to integrate their agents or systems with Discord by connecting to a Discord bot. This utility provides methods to interact with Discord servers, channels, and users, enabling agents to send and receive messages, manage roles, and perform other Discord-related operations.)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (## Overview)

[//]: # ()
[//]: # (By using the `DiscordClient`, you can:)

[//]: # ()
[//]: # (- **Connect to Discord**: Establish a connection to Discord using your bot's token.)

[//]: # (- **Send Messages**: Send messages to channels, threads, or directly to users &#40;DMs&#41;.)

[//]: # (- **Receive Messages**: Process incoming messages and react accordingly.)

[//]: # (- **Manage Roles**: Add or remove roles for users within a guild &#40;server&#41;.)

[//]: # (- **Handle Threads**: Create and reply to threads within channels.)

[//]: # (- **Send Embeds**: Send rich embed messages with formatted content and images.)

[//]: # ()
[//]: # (**Note**: To use the `DiscordClient`, you need to set up your own Discord bot and obtain a bot token. Refer to [Discord's Developer Documentation]&#40;https://discord.com/developers/docs/intro&#41; for instructions on how to create and configure a Discord bot.)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (## Setting Up)

[//]: # ()
[//]: # (Before using the `DiscordClient`, ensure you have the following:)

[//]: # ()
[//]: # (1. **Discord Bot Token**: Obtain this from the [Discord Developer Portal]&#40;https://discord.com/developers/applications&#41;.)

[//]: # ()
[//]: # (2. **Environment Variable**: Set the `DISCORD_TOKEN` environment variable with your bot's token.)

[//]: # ()
[//]: # (   ```bash)

[//]: # (   export DISCORD_TOKEN='your-discord-bot-token-here')

[//]: # (   ```)

[//]: # ()
[//]: # (3. **Discord Intents**: Configure the necessary intents for your bot, such as `message_content`, to allow the bot to read message content.)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (## Using the DiscordClient)

[//]: # ()
[//]: # (### Initialization)

[//]: # ()
[//]: # (Create an instance of the `DiscordClient`:)

[//]: # ()
[//]: # (```python)

[//]: # (from agentforge.utils.DiscordClient import DiscordClient)

[//]: # ()
[//]: # (# Initialize the Discord client)

[//]: # (discord_client = DiscordClient&#40;&#41;)

[//]: # (```)

[//]: # ()
[//]: # (### Running the Client)

[//]: # ()
[//]: # (Start the Discord client to begin listening for events and messages:)

[//]: # ()
[//]: # (```python)

[//]: # (discord_client.run&#40;&#41;)

[//]: # (```)

[//]: # ()
[//]: # (This method runs the Discord client in a separate thread to avoid blocking your main application.)

[//]: # ()
[//]: # (### Stopping the Client)

[//]: # ()
[//]: # (To stop the Discord client:)

[//]: # ()
[//]: # (```python)

[//]: # (discord_client.stop&#40;&#41;)

[//]: # (```)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (## Key Methods)

[//]: # ()
[//]: # (### 1. `run&#40;&#41;`)

[//]: # ()
[//]: # (**Purpose**: Starts the Discord client and begins processing events.)

[//]: # ()
[//]: # (**Usage**:)

[//]: # ()
[//]: # (```python)

[//]: # (discord_client.run&#40;&#41;)

[//]: # (```)

[//]: # ()
[//]: # (**Notes**:)

[//]: # ()
[//]: # (- Runs the client in a separate thread.)

[//]: # (- Must be called to start listening for messages and events.)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (### 2. `stop&#40;&#41;`)

[//]: # ()
[//]: # (**Purpose**: Stops the Discord client and cleans up resources.)

[//]: # ()
[//]: # (**Usage**:)

[//]: # ()
[//]: # (```python)

[//]: # (discord_client.stop&#40;&#41;)

[//]: # (```)

[//]: # ()
[//]: # (**Notes**:)

[//]: # ()
[//]: # (- Stops the client and joins the thread.)

[//]: # (- Should be called when you want to gracefully shut down the bot.)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (### 3. `send_message&#40;channel_id, content&#41;`)

[//]: # ()
[//]: # (**Purpose**: Sends a message to a specified Discord channel.)

[//]: # ()
[//]: # (**Parameters**:)

[//]: # ()
[//]: # (- `channel_id` &#40;int&#41;: The ID of the Discord channel to send the message to.)

[//]: # (- `content` &#40;str&#41;: The content of the message to send.)

[//]: # ()
[//]: # (**Usage**:)

[//]: # ()
[//]: # (```python)

[//]: # (channel_id = 123456789012345678  # Replace with your channel ID)

[//]: # (message = "Hello, Discord!")

[//]: # (discord_client.send_message&#40;channel_id, message&#41;)

[//]: # (```)

[//]: # ()
[//]: # (**Notes**:)

[//]: # ()
[//]: # (- Supports sending long messages by chunking content appropriately.)

[//]: # (- Messages are sent asynchronously in the Discord client's event loop.)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (### 4. `send_dm&#40;user_id, content&#41;`)

[//]: # ()
[//]: # (**Purpose**: Sends a direct message &#40;DM&#41; to a specific Discord user.)

[//]: # ()
[//]: # (**Parameters**:)

[//]: # ()
[//]: # (- `user_id` &#40;int&#41;: The ID of the Discord user to send the DM to.)

[//]: # (- `content` &#40;str&#41;: The content of the direct message.)

[//]: # ()
[//]: # (**Usage**:)

[//]: # ()
[//]: # (```python)

[//]: # (user_id = 123456789012345678  # Replace with the user's ID)

[//]: # (message = "Hello, this is a direct message!")

[//]: # (discord_client.send_dm&#40;user_id, message&#41;)

[//]: # (```)

[//]: # ()
[//]: # (**Notes**:)

[//]: # ()
[//]: # (- Handles exceptions if the bot cannot send DMs to the user &#40;e.g., due to privacy settings&#41;.)

[//]: # (- Messages are sent asynchronously.)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (### 5. `process_channel_messages&#40;&#41;`)

[//]: # ()
[//]: # (**Purpose**: Retrieves and processes messages from the message queue.)

[//]: # ()
[//]: # (**Usage**:)

[//]: # ()
[//]: # (```python)

[//]: # (for channel_id, messages in discord_client.process_channel_messages&#40;&#41;:)

[//]: # (    for message_data in messages:)

[//]: # (        author = message_data['author'])

[//]: # (        content = message_data['message'])

[//]: # (        print&#40;f"{author} said: {content}"&#41;)

[//]: # (```)

[//]: # ()
[//]: # (**Notes**:)

[//]: # ()
[//]: # (- Yields tuples containing `channel_id` and a list of `message_data` dictionaries.)

[//]: # (- `message_data` includes details like `channel`, `message`, `author`, `timestamp`, etc.)

[//]: # (- Use this method to process incoming messages in your application.)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (### 6. `send_embed&#40;channel_id, title, fields, color='blue', image_url=None&#41;`)

[//]: # ()
[//]: # (**Purpose**: Sends an embed message to a specified Discord channel.)

[//]: # ()
[//]: # (**Parameters**:)

[//]: # ()
[//]: # (- `channel_id` &#40;int&#41;: The ID of the channel to send the embed message to.)

[//]: # (- `title` &#40;str&#41;: The title of the embed message.)

[//]: # (- `fields` &#40;list of tuples&#41;: A list of `&#40;name, value&#41;` pairs for the embed fields.)

[//]: # (- `color` &#40;str, optional&#41;: The color of the embed &#40;default is `'blue'`&#41;.)

[//]: # (- `image_url` &#40;str, optional&#41;: URL of an image to include in the embed.)

[//]: # ()
[//]: # (**Usage**:)

[//]: # ()
[//]: # (```python)

[//]: # (fields = [)

[//]: # (    &#40;"Field 1", "Value 1"&#41;,)

[//]: # (    &#40;"Field 2", "Value 2"&#41;)

[//]: # (])

[//]: # (discord_client.send_embed&#40;)

[//]: # (    channel_id=123456789012345678,)

[//]: # (    title="Embed Title",)

[//]: # (    fields=fields,)

[//]: # (    color='green',)

[//]: # (    image_url='https://example.com/image.png')

[//]: # (&#41;)

[//]: # (```)

[//]: # ()
[//]: # (**Notes**:)

[//]: # ()
[//]: # (- Colors can be `'blue'`, `'red'`, `'green'`, etc.)

[//]: # (- Embeds allow for rich content with formatting and images.)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (### 7. `create_thread&#40;channel_id, message_id, name, auto_archive_duration=1440, remove_author=True&#41;`)

[//]: # ()
[//]: # (**Purpose**: Creates a new thread in a specified channel attached to a message.)

[//]: # ()
[//]: # (**Parameters**:)

[//]: # ()
[//]: # (- `channel_id` &#40;int&#41;: The ID of the channel where the thread will be created.)

[//]: # (- `message_id` &#40;int&#41;: The ID of the message to which the thread is attached.)

[//]: # (- `name` &#40;str&#41;: The name of the thread.)

[//]: # (- `auto_archive_duration` &#40;int, optional&#41;: Auto-archive duration in minutes &#40;default is 1440 minutes or 24 hours&#41;.)

[//]: # (- `remove_author` &#40;bool, optional&#41;: Whether to remove the message author from the thread &#40;default is `True`&#41;.)

[//]: # ()
[//]: # (**Usage**:)

[//]: # ()
[//]: # (```python)

[//]: # (thread_id = discord_client.create_thread&#40;)

[//]: # (    channel_id=123456789012345678,)

[//]: # (    message_id=987654321098765432,)

[//]: # (    name="New Discussion Thread")

[//]: # (&#41;)

[//]: # (```)

[//]: # ()
[//]: # (**Notes**:)

[//]: # ()
[//]: # (- Returns the ID of the created thread.)

[//]: # (- Useful for organizing conversations.)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (### 8. `reply_to_thread&#40;thread_id, content&#41;`)

[//]: # ()
[//]: # (**Purpose**: Sends a reply to a specific thread.)

[//]: # ()
[//]: # (**Parameters**:)

[//]: # ()
[//]: # (- `thread_id` &#40;int&#41;: The ID of the thread to reply to.)

[//]: # (- `content` &#40;str&#41;: The content of the reply message.)

[//]: # ()
[//]: # (**Usage**:)

[//]: # ()
[//]: # (```python)

[//]: # (thread_id = 123456789012345678  # The thread ID obtained earlier)

[//]: # (reply_message = "This is a reply to the thread.")

[//]: # (discord_client.reply_to_thread&#40;thread_id, reply_message&#41;)

[//]: # (```)

[//]: # ()
[//]: # (**Notes**:)

[//]: # ()
[//]: # (- Supports sending long messages by chunking content.)

[//]: # (- Returns `True` if the reply was sent successfully.)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (### 9. `add_role&#40;guild_id, user_id, role_name&#41;`)

[//]: # ()
[//]: # (**Purpose**: Adds a role to a user in a guild &#40;server&#41;.)

[//]: # ()
[//]: # (**Parameters**:)

[//]: # ()
[//]: # (- `guild_id` &#40;int&#41;: The ID of the guild.)

[//]: # (- `user_id` &#40;int&#41;: The ID of the user to whom the role will be added.)

[//]: # (- `role_name` &#40;str&#41;: The name of the role to add.)

[//]: # ()
[//]: # (**Usage**:)

[//]: # ()
[//]: # (```python)

[//]: # (guild_id = 123456789012345678)

[//]: # (user_id = 987654321098765432)

[//]: # (role_name = "Member")

[//]: # (result = discord_client.add_role&#40;guild_id, user_id, role_name&#41;)

[//]: # (print&#40;result&#41;)

[//]: # (```)

[//]: # ()
[//]: # (**Notes**:)

[//]: # ()
[//]: # (- Returns a message indicating the result of the operation.)

[//]: # (- The bot must have the necessary permissions to manage roles.)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (### 10. `remove_role&#40;guild_id, user_id, role_name&#41;`)

[//]: # ()
[//]: # (**Purpose**: Removes a role from a user in a guild.)

[//]: # ()
[//]: # (**Parameters**:)

[//]: # ()
[//]: # (- `guild_id` &#40;int&#41;: The ID of the guild.)

[//]: # (- `user_id` &#40;int&#41;: The ID of the user from whom the role will be removed.)

[//]: # (- `role_name` &#40;str&#41;: The name of the role to remove.)

[//]: # ()
[//]: # (**Usage**:)

[//]: # ()
[//]: # (```python)

[//]: # (result = discord_client.remove_role&#40;guild_id, user_id, role_name&#41;)

[//]: # (print&#40;result&#41;)

[//]: # (```)

[//]: # ()
[//]: # (**Notes**:)

[//]: # ()
[//]: # (- Returns a message indicating the result of the operation.)

[//]: # (- The bot must have the necessary permissions.)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (### 11. `has_role&#40;guild_id, user_id, role_name&#41;`)

[//]: # ()
[//]: # (**Purpose**: Checks if a user has a specific role in a guild.)

[//]: # ()
[//]: # (**Parameters**:)

[//]: # ()
[//]: # (- `guild_id` &#40;int&#41;: The ID of the guild.)

[//]: # (- `user_id` &#40;int&#41;: The ID of the user.)

[//]: # (- `role_name` &#40;str&#41;: The name of the role to check.)

[//]: # ()
[//]: # (**Usage**:)

[//]: # ()
[//]: # (```python)

[//]: # (has_role = discord_client.has_role&#40;guild_id, user_id, role_name&#41;)

[//]: # (print&#40;f"User has role: {has_role}"&#41;)

[//]: # (```)

[//]: # ()
[//]: # (**Notes**:)

[//]: # ()
[//]: # (- Returns `True` if the user has the role, `False` otherwise.)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (### 12. `list_roles&#40;guild_id, user_id=None&#41;`)

[//]: # ()
[//]: # (**Purpose**: Lists all roles in a guild and optionally the roles of a specific user.)

[//]: # ()
[//]: # (**Parameters**:)

[//]: # ()
[//]: # (- `guild_id` &#40;int&#41;: The ID of the guild.)

[//]: # (- `user_id` &#40;int, optional&#41;: The ID of the user to list roles for.)

[//]: # ()
[//]: # (**Usage**:)

[//]: # ()
[//]: # (```python)

[//]: # (roles_info = discord_client.list_roles&#40;guild_id, user_id&#41;)

[//]: # (print&#40;roles_info&#41;)

[//]: # (```)

[//]: # ()
[//]: # (**Notes**:)

[//]: # ()
[//]: # (- Returns a formatted string listing the roles.)

[//]: # (- Useful for debugging or displaying role information.)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (## Practical Application)

[//]: # ()
[//]: # (### Integrating with an Agent)

[//]: # ()
[//]: # (Here's how you might integrate the `DiscordClient` within an agent to send and receive messages:)

[//]: # ()
[//]: # (```python)

[//]: # (from agentforge.agent import Agent)

[//]: # (from agentforge.utils.DiscordClient import DiscordClient)

[//]: # ()
[//]: # (class DiscordAgent&#40;Agent&#41;:)

[//]: # (    def __init__&#40;self&#41;:)

[//]: # (        super&#40;&#41;.__init__&#40;&#41;)

[//]: # (        self.discord_client = DiscordClient&#40;&#41;)

[//]: # (        self.discord_client.run&#40;&#41;)

[//]: # ()
[//]: # (    def process_messages&#40;self&#41;:)

[//]: # (        for channel_id, messages in self.discord_client.process_channel_messages&#40;&#41;:)

[//]: # (            for message_data in messages:)

[//]: # (                content = message_data['message'])

[//]: # (                author = message_data['author'])

[//]: # (                # Process the message as needed)

[//]: # (                response = self.generate_response&#40;content&#41;)

[//]: # (                # Send a reply)

[//]: # (                self.discord_client.send_message&#40;channel_id, response&#41;)

[//]: # ()
[//]: # (    def generate_response&#40;self, message&#41;:)

[//]: # (        # Your logic to generate a response)

[//]: # (        return f"Echo: {message}")

[//]: # ()
[//]: # (    def stop&#40;self&#41;:)

[//]: # (        self.discord_client.stop&#40;&#41;)

[//]: # ()
[//]: # (# Instantiate and use the agent)

[//]: # (agent = DiscordAgent&#40;&#41;)

[//]: # (try:)

[//]: # (    while True:)

[//]: # (        agent.process_messages&#40;&#41;)

[//]: # (        # Add sleep or other logic as needed)

[//]: # (except KeyboardInterrupt:)

[//]: # (    agent.stop&#40;&#41;)

[//]: # (```)

[//]: # ()
[//]: # (**Notes**:)

[//]: # ()
[//]: # (- In this example, the agent listens for messages and echoes them back.)

[//]: # (- Ensure you handle exceptions and implement proper shutdown procedures.)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (## Best Practices)

[//]: # ()
[//]: # (- **Permissions**: Ensure your bot has the necessary permissions in your Discord server to perform actions like sending messages, managing roles, and creating threads.)

[//]: # (- **Rate Limits**: Be mindful of Discord's rate limits to avoid being temporarily blocked. The `DiscordClient` handles some rate limiting, but you should design your application to respect these limits.)

[//]: # (- **Error Handling**: Always check for exceptions, especially when interacting with Discord's API, as operations can fail due to permissions or network issues.)

[//]: # (- **Secure Your Token**: Never expose your bot's token in source code or version control. Use environment variables or secure storage.)

[//]: # (- **Bot Intents**: Configure the correct intents for your bot to receive the necessary events. For example, to read message content, enable the `MESSAGE CONTENT INTENT`.)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (## Conclusion)

[//]: # ()
[//]: # (The `DiscordClient` utility in **AgentForge** provides a powerful interface for integrating your agents with Discord. By leveraging this utility, you can create interactive bots that communicate within Discord servers, enhancing user engagement and extending the capabilities of your agents.)

[//]: # ()
[//]: # (Whether you're building a customer support bot, a game assistant, or any interactive application, the `DiscordClient` offers the tools needed to connect your systems to the vibrant Discord community.)

[//]: # ()
[//]: # (---)

[//]: # ()
[//]: # (**Need Help?**)

[//]: # ()
[//]: # (If you have questions or need assistance, feel free to reach out:)

[//]: # ()
[//]: # (- **Email**: [contact@agentforge.net]&#40;mailto:contact@agentforge.net&#41;)

[//]: # (- **Discord**: Join our [Discord Server]&#40;https://discord.gg/ttpXHUtCW6&#41;)

[//]: # ()
[//]: # (---)
