# utils/discord_client.py

import discord
import os
import asyncio
import threading
from agentforge.utils.logger import Logger
from agentforge.tools.semantic_chunk import semantic_chunk
from agentforge.utils.discord.discord_utils import DiscordUtils



class DiscordClient:
    """
    A Discord client that handles bot functionality, message processing, and role management.

    This class uses a combination of asyncio and threading to manage Discord operations:
    - The Discord client runs in a separate thread to avoid blocking the main application.
    - Asynchronous methods are used for Discord API calls, which are then run in the client's event loop.
    - Thread-safe methods are provided for external code to interact with the Discord client.

    Attributes:
        token (str): The Discord bot token.
        intents (discord.Intents): The intents for the Discord client.
        client (discord.Client): The main Discord client instance.
        logger (Logger): A custom logger for the Discord client.
        tree (discord.app_commands.CommandTree): The command tree for slash commands.
        message_queue (dict): A queue to store incoming messages, keyed by channel ID.
        running (bool): A flag indicating whether the client is running.
        discord_thread (threading.Thread): The thread running the Discord client.
    """

    def __init__(self):
        """
        Initialize the DiscordClient with necessary attributes and event handlers.
        """
        self.discord_thread = None
        self.token = str(os.getenv('DISCORD_TOKEN'))
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.client = discord.Client(intents=self.intents)
        self.logger = Logger('DiscordClient', 'DiscordClient')
        self.tree = discord.app_commands.CommandTree(self.client)
        self.message_queue = {}
        self.running = False
        self.load_commands()
        self.utils = DiscordUtils(self.client, self.logger)


        @self.client.event
        async def on_ready():
            await self.tree.sync()
            self.logger.info(f'[DiscordClient.on_ready] {self.client.user} has connected to Discord!')

        @self.client.event
        async def on_message(message: discord.Message):
            self.logger.debug(f"[DiscordClient.on_message] Received message:\n{message}")

            content = message.content
            for mention in message.mentions:
                # If a mention is copy/pasted, this does not work. The mention value will come through as Null.
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

            # Add thread information to message_data if the message is in a thread
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
        """
        Start the Discord client in a separate thread.

        This method creates a new thread that runs the Discord client's event loop.
        The thread allows the Discord client to operate independently of the main
        application thread, preventing it from blocking other operations.
        """

        def run_discord():
            self.logger.info("[DiscordClient.run] Client Starting")
            asyncio.run(self.client.start(self.token))

        self.discord_thread = threading.Thread(target=run_discord)
        self.discord_thread.start()
        self.running = True

    def stop(self):
        """
        Stop the Discord client and join the client thread.

        This method closes the Discord client's connection and waits for the
        client thread to finish, ensuring a clean shutdown.
        """
        self.running = False
        asyncio.run(self.client.close())
        self.discord_thread.join()
        self.logger.info("[DiscordClient.stop] Client Stopped")

    def process_channel_messages(self):
        """
        Process and yield messages from the message queue.

        This function retrieves all messages sent to a discord channel from the
        message_queue and yields them.
        Each message is represented as a tuple with the following structure:

        (channel_id, [message_data])

        where:
        - channel_id (int): The ID of the Discord channel where the message was sent.
        - message_data (list): A list containing a single dictionary with message details:
            {
                'channel': str,       # The name of the channel (e.g., 'system')
                'channel_id': int,    # The ID of the channel (same as the tuple's first element)
                'message': str,       # The content of the message
                'author': str,        # The display name of the message author
                'author_id': Member,  # The Discord Member object of the author
                'timestamp': str      # The timestamp of the message in 'YYYY-MM-DD HH:MM:SS' format
                'mentions': list      # A list of Discord Member objects mentioned in the message
            }

        Yields:
        tuple: A message tuple as described above.

        Note:
        - This function is designed to work with Discord message objects.
        - If the message queue is empty, the function will print "No Message Found" and pass.
        - Any exceptions during message processing will be caught and printed.
        """
        if self.message_queue:
            try:
                next_message = self.message_queue.popitem()
                yield next_message
            except Exception as e:
                print(f"Exception: {e}")
        else:
            pass

    def send_message(self, channel_id, content):
        """
        Send a message to a specified Discord channel.
        
        Args:
            channel_id (int): The ID of the channel to send the message to.
            content (str): The content of the message to send.
        """
        self.utils.send_message(channel_id, content)

    def send_dm(self, user_id, content):
        """
        Send a direct message to a specified Discord user.
        
        Args:
            user_id (int): The ID of the user to send the direct message to.
            content (str): The content of the direct message to send.
        """
        self.utils.send_dm(user_id, content)
        
    def send_embed(self, channel_id, title, fields, color='blue', image_url=None):
        """
        Send an embed message to a specified Discord channel.

        Args:
            channel_id (int): The ID of the channel to send the embed message to.
            title (str): The title of the embed message.
            fields (list): A list of tuples representing the fields of the embed message.
            color (str, optional): The color of the embed message. Defaults to 'blue'.
            image_url (str, optional): The URL of the image to include in the embed message.
        """
        self.utils.send_embed(channel_id, title, fields, color, image_url)

    def load_commands(self):
        """
        Load slash commands for the Discord client.

        This method registers a single slash command ("bot") for the Discord client.
        The command is added to the command tree and will be available for users to
        interact with in Discord.
        """
        name = 'bot'
        description = 'send a command to the bot'
        function_name = 'bot'

        @discord.app_commands.command(name=name, description=description)
        async def command_callback(interaction: discord.Interaction, command: str):
            kwargs = {"arg": command}
            await self.handle_command(interaction, name, function_name, kwargs)

        param_name = "command"
        param_description = "send a command to the bot"
        command_callback = discord.app_commands.describe(**{param_name: param_description})(command_callback)

        self.logger.info(f"[DiscordClient.load_commands] Register Command: {name} - Function: {function_name}")
        self.tree.add_command(command_callback)

    async def handle_command(self, interaction: discord.Interaction, command_name: str, function_name: str,
                             kwargs: dict):
        """
        Handle a slash command interaction.

        This method is called asynchronously by the Discord client when a slash
        command is invoked. It adds the command to the message queue for processing.

        Args:
            interaction (discord.Interaction): The interaction object for the command.
            command_name (str): The name of the command.
            function_name (str): The name of the function to handle the command.
            kwargs (dict): Additional arguments for the command.
        """
        message_data = {
            "channel": str(interaction.channel),
            "channel_id": interaction.channel_id,
            "message": f"/{command_name}",
            "author": interaction.user.display_name,
            "author_id": interaction.user,
            "timestamp": interaction.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "mentions": interaction.data.get("resolved", {}).get("members", []),
            "function_name": function_name,
            "arg": kwargs.get('arg', None)
        }

        if interaction.channel_id not in self.message_queue:
            self.message_queue[interaction.channel_id] = []
        self.message_queue[interaction.channel_id].append(message_data)
        self.logger.info(f"[DiscordClient.handle_command] Command '{command_name}' received and added to the queue")

        await interaction.response.send_message(f"Command '{command_name}' received and added to the queue.")

    async def set_typing_indicator(self, channel_id, is_typing):
        """
        Set the typing indicator for a specified Discord channel.

        This method uses asyncio.run_coroutine_threadsafe to safely schedule the
        asynchronous typing indicator operation in the Discord client's event loop,
        allowing it to be called from any thread.

        Args:
            channel_id (int): The ID of the channel to set the typing indicator for.
            is_typing (bool): Whether to start or stop the typing indicator.
        """
        channel = self.client.get_channel(channel_id)

        if channel:
            if is_typing:
                async with channel.typing():
                    # Keep the typing indicator on for a specific duration
                    await asyncio.sleep(5)  # Adjust the duration as needed
            else:
                # Stop the typing indicator immediately
                await asyncio.sleep(0)
        else:
            self.logger.error(f"Channel with ID {channel_id} not found.")

    def create_thread(self, channel_id, message_id, name, auto_archive_duration=1440, remove_author=True):
        """
        Create a new thread in a specified channel, attached to a specific message.

        Args:
            channel_id (int): The ID of the channel to create the thread in.
            message_id (int): The ID of the message to attach the thread to.
            name (str): The name of the new thread.
            auto_archive_duration (int, optional): Duration in minutes after which the thread
                                               will automatically archive. Default is 1440 (24 hours).
            remove_author (bool, optional): Whether to remove the message author from the thread. Default is True.

        Returns:
            int: The ID of the created thread, or None if creation failed.
        """
        return self.utils.create_thread(channel_id, message_id, name, auto_archive_duration, remove_author)

    def reply_to_thread(self, thread_id, content):
        """
        Reply to a specific thread.

        Args:
            thread_id (int): The ID of the thread to reply to.
            content (str): The content of the reply message.

        Returns:
            bool: True if the reply was sent successfully, False otherwise.
        """
        return self.utils.reply_to_thread(thread_id, content)


if __name__ == "__main__":
    # This is just for testing the DiscordClient
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
        finally:
            time.sleep(5)
