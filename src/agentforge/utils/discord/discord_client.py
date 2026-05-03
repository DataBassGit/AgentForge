# utils/discord_client.py

import discord
from discord import app_commands
import os
import asyncio
import threading
from agentforge.utils.logger import Logger
from agentforge.tools.semantic_chunk import semantic_chunk
from agentforge.utils.discord.discord_utils import DiscordUtils


class DiscordClient:
    """
    A Discord client that handles bot functionality, message processing, and role management.
    """

    def __init__(self):
        """
        Initialize the DiscordClient with necessary attributes and event handlers.
        """
        self.discord_thread = None
        self.token = str(os.getenv('DISCORD_TOKEN'))
        self.intents = discord.Intents.default()
        self.intents.message_content = True

        # Dedicated loop for Voice WebSocket handling
        self.discord_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.discord_loop)

        # Native discord.py Client (Replaces Pycord's discord.Bot)
        self.client = discord.Client(intents=self.intents)
        self.tree = app_commands.CommandTree(self.client)

        self.logger = Logger('DiscordClient', 'DiscordClient')
        self.message_queue = {}
        self.running = False
        self.utils = DiscordUtils(self.client, self.logger)
        self.load_commands()

        @self.client.event
        async def on_ready():
            await self.tree.sync()  # Syncs slash commands natively
            self.logger.info(f'[DiscordClient.on_ready] {self.client.user} has connected to Discord!')

        @self.client.event
        async def on_message(message: discord.Message):
            self.logger.debug(f"[DiscordClient.on_message] Received message:\n{message}")

            content = message.content
            for mention in message.mentions:
                content = content.replace(f'<@{mention.id}>', f'@{mention.display_name}')

            message_data = {
                "channel": str(message.channel),
                "channel_id": message.channel.id,
                "message": content,
                "message_id": message.id,
                "author": message.author.display_name,
                "author_id": message.author,
                "timestamp": message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "mentions": message.mentions,
                "attachments": message.attachments
            }

            if isinstance(message.channel, discord.Thread):
                message_data["thread_id"] = message.channel.id
                message_data["thread_name"] = message.channel.name

            self.logger.debug(
                f"[DiscordClient.on_message] Channel: {str(message.channel)}({message.channel.id}) - {message.author.display_name} said:\n{content}")

            if message.author != self.client.user:
                if message.channel.id not in self.message_queue:
                    self.message_queue[message.channel.id] = []
                self.message_queue[message.channel.id].append(message_data)
                self.logger.debug("[DiscordClient.on_message] Message added to queue")
            else:
                self.logger.debug(f"[DiscordClient.on_message] Message not added to queue:\n{message_data}")

    def run(self):
        """Start the Discord client in a separate thread."""

        def run_discord():
            self.logger.info("[DiscordClient.run] Client Starting")
            asyncio.set_event_loop(self.discord_loop)
            self.discord_loop.run_until_complete(self.client.start(self.token))

        self.discord_thread = threading.Thread(target=run_discord, daemon=True)
        self.discord_thread.start()
        self.running = True

    def stop(self):
        """Stop the Discord client cleanly."""
        self.running = False
        asyncio.run_coroutine_threadsafe(self.client.close(), self.discord_loop).result()
        self.discord_thread.join(timeout=2)
        self.logger.info("[DiscordClient.stop] Client Stopped")

    def process_channel_messages(self):
        """Process and yield messages from the message queue."""
        if self.message_queue:
            try:
                next_message = self.message_queue.popitem()
                yield next_message
            except Exception as e:
                print(f"Exception: {e}")

    def send_message(self, channel_id, content, message_id=None):
        try:
            self.utils.send_message(channel_id, content, message_id)
            return True
        except:
            return False

    def send_dm(self, user_id, content):
        self.utils.send_dm(user_id, content)

    def send_embed(self, channel_id, title, fields, color='blue', image_url=None):
        self.utils.send_embed(channel_id, title, fields, color, image_url)

    def load_commands(self):
        """Load slash commands using standard discord.py syntax."""
        name = 'bot'
        description = 'send a command to the bot'
        function_name = 'bot'

        @self.tree.command(name=name, description=description)
        @app_commands.describe(command="send a command to the bot")
        async def command_callback(interaction: discord.Interaction, command: str):
            kwargs = {"arg": command}
            await self.handle_command(interaction, name, function_name, kwargs)

        self.logger.info(f"[DiscordClient.load_commands] Register Command: {name} - Function: {function_name}")

    async def handle_command(self, interaction: discord.Interaction, command_name: str, function_name: str,
                             kwargs: dict):
        message_data = {
            "channel": str(interaction.channel),
            "channel_id": interaction.channel_id,
            "message": f"/{command_name}",
            "author": interaction.user.display_name,
            "author_id": interaction.user,
            "timestamp": interaction.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "mentions": [],
            "function_name": function_name,
            "arg": kwargs.get('arg', None)
        }

        if interaction.channel_id not in self.message_queue:
            self.message_queue[interaction.channel_id] = []
        self.message_queue[interaction.channel_id].append(message_data)
        self.logger.info(f"[DiscordClient.handle_command] Command '{command_name}' received and added to the queue")

        await interaction.response.send_message(f"Command '{command_name}' received and added to the queue.")

    async def set_typing_indicator(self, channel_id, is_typing):
        channel = self.client.get_channel(channel_id)
        if channel:
            if is_typing:
                async with channel.typing():
                    await asyncio.sleep(5)
            else:
                await asyncio.sleep(0)
        else:
            self.logger.error(f"Channel with ID {channel_id} not found.")

    def create_thread(self, channel_id, message_id, name, auto_archive_duration=1440, remove_author=True):
        return self.utils.create_thread(channel_id, message_id, name, auto_archive_duration, remove_author)

    def reply_to_thread(self, thread_id, content):
        return self.utils.reply_to_thread(thread_id, content)

    def lock_thread(self, thread_id):
        """
        Lock a specific thread, making it read-only for normal users.
        """
        return self.utils.lock_thread(thread_id)


if __name__ == "__main__":
    import time

    client = DiscordClient()
    client.run()
    while True:
        try:
            for message_item in client.process_channel_messages():
                time.sleep(5)
                client.send_message(message_item[0], f"Processed: {message_item}")
        except KeyboardInterrupt:
            print("Stopping...")
            client.stop()
            break
        finally:
            time.sleep(5)