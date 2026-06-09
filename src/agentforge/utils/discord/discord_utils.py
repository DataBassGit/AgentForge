import asyncio
import os
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

    def send_message(self, channel_id, content, message_id=None, images=None):
        """
        Send a message to a specified Discord channel, optionally replying to a specific message.

        Args:
            channel_id (int): The ID of the channel to send the message to
            content (str): The content of the message to send
            message_id (int, optional): The ID of the message to reply to. Defaults to None.
            images (path, optional): URL or local path of an image to embed.
        """

        async def send():
            sent_id = None
            try:
                messages = semantic_chunk(content, min_length=200,
                                          max_length=1900) if content and content.strip() else []
                channel = self.client.get_channel(channel_id)
                if not channel:
                    self.logger.error(f"[DiscordUtils.send_message] Channel {channel_id} not found")
                    return

                # Create a message reference if a message_id is provided
                reference = (
                    discord.MessageReference(message_id=message_id, channel_id=channel_id) if message_id else None
                )
                first_message_sent = False
                for msg in messages:
                    # ... existing chunk loop, unchanged ...
                    current_ref = reference if not first_message_sent else None
                    sent = await channel.send(msg.content, reference=current_ref)
                    sent_id = sent.id
                    first_message_sent = True

                # Embed/attach images after the text
                if images:
                    files, embeds = self._build_image_payloads(images)
                    if files or embeds:
                        kwargs = {}
                        if files:  kwargs['files'] = files
                        if embeds: kwargs['embeds'] = embeds
                        await channel.send(**kwargs)
                return sent_id
            except discord.errors.Forbidden:
                self.logger.error(
                    f"[DiscordUtils.send_message] Bot doesn't have permission to send messages in channel {channel_id}"
                )
            except Exception as e:
                content_preview = content[:100]
                self.logger.error(
                    f"[DiscordUtils.send_message] Error sending message to channel {channel_id}: {str(e)}\n"
                    f"Message: {content_preview}..."
                )

        try:
            return asyncio.run_coroutine_threadsafe(send(), self.client.loop).result()
        except RuntimeError as e:
            self.logger.error(f"[DiscordUtils.send_message] Failed to schedule: {str(e)}")

    def send_dm(self, user_id, content, images=None):
        """
        Send a direct message to a specified Discord user.

        Args:
            user_id (int): The ID of the user to send the direct message to
            content (str): The content of the direct message to send
        """

        async def send_dm_async():
            try:
                user = await self.client.fetch_user(user_id)
                if not user:
                    self.logger.error(f"[DiscordUtils.send_dm] User {user_id} not found")
                    return
                messages = semantic_chunk(content, min_length=200,
                                          max_length=1900) if content and content.strip() else []
                for msg in messages:
                    if len(msg.content) > 2000:
                        for sub_msg in semantic_chunk(msg.content, min_length=200, max_length=1900):
                            await user.send(sub_msg.content)
                    else:
                        await user.send(msg.content)

                if images:
                    files, embeds = self._build_image_payloads(images)
                    if files or embeds:
                        kwargs = {}
                        if files:  kwargs['files'] = files
                        if embeds: kwargs['embeds'] = embeds
                        await user.send(**kwargs)
            except discord.errors.NotFound:
                self.logger.error(f"[DiscordUtils.send_dm] User {user_id} not found")
            except discord.errors.Forbidden:
                self.logger.error(f"[DiscordUtils.send_dm] Cannot DM user {user_id}. Forbidden.")
            except Exception as e:
                self.logger.error(f"[DiscordUtils.send_dm] Error sending DM to {user_id}: {str(e)}")

        try:
            asyncio.run_coroutine_threadsafe(send_dm_async(), self.client.loop)
        except RuntimeError as e:
            self.logger.error(f"[DiscordUtils.send_dm] Failed to schedule DM: {str(e)}")

    def send_embed(self, channel_id, title, fields, color="blue", image_url=None):
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

                    embed = discord.Embed(title=title, color=embed_color)
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

    def create_thread(
        self, channel_id, message_id, name, auto_archive_duration=1440, remove_author=True, do_lock_thread=True
    ):
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
                    self.logger.error(
                        f"[DiscordUtils.create_thread] Message with ID {message_id} not found in channel {channel_id}"
                    )
                    return None

                # Safely check if thread exists using hasattr
                if hasattr(message, "thread") and message.thread:
                    self.logger.info(f"[DiscordUtils.create_thread] Thread already exists for message {message_id}")
                    return message.thread.id

                thread = await message.create_thread(name=name, auto_archive_duration=auto_archive_duration)
                self.logger.info(f"[DiscordUtils.create_thread] Thread '{name}' created successfully")

                if remove_author:
                    await thread.remove_user(message.author)
                    self.logger.info(
                        f"[DiscordUtils.create_thread] Removed author {message.author} from thread '{name}'"
                    )
                if do_lock_thread:
                    await thread.edit(locked=True, archived=False)
                    self.logger.info(f"[DiscordUtils.create_thread] Locked thread '{name}'")

                return thread.id
            except discord.errors.Forbidden:
                self.logger.error(
                    "[DiscordUtils.create_thread] Bot doesn't have permission to create threads "
                    f"in channel {channel_id}"
                )
            except discord.errors.HTTPException as e:
                if e.code == 160004:  # Thread already exists error code
                    if message.thread:
                        return message.thread.id
                    self.logger.error("[DiscordUtils.create_thread] Thread exists but cannot be accessed")
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
                self.logger.error(
                    f"[DiscordUtils.reply_to_thread] Bot doesn't have permission to reply to thread {thread_id}"
                )
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
                    f"[DiscordUtils.lock_thread] Bot doesn't have MANAGE_THREADS permission for {thread_id}"
                )
            except Exception as e:
                self.logger.error(f"[DiscordUtils.lock_thread] Error locking thread: {str(e)}")
            return False

        try:
            return asyncio.run_coroutine_threadsafe(lock_async(), self.client.loop).result()
        except RuntimeError as e:
            self.logger.error(f"[DiscordUtils.lock_thread] Failed to schedule thread lock: {str(e)}")
            return False


    def set_channel_presence(self, channel_id, is_present=True):
        """
        Modifies the bot's permissions in a channel to simulate entering/leaving a room.
        """

        async def update_presence():
            try:
                # Fetch channel (Bot must be Admin to find channels it currently can't "view")
                channel = self.client.get_channel(channel_id)
                if not channel:
                    try:
                        channel = await self.client.fetch_channel(channel_id)
                    except discord.NotFound:
                        self.logger.error(f"[DiscordUtils.set_channel_presence] Channel {channel_id} not found")
                        return False

                bot_member = channel.guild.get_member(self.client.user.id)
                overwrite = channel.overwrites_for(bot_member)

                # Toggle view and send permissions to physically show/hide her from the room
                overwrite.view_channel = is_present
                overwrite.send_messages = is_present

                await channel.set_permissions(bot_member, overwrite=overwrite)
                self.logger.info(f"[DiscordUtils.set_channel_presence] Set presence in {channel_id} to {is_present}")
                return True

            except discord.errors.Forbidden:
                self.logger.error(
                    f"[DiscordUtils.set_channel_presence] Missing 'Manage Roles/Channels' permission in channel {channel_id}")
            except Exception as e:
                self.logger.error(f"[DiscordUtils.set_channel_presence] Error updating presence: {str(e)}")
            return False

        try:
            return asyncio.run_coroutine_threadsafe(update_presence(), self.client.loop).result()
        except RuntimeError as e:
            self.logger.error(f"[DiscordUtils.set_channel_presence] Failed to schedule presence update: {str(e)}")
            return False

    def set_role_channel_presence(self, channel_id, role_name, is_present=True):
        """
        Modifies a specific role's permissions in a channel to simulate entering/leaving a room.
        """

        async def update_role_presence():
            try:
                # Fetch channel
                channel = self.client.get_channel(channel_id)
                if not channel:
                    try:
                        channel = await self.client.fetch_channel(channel_id)
                    except discord.NotFound:
                        self.logger.error(f"[DiscordUtils.set_role_channel_presence] Channel {channel_id} not found")
                        return False

                # Find the target role in the guild by name
                target_role = discord.utils.get(channel.guild.roles, name=role_name)
                if not target_role:
                    self.logger.error(f"[DiscordUtils.set_role_channel_presence] Role '{role_name}' not found in guild")
                    return False

                overwrite = channel.overwrites_for(target_role)

                # Toggle view and send permissions for the role
                overwrite.view_channel = is_present
                overwrite.send_messages = is_present

                await channel.set_permissions(target_role, overwrite=overwrite)
                self.logger.info(
                    f"[DiscordUtils.set_role_channel_presence] Set presence for role '{role_name}' in {channel_id} to {is_present}")
                return True

            except discord.errors.Forbidden:
                self.logger.error(
                    f"[DiscordUtils.set_role_channel_presence] Missing 'Manage Roles/Channels' permission in channel {channel_id}")
            except Exception as e:
                self.logger.error(f"[DiscordUtils.set_role_channel_presence] Error updating role presence: {str(e)}")
            return False

        try:
            return asyncio.run_coroutine_threadsafe(update_role_presence(), self.client.loop).result()
        except RuntimeError as e:
            self.logger.error(
                f"[DiscordUtils.set_role_channel_presence] Failed to schedule role presence update: {str(e)}")
            return False

    def set_member_channel_presence(self, channel_id, user_id, is_present=True):
        """
        Modifies a specific user's permissions in a channel to simulate letting them into a room.
        """

        async def update_member_presence():
            try:
                # Fetch channel
                channel = self.client.get_channel(channel_id)
                if not channel:
                    try:
                        channel = await self.client.fetch_channel(channel_id)
                    except discord.NotFound:
                        self.logger.error(f"[DiscordUtils.set_member_channel_presence] Channel {channel_id} not found")
                        return False

                # Fetch the specific member from the guild
                member = channel.guild.get_member(user_id)
                if not member:
                    try:
                        member = await channel.guild.fetch_member(user_id)
                    except discord.NotFound:
                        self.logger.error(
                            f"[DiscordUtils.set_member_channel_presence] Member {user_id} not found in guild")
                        return False

                overwrite = channel.overwrites_for(member)

                # Toggle view and send permissions for the specific user
                overwrite.view_channel = is_present
                overwrite.send_messages = is_present

                await channel.set_permissions(member, overwrite=overwrite)
                self.logger.info(
                    f"[DiscordUtils.set_member_channel_presence] Set presence for user {user_id} in {channel_id} to {is_present}")
                return True

            except discord.errors.Forbidden:
                self.logger.error(
                    f"[DiscordUtils.set_member_channel_presence] Missing 'Manage Roles/Channels' permission")
            except Exception as e:
                self.logger.error(
                    f"[DiscordUtils.set_member_channel_presence] Error updating member presence: {str(e)}")
            return False

        try:
            return asyncio.run_coroutine_threadsafe(update_member_presence(), self.client.loop).result()
        except RuntimeError as e:
            self.logger.error(
                f"[DiscordUtils.set_member_channel_presence] Failed to schedule member presence update: {str(e)}")
            return False

    def clear_channel(self, channel_id, limit=1000):
        """
        Purges messages from a channel to provide a fresh start.
        """

        async def purge_async():
            try:
                channel = self.client.get_channel(channel_id)
                if not channel:
                    self.logger.error(f"[DiscordUtils.clear_channel] Channel {channel_id} not found")
                    return False

                deleted = await channel.purge(limit=limit)
                self.logger.info(f"[DiscordUtils.clear_channel] Deleted {len(deleted)} messages in {channel_id}")
                return True
            except discord.errors.Forbidden:
                self.logger.error(f"[DiscordUtils.clear_channel] Missing 'Manage Messages' permission")
            except Exception as e:
                self.logger.error(f"[DiscordUtils.clear_channel] Error: {e}")
            return False

        try:
            return asyncio.run_coroutine_threadsafe(purge_async(), self.client.loop).result()
        except RuntimeError as e:
            self.logger.error(f"[DiscordUtils.clear_channel] Failed: {e}")
            return False

    def get_channel_members(self, channel_id):
        """
        Returns a list of members who have view permissions for a specific channel.
        """
        channel = self.client.get_channel(channel_id)
        if not channel:
            return []

        # Returns members who can see the channel
        return [member for member in channel.members if not member.bot]

    def _build_image_payloads(self, images):
        """
        Turn a list of image references into Discord send payloads.
          - http(s) URLs        -> embeds (Discord fetches & displays them)
          - existing local paths -> uploaded as file attachments
        Returns (files, embeds), each capped at Discord's per-message limit of 10.
        """
        files, embeds = [], []
        for img in images or []:
            if not img or not isinstance(img, str):
                continue
            if img.lower().startswith(('http://', 'https://')):
                if len(embeds) < 10:
                    embed = discord.Embed()
                    embed.set_image(url=img)
                    embeds.append(embed)
            elif os.path.isfile(img):
                if len(files) < 10:
                    files.append(discord.File(img))
        return files, embeds

    def get_message_image_urls(self, channel_id, message_id):
        """
        Fetch a message and return current (freshly re-signed) URLs for its image
        attachments. Returns [] if the message is gone or inaccessible.
        """

        async def _fetch():
            channel = self.client.get_channel(int(channel_id))
            if channel is None:
                channel = await self.client.fetch_channel(int(channel_id))
            message = await channel.fetch_message(int(message_id))
            urls = []
            for a in message.attachments:
                ct = a.content_type or ""
                if ct.startswith("image/") or a.filename.lower().endswith(
                        ('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    urls.append(a.url)
            return urls

        try:
            return asyncio.run_coroutine_threadsafe(_fetch(), self.client.loop).result()
        except Exception as e:
            self.logger.error(f"[DiscordUtils.get_message_image_urls] {channel_id}/{message_id}: {e}")
            return []
