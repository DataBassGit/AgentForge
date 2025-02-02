# main.py

from agentforge.utils.DiscordClient import DiscordClient
import time
import yaml


def process_message(message):
    print(f"Processing message: {message}")
    # Simulate some time-consuming task
    time.sleep(5)
    return f"Processed: -{message}- This process_message function should be replaced."


def main():
    client = DiscordClient()
    client.run()

    with open(".agentforge/personas/default.yaml", "r") as file:
        persona = yaml.safe_load(file)
        persona_name = persona.get("Name")

    while True:
        try:
            print("Getting message")
            for channel_id, messages in client.process_channel_messages():
                for message in messages:
                    print(f"Message received: {message}")
                    function_name = message.get("function_name")

                    # Check if this is a /bot command
                    if function_name:
                        arg = message.get("arg")
                        print(f"This is where the bot would process the string sent by the user: {arg}")

                    # Check if the message is a DM
                    elif message['channel'].startswith('Direct Message'):
                        # If it's a DM, use the author's ID to send a DM back
                        response = process_message(message['message'])
                        client.send_dm(message['author_id'].id, response)

                    else:
                        # Check if bot is mentioned in the message
                        mentioned = any(mention.name == persona_name for mention in message['mentions'])
                        if mentioned:
                            # If bot is @ mentioned, send the response to the channel
                            # 'Name' in persona must match discord display name.
                            response = process_message(message['message'])
                            client.send_message(channel_id, response)
                        else:
                            print('That message was not for me.')
        except KeyboardInterrupt:
            print("Stopping...")
            client.stop()
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            time.sleep(5)


if __name__ == "__main__":
    main()
