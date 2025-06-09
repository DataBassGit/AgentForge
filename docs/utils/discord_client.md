# Discord Integration Guide

## Overview

**AgentForge** offers a Discord integration that lets you run a bot in a separate thread and exchange messages with users in real time. This functionality resides in two modules within `agentforge/utils/discord`:

1. **`discord_client.py`**: Defines the main `DiscordClient` class, which manages the bot's connection, event handling, message queue, and slash commands.  
2. **`discord_utils.py`**: Contains helper methods in `DiscordUtils` for sending messages, embeds, direct messages, threads, and chunking large texts.

Together, these classes provide:

- A **separate thread** for the Discord bot so it doesn't block the main application.  
- An **asynchronous** event loop for receiving messages, slash commands, and updates.  
- **Utility methods** for chunking large messages, creating threads, sending embeds, and more.

---

## Prerequisites

1. **Discord Bot Token**: You must have a Discord bot token set as an environment variable named `DISCORD_TOKEN`.  
2. **Installation**: Ensure you have the `discord.py` (version 2.0 or higher) dependency installed.  

---

## Quick Start

Here's a minimal snippet showing how you might integrate the Discord client into an **AgentForge**-based application:

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
- **`set_typing_indicator(channel_id, is_typing)`** *(Async)*: Toggles the "typing..." indicator in a channel.  

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
This companion class handles lower-level tasks like chunking large messages, retrieving channels, or sending direct messages. It's used internally by `DiscordClient`, but you can also use it directly if needed.

### Notable Methods

- **`send_message(channel_id, content)`**  
  Splits the content into semantic chunks (via `semantic_chunk`) and sends each chunk to the specified channel.

- **`send_dm(user_id, content)`**  
  Fetches the user by ID and sends them a direct message.

- **`send_embed(channel_id, title, fields, color='blue', image_url=None)`**  
  Creates and sends a `discord.Embed` object, adding multiple fields.

- **`create_thread(channel_id, message_id, name, auto_archive_duration=1440, remove_author=True)`**  
  Creates a thread off of a message. If `remove_author=True`, removes the original message's author from the thread.

- **`reply_to_thread(thread_id, content)`**  
  Splits the content into chunks and sends them as messages inside a thread.

---

## Key Concepts

### Message Queue

The **message queue** is a pivotal part of how Discord messages flow into your agent logic. Each new user message is appended to `message_queue[channel_id]`. You pull them out by calling `process_channel_messages()` in your main loop, letting your application handle the data before acknowledging it or replying.

### Thread Safety and Async Calls

- The Discord bot runs in its own thread (started by `DiscordClient.run()`).  
- When you call methods like `send_message`, they schedule asynchronous tasks in the Discord client's loop using `asyncio.run_coroutine_threadsafe`. This approach ensures non-blocking, thread-safe interactions.

### Chunking Large Messages

Both `send_message` and `send_dm` use a `semantic_chunk` function to break up content into ~1900-character pieces. This prevents errors from Discord's 2000-character limit. If a chunk still ends up too big, it re-chunks it further.

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

**AgentForge**'s Discord integration provides a threaded client that can parse and queue incoming messages, respond, send DMs, embed messages, and manage threads. For developers building chat-oriented agents, it offers a straightforward path to real-time user interaction on Discord.

If you need more complex slash commands or event handling, you can expand the provided structure. By leveraging `DiscordClient` and `DiscordUtils`, your agents can seamlessly fit into Discord communities, respond to user queries, or even gather context for advanced LLM-driven tasks.

---

**Need Help?**

- **Email**: [contact@agentforge.net](mailto:contact@agentforge.net)  
- **Discord**: Join our [Discord Server](https://discord.gg/ttpXHUtCW6)

