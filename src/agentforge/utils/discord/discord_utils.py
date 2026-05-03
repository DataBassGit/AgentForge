import asyncio
import threading

import discord
from agentforge.tools.semantic_chunk import semantic_chunk

class DiscordUtils:
    def __init__(self, client, logger):
        """
        Initialize Discord utilities with client and logger instances.

        Args:
            client (discord.Client): The Discord client instance
            logger (Logger): Logger instance for error handling
        """
        self.client = client
        self.logger = logger

    def send_message(self, channel_id, content, message_id=None):
        """
        Send a message to a specified Discord channel, optionally replying to a specific message.

        Args:
            channel_id (int): The ID of the channel to send the message to
            content (str): The content of the message to send
            message_id (int, optional): The ID of the message to reply to. Defaults to None.
        """

        async def send():
            try:
                messages = semantic_chunk(content, min_length=200, max_length=1900)
                channel = self.client.get_channel(channel_id)

                if not channel:
                    self.logger.error(f"[DiscordUtils.send_message] Channel {channel_id} not found")
                    return

                # Create a message reference if a message_id is provided
                reference = discord.MessageReference(message_id=message_id,
                                                     channel_id=channel_id) if message_id else None
                first_message_sent = False

                for msg in messages:
                    if len(msg.content) > 2000:
                        # Re-chunk the over-sized message
                        sub_messages = semantic_chunk(msg.content, min_length=200, max_length=1900)
                        for sub_msg in sub_messages:
                            # Only attach the reply reference to the very first chunk sent
                            current_ref = reference if not first_message_sent else None
                            await channel.send(sub_msg.content, reference=current_ref)
                            first_message_sent = True
                    else:
                        current_ref = reference if not first_message_sent else None
                        await channel.send(msg.content, reference=current_ref)
                        first_message_sent = True

            except discord.errors.Forbidden:
                self.logger.error(
                    f"[DiscordUtils.send_message] Bot doesn't have permission to send messages in channel {channel_id}")
            except Exception as e:
                self.logger.error(
                    f"[DiscordUtils.send_message] Error sending message to channel {channel_id}: {str(e)}\nMessage: {content[:100]}...")

        try:
            return asyncio.run_coroutine_threadsafe(send(), self.client.loop)
        except RuntimeError as e:
            self.logger.error(f"[DiscordUtils.send_message] Failed to schedule message sending: {str(e)}")

    def send_dm(self, user_id, content):
        """
        Send a direct message to a specified Discord user.

        Args:
            user_id (int): The ID of the user to send the direct message to
            content (str): The content of the direct message to send
        """
        async def send_dm_async():
            try:
                user = await self.client.fetch_user(user_id)
                if user:
                    messages = semantic_chunk(content, min_length=200, max_length=1900)
                    for msg in messages:
                        if len(msg.content) > 2000:
                            # Re-chunk the over-sized message
                            sub_messages = semantic_chunk(msg.content, min_length=200, max_length=1900)
                            for sub_msg in sub_messages:
                                await user.send(sub_msg.content)
                        else:
                            await user.send(msg.content)
                else:
                    self.logger.error(f"[DiscordUtils.send_dm] User {user_id} not found")
            except discord.errors.NotFound:
                self.logger.error(f"[DiscordUtils.send_dm] User {user_id} not found")
            except discord.errors.Forbidden:
                self.logger.error(f"[DiscordUtils.send_dm] Cannot send DM to user {user_id}. Forbidden.")
            except Exception as e:
                self.logger.error(f"[DiscordUtils.send_dm] Error sending DM to user {user_id}: {str(e)}")

        try:
            asyncio.run_coroutine_threadsafe(send_dm_async(), self.client.loop)
        except RuntimeError as e:
            self.logger.error(f"[DiscordUtils.send_dm] Failed to schedule DM sending: {str(e)}")

    def send_embed(self, channel_id, title, fields, color='blue', image_url=None):
        """
        Send an embed message to a specified Discord channel.

        Args:
            channel_id (int): The ID of the channel to send the embed message to
            title (str): The title of the embed message
            fields (list): A list of tuples representing the fields of the embed message
            color (str, optional): The color of the embed message. Defaults to 'blue'
            image_url (str, optional): The URL of the image to include in the embed message
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
                    self.logger.error(f"[DiscordUtils.send_embed] Channel with ID {channel_id} not found")
            except discord.errors.Forbidden:
                self.logger.error(f"[DiscordUtils.send_embed] Cannot send embed to channel {channel_id}. Forbidden")
            except Exception as e:
                self.logger.error(f"[DiscordUtils.send_embed] Error sending embed to channel {channel_id}: {str(e)}")

        try:
            asyncio.run_coroutine_threadsafe(send_embed_async(), self.client.loop)
        except RuntimeError as e:
            self.logger.error(f"[DiscordUtils.send_embed] Failed to schedule embed sending: {str(e)}")

    def create_thread(self, channel_id, message_id, name, auto_archive_duration=1440, remove_author=True, do_lock_thread=True):
        """
        Create a new thread in a specified channel, attached to a specific message.

        Args:
            channel_id (int): The ID of the channel to create the thread in
            message_id (int): The ID of the message to attach the thread to
            name (str): The name of the new thread
            auto_archive_duration (int, optional): Duration in minutes after which the thread
                                               will automatically archive. Default is 1440 (24 hours)
            remove_author (bool, optional): Whether to remove the message author from the thread. Default is True

        Returns:
            int: The ID of the created thread, or None if creation failed
        """
        async def create_thread_async():
            try:
                channel = self.client.get_channel(channel_id)
                if not channel:
                    self.logger.error(f"[DiscordUtils.create_thread] Channel with ID {channel_id} not found")
                    return None

                message = await channel.fetch_message(message_id)
                if not message:
                    self.logger.error(f"[DiscordUtils.create_thread] Message with ID {message_id} not found in channel {channel_id}")
                    return None

                # Safely check if thread exists using hasattr
                if hasattr(message, 'thread') and message.thread:
                    self.logger.info(f"[DiscordUtils.create_thread] Thread already exists for message {message_id}")
                    return message.thread.id

                thread = await message.create_thread(name=name, auto_archive_duration=auto_archive_duration)
                self.logger.info(f"[DiscordUtils.create_thread] Thread '{name}' created successfully")

                if remove_author:
                    await thread.remove_user(message.author)
                    self.logger.info(f"[DiscordUtils.create_thread] Removed author {message.author} from thread '{name}'")
                if do_lock_thread:
                    await thread.edit(locked=True, archived=False)
                    self.logger.info(f"[DiscordUtils.create_thread] Locked thread '{name}'")

                return thread.id
            except discord.errors.Forbidden:
                self.logger.error(f"[DiscordUtils.create_thread] Bot doesn't have permission to create threads in channel {channel_id}")
            except discord.errors.HTTPException as e:
                if e.code == 160004:  # Thread already exists error code
                    if message.thread:
                        return message.thread.id
                    self.logger.error(f"[DiscordUtils.create_thread] Thread exists but cannot be accessed")
                else:
                    self.logger.error(f"[DiscordUtils.create_thread] Error creating thread: {str(e)}")

            except Exception as e:
                self.logger.error(f"[DiscordUtils.create_thread] Error creating thread: {str(e)}")
            return None

        try:
            return asyncio.run_coroutine_threadsafe(create_thread_async(), self.client.loop).result()
        except RuntimeError as e:
            self.logger.error(f"[DiscordUtils.create_thread] Failed to schedule thread creation: {str(e)}")
            return None

    def reply_to_thread(self, thread_id, content):
        """
        Reply to a specific thread.

        Args:
            thread_id (int): The ID of the thread to reply to
            content (str): The content of the reply message

        Returns:
            bool: True if the reply was sent successfully, False otherwise
        """
        async def reply_async():
            try:
                thread = self.client.get_channel(thread_id)
                if not thread:
                    self.logger.error(f"[DiscordUtils.reply_to_thread] Thread {thread_id} not found")
                    return False

                # Split the content into semantic chunks
                chunks = semantic_chunk(content, min_length=200, max_length=1900)
                for i, chunk in enumerate(chunks, 1):
                    message = f"```{chunk.content}```"
                    await thread.send(message)

                self.logger.info(f"[DiscordUtils.reply_to_thread] Reply sent to thread {thread_id}")
                return True
            except discord.errors.Forbidden:
                self.logger.error(f"[DiscordUtils.reply_to_thread] Bot doesn't have permission to reply to thread {thread_id}")
            except Exception as e:
                self.logger.error(f"[DiscordUtils.reply_to_thread] Error replying to thread: {str(e)}")
            return False

        try:
            return asyncio.run_coroutine_threadsafe(reply_async(), self.client.loop).result()
        except RuntimeError as e:
            self.logger.error(f"[DiscordUtils.reply_to_thread] Failed to schedule reply: {str(e)}")
            return False

    def lock_thread(self, thread_id):
        """
        Lock a thread so that only users with MANAGE_THREADS (like the bot) can send messages.

        Args:
            thread_id (int): The ID of the thread to lock

        Returns:
            bool: True if locked successfully, False otherwise
        """

        async def lock_async():
            try:
                # Attempt to get the thread from cache
                thread = self.client.get_channel(thread_id)

                # Fallback to fetching via API if the thread isn't in cache
                if not thread:
                    try:
                        thread = await self.client.fetch_channel(thread_id)
                    except discord.NotFound:
                        self.logger.error(f"[DiscordUtils.lock_thread] Thread {thread_id} not found")
                        return False

                # Setting locked=True prevents normal users from replying.
                # Setting archived=False ensures it stays visible in the active threads list.
                await thread.edit(locked=True, archived=False)

                self.logger.info(f"[DiscordUtils.lock_thread] Thread {thread_id} locked")
                return True

            except discord.errors.Forbidden:
                self.logger.error(
                    f"[DiscordUtils.lock_thread] Bot doesn't have MANAGE_THREADS permission for {thread_id}")
            except Exception as e:
                self.logger.error(f"[DiscordUtils.lock_thread] Error locking thread: {str(e)}")
            return False

        try:
            return asyncio.run_coroutine_threadsafe(lock_async(), self.client.loop).result()
        except RuntimeError as e:
            self.logger.error(f"[DiscordUtils.lock_thread] Failed to schedule thread lock: {str(e)}")
            return False