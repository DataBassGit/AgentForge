# utils/guiutils/discord_client.py

import discord
import os
import asyncio
import threading
from agentforge.utils.functions.Logger import Logger


class DiscordClient:
    def __init__(self):
        self.token = str(os.getenv('DISCORD_TOKEN'))
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.client = discord.Client(intents=self.intents)
        self.logger = Logger('DiscordClient')
        self.message_queue = {}
        self.running = False

        @self.client.event
        async def on_ready():
            print("Client Ready")
            self.logger.log(f'{self.client.user} has connected to Discord!', 'info', 'DiscordClient')

        @self.client.event
        async def on_message(message: discord.Message):
            self.logger.log(f"On Message: {message}", 'debug', 'DiscordClient')

            # content = message.content.replace(f'<@!{user.id}>', f'@{mention_name}')
            content = message.content

            message_data = {
                "channel": str(message.channel),
                "channel_id": message.channel.id,
                "message": content,
                "author": message.author.display_name,
                "author_id": message.author,
                "timestamp": message.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }

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
        def run_discord():
            print("Client Starting")
            asyncio.run(self.client.start(self.token))

        self.discord_thread = threading.Thread(target=run_discord)
        self.discord_thread.start()
        self.running = True

    def stop(self):
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
                message = self.message_queue.popitem()
                yield message
            except Exception as e:
                print(f"Exception: {e}")
        else:
            pass

    def send_message(self, channel_id, content):
        async def send():
            channel = self.client.get_channel(channel_id)
            if channel:
                await channel.send(content)
            else:
                self.logger.log(f"Channel {channel_id} not found", 'error', 'DiscordClient')

        asyncio.run_coroutine_threadsafe(send(), self.client.loop)

    def send_dm(self, user_id, content):
        async def send_dm_async():
            try:
                user = await self.client.fetch_user(user_id)
                if user:
                    await user.send(content)
                else:
                    self.logger.log(f"User {user_id} not found", 'error', 'DiscordClient')
            except discord.errors.NotFound:
                self.logger.log(f"User {user_id} not found", 'error', 'DiscordClient')
            except discord.errors.Forbidden:
                self.logger.log(f"Cannot send DM to user {user_id}. Forbidden.", 'error', 'DiscordClient')
            except Exception as e:
                self.logger.log(f"Error sending DM to user {user_id}: {str(e)}", 'error', 'DiscordClient')

        asyncio.run_coroutine_threadsafe(send_dm_async(), self.client.loop)


if __name__ == "__main__":
    # This is just for testing the DiscordClient
    import time

    client = DiscordClient()
    client.run()

    while True:
        try:
            for message in client.process_channel_messages():
                time.sleep(5)
                client.send_message(message[0], f"Processed: {message}")
        except KeyboardInterrupt:
            print("Stopping...")
            client.stop()
        finally:
            time.sleep(5)
