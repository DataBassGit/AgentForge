# utils/DiscordClient.py

import discord
import os
import asyncio
import threading
from agentforge.utils.Logger import Logger
from agentforge.tools.SemanticChunk import semantic_chunk

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
        self.token = str(os.getenv('DISCORD_TOKEN'))
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.client = discord.Client(intents=self.intents)
        self.logger = Logger('DiscordClient')
        self.tree = discord.app_commands.CommandTree(self.client)
        self.message_queue = {}
        self.running = False
        self.load_commands()

        @self.client.event
        async def on_ready():
            await self.tree.sync()
            print("Client Ready")
            self.logger.log(f'{self.client.user} has connected to Discord!', 'info', 'DiscordClient')

        @self.client.event
        async def on_message(message: discord.Message):
            self.logger.log(f"On Message: {message}", 'debug', 'DiscordClient')

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
                "mentions": message.mentions
            }

            # Add thread information to message_data if the message is in a thread
            if isinstance(message.channel, discord.Thread):
                message_data["thread_id"] = message.channel.id
                message_data["thread_name"] = message.channel.name

            self.logger.log(f"{message.author.display_name} said: {content} in {str(message.channel)}. Channel ID: {message.channel.id}", 'info', 'DiscordClient')
            # print(f"{author_name} said: {content} in {channel}. Channel ID: {channel_id}")
            # print(f"Mentions: {formatted_mentions}")

            if message.author != self.client.user:
                if message.channel.id not in self.message_queue:
                    self.message_queue[message.channel.id] = []
                self.message_queue[message.channel.id].append(message_data)
                self.logger.log("Message added to queue", 'debug', 'DiscordClient')
            else:
                self.logger.log(f"Message not added to queue: {message_data}", 'debug', 'DiscordClient')

    def run(self):
        """
        Start the Discord client in a separate thread.

        This method creates a new thread that runs the Discord client's event loop.
        The thread allows the Discord client to operate independently of the main
        application thread, preventing it from blocking other operations.
        """
        def run_discord():
            print("Client Starting")
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

        This method uses asyncio.run_coroutine_threadsafe to safely schedule the
        asynchronous send operation in the Discord client's event loop, allowing
        it to be called from any thread.

        Args:
            channel_id (int): The ID of the channel to send the message to.
            content (str): The content of the message to send.
        """
        async def send():
            messages = semantic_chunk(content, min_length=200, max_length=1900)
            channel = self.client.get_channel(channel_id)
            if channel:
                for msg in messages:
                    if len(msg.content) > 2000:
                        # Re-chunk the oversized message
                        sub_messages = semantic_chunk(msg.content, min_length=200, max_length=1900)
                        for sub_msg in sub_messages:
                            await channel.send(sub_msg.content)
                    else:
                        await channel.send(msg.content)
            else:
                self.logger.log(f"Channel {channel_id} not found", 'error', 'DiscordClient')

        asyncio.run_coroutine_threadsafe(send(), self.client.loop)

    def send_dm(self, user_id, content):
        """
        Send a direct message to a specified Discord user.

        This method uses asyncio.run_coroutine_threadsafe to safely schedule the
        asynchronous send operation in the Discord client's event loop, allowing
        it to be called from any thread.

        Args:
            user_id (int): The ID of the user to send the direct message to.
            content (str): The content of the direct message to send.
        """
        async def send_dm_async():
            try:
                user = await self.client.fetch_user(user_id)
                if user:
                    messages = semantic_chunk(content, min_length=200, max_length=1900)
                    for msg in messages:
                        if len(msg.content) > 2000:
                            # Re-chunk the oversized message
                            sub_messages = semantic_chunk(msg.content, min_length=200, max_length=1900)
                            for sub_msg in sub_messages:
                                await user.send(sub_msg.content)
                        else:
                            await user.send(msg.content)
                else:
                    self.logger.log(f"User {user_id} not found", 'error', 'DiscordClient')
            except discord.errors.NotFound:
                self.logger.log(f"User {user_id} not found", 'error', 'DiscordClient')
            except discord.errors.Forbidden:
                self.logger.log(f"Cannot send DM to user {user_id}. Forbidden.", 'error', 'DiscordClient')
            except Exception as e:
                self.logger.log(f"Error sending DM to user {user_id}: {str(e)}", 'error', 'DiscordClient')

        asyncio.run_coroutine_threadsafe(send_dm_async(), self.client.loop)

    def send_embed(self, channel_id, title, fields, color='blue', image_url=None):
        """
        Send an embed message to a specified Discord channel.

        This method uses asyncio.run_coroutine_threadsafe to safely schedule the
        asynchronous send operation in the Discord client's event loop, allowing
        it to be called from any thread.

        Args:
            channel_id (int): The ID of the channel to send the embed message to.
            title (str): The title of the embed message.
            fields (list): A list of tuples representing the fields of the embed message.
            color (str, optional): The color of the embed message. Defaults to 'blue'.
            image_url (str, optional): The URL of the image to include in the embed message.
        """
        async def send_embed_async():
            try:
                channel = self.client.get_channel(channel_id)
                if channel:
                    # Convert color string to discord.Color
                    embed_color = getattr(discord.Color, color.lower(), discord.Color.blue)()

                    embed = discord.Embed(
                        title=title,
                        color=embed_color
                    )
                    if image_url:
                        embed.set_image(url=image_url)
                    for name, value in fields:
                        embed.add_field(name=name, value=value, inline=False)

                    await channel.send(embed=embed)
                else:
                    self.logger.log(f"Channel {channel_id} not found", 'error', 'DiscordClient')
            except discord.errors.Forbidden:
                self.logger.log(f"Cannot send embed to channel {channel_id}. Forbidden.", 'error', 'DiscordClient')
            except Exception as e:
                self.logger.log(f"Error sending embed to channel {channel_id}: {str(e)}", 'error', 'DiscordClient')

        asyncio.run_coroutine_threadsafe(send_embed_async(), self.client.loop)

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

        self.logger.log(f"Register command: {name}, Function: {function_name}", "info", "DiscordClient")
        self.tree.add_command(command_callback)

    async def handle_command(self, interaction: discord.Interaction, command_name: str, function_name: str, kwargs: dict):
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
            print(f"Channel with ID {channel_id} not found.")

    def add_role(self, guild_id, user_id, role_name):
        """
        Add a role to a user in a specified guild.

        This method demonstrates how to run an asynchronous operation synchronously
        from an external thread. It uses asyncio.run_coroutine_threadsafe to schedule
        the operation in the Discord client's event loop and waits for the result.

        Args:
            guild_id (int): The ID of the guild.
            user_id (int): The ID of the user.
            role_name (str): The name of the role to add.

        Returns:
            str: A message indicating the result of the operation.
        """
        async def add_role_async():
            try:
                guild = self.client.get_guild(guild_id)
                if not guild:
                    return f"Guild with ID {guild_id} not found."

                member = await guild.fetch_member(user_id)
                if not member:
                    return f"User with ID {user_id} not found in the guild."

                role = discord.utils.get(guild.roles, name=role_name)
                if not role:
                    return f"Role '{role_name}' not found in the guild."

                await member.add_roles(role)
                return f"Successfully added role '{role_name}' to user {member.name}."
            except discord.errors.Forbidden:
                return f"Bot doesn't have permission to manage roles."
            except Exception as e:
                return f"Error adding role: {str(e)}"

        return asyncio.run_coroutine_threadsafe(add_role_async(), self.client.loop).result()

    def remove_role(self, guild_id, user_id, role_name):
        """
        Remove a role from a user in a specified guild.

        This method demonstrates how to run an asynchronous operation synchronously
        from an external thread. It uses asyncio.run_coroutine_threadsafe to schedule
        the operation in the Discord client's event loop and waits for the result.

        Args:
            guild_id (int): The ID of the guild.
            user_id (int): The ID of the user.
            role_name (str): The name of the role to remove.

        Returns:
            str: A message indicating the result of the operation.
        """
        async def remove_role_async():
            try:
                guild = self.client.get_guild(guild_id)
                if not guild:
                    return f"Guild with ID {guild_id} not found."

                member = await guild.fetch_member(user_id)
                if not member:
                    return f"User with ID {user_id} not found in the guild."

                role = discord.utils.get(guild.roles, name=role_name)
                if not role:
                    return f"Role '{role_name}' not found in the guild."

                await member.remove_roles(role)
                return f"Successfully removed role '{role_name}' from user {member.name}."
            except discord.errors.Forbidden:
                return f"Bot doesn't have permission to manage roles."
            except Exception as e:
                return f"Error removing role: {str(e)}"

        return asyncio.run_coroutine_threadsafe(remove_role_async(), self.client.loop).result()

    def has_role(self, guild_id, user_id, role_name):
        """
        Check if a user has a specified role in a guild.

        This method demonstrates how to run an asynchronous operation synchronously
        from an external thread. It uses asyncio.run_coroutine_threadsafe to schedule
        the operation in the Discord client's event loop and waits for the result.

        Args:
            guild_id (int): The ID of the guild.
            user_id (int): The ID of the user.
            role_name (str): The name of the role to check.

        Returns:
            bool: True if the user has the role, False otherwise.
        """
        async def has_role_async():
            try:
                guild = self.client.get_guild(guild_id)
                if not guild:
                    return f"Guild with ID {guild_id} not found."

                member = await guild.fetch_member(user_id)
                if not member:
                    return f"User with ID {user_id} not found in the guild."

                role = discord.utils.get(guild.roles, name=role_name)
                if not role:
                    return f"Role '{role_name}' not found in the guild."

                return role in member.roles
            except Exception as e:
                return f"Error checking role: {str(e)}"

        return asyncio.run_coroutine_threadsafe(has_role_async(), self.client.loop).result()

    def list_roles(self, guild_id, user_id=None):
        """
        List roles in a guild and optionally for a specific user.

        This method demonstrates how to run an asynchronous operation synchronously
        from an external thread. It uses asyncio.run_coroutine_threadsafe to schedule
        the operation in the Discord client's event loop and waits for the result.

        Args:
            guild_id (int): The ID of the guild.
            user_id (int, optional): The ID of the user. If provided, the method will also list the user's roles.

        Returns:
            str: A formatted string listing the roles in the guild and optionally for the user.
        """
        async def list_roles_async():
            try:
                guild = self.client.get_guild(guild_id)
                if not guild:
                    return f"Guild with ID {guild_id} not found."

                # List all guild roles
                all_roles = [f"{role.name} (ID: {role.id})" for role in guild.roles if role.name != "@everyone"]
                guild_roles = "Guild Roles:\n" + "\n".join(all_roles) if all_roles else "No roles found in this guild."

                # List user roles if user_id is provided
                user_roles = ""
                if user_id:
                    member = await guild.fetch_member(user_id)
                    if member:
                        user_role_list = [f"{role.name} (ID: {role.id})" for role in member.roles if
                                          role.name != "@everyone"]
                        user_roles = f"\n\nRoles for user {member.name}:\n" + "\n".join(
                            user_role_list) if user_role_list else f"\n\nUser {member.name} has no roles."
                    else:
                        user_roles = f"\n\nUser with ID {user_id} not found in the guild."

                return guild_roles + user_roles
            except Exception as e:
                return f"Error listing roles: {str(e)}"

        return asyncio.run_coroutine_threadsafe(list_roles_async(), self.client.loop).result()

    def create_thread(self, channel_id, message_id, name, auto_archive_duration=1440, remove_author=True):
        """
        Create a new thread in a specified channel, attached to a specific message.

        This method uses asyncio.run_coroutine_threadsafe to safely schedule the
        asynchronous thread creation operation in the Discord client's event loop,
        allowing it to be called from any thread.

        Args:
            channel_id (int): The ID of the channel to create the thread in.
            message_id (int): The ID of the message to attach the thread to.
            name (str): The name of the new thread.
            auto_archive_duration (int, optional): Duration in minutes after which the thread
                                                   will automatically archive. Default is 1440 (24 hours).
            remove_author (bool, optional): Whether to remove the message author from the thread. Default is False.

        Returns:
            int: The ID of the created thread, or None if creation failed.
        """
        async def create_thread_async():
            try:
                channel = self.client.get_channel(channel_id)
                if not channel:
                    self.logger.log(f"Channel {channel_id} not found", 'error', 'DiscordClient')
                    return None

                message = await channel.fetch_message(message_id)
                if not message:
                    self.logger.log(f"Message {message_id} not found in channel {channel_id}", 'error', 'DiscordClient')
                    return None

                thread = await message.create_thread(name=name, auto_archive_duration=auto_archive_duration)
                self.logger.log(f"Thread '{name}' created successfully", 'info', 'DiscordClient')

                if remove_author:
                    await thread.remove_user(message.author)
                    self.logger.log(f"Removed author {message.author} from thread '{name}'", 'info', 'DiscordClient')

                return thread.id
            except discord.errors.Forbidden:
                self.logger.log(f"Bot doesn't have permission to create threads in channel {channel_id}", 'error', 'DiscordClient')
            except Exception as e:
                self.logger.log(f"Error creating thread: {str(e)}", 'error', 'DiscordClient')
            return None

        return asyncio.run_coroutine_threadsafe(create_thread_async(), self.client.loop).result()

    def reply_to_thread(self, thread_id, content):
        """
        Reply to a specific thread.

        This method uses asyncio.run_coroutine_threadsafe to safely schedule the
        asynchronous reply operation in the Discord client's event loop,
        allowing it to be called from any thread.

        Args:
            thread_id (int): The ID of the thread to reply to.
            content (str): The content of the reply message.

        Returns:
            bool: True if the reply was sent successfully, False otherwise.
        """
        async def reply_async():
            try:
                thread = self.client.get_channel(thread_id)
                if not thread:
                    self.logger.log(f"Thread {thread_id} not found", 'error', 'DiscordClient')
                    return False

                # Split the content into semantic chunks
                chunks = semantic_chunk(content, min_length=200, max_length=1900)
                for i, chunk in enumerate(chunks, 1):
                    message = f"```chunk.content```"
                    await thread.send(message)
                
                self.logger.log(f"Reply sent to thread {thread_id}", 'info', 'DiscordClient')
                return True
            except discord.errors.Forbidden:
                self.logger.log(f"Bot doesn't have permission to reply to thread {thread_id}", 'error', 'DiscordClient')
            except Exception as e:
                self.logger.log(f"Error replying to thread: {str(e)}", 'error', 'DiscordClient')
            return False

        return asyncio.run_coroutine_threadsafe(reply_async(), self.client.loop).result()


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
