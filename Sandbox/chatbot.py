# main.py

from modules.discord_client import DiscordClient
import time


def process_message(message):
    print(f"Processing message: {message}")
    # Simulate some time-consuming task
    time.sleep(5)
    return f"Processed: {message}"


def main():
    client = DiscordClient()
    client.run()

    while True:
        try:
            print("Getting message")
            for message in client.process_channel_messages():
                print(f"Message received: {message}")
                response = process_message(message)
                client.send_message(message[0], response)
        except KeyboardInterrupt:
            print("Stopping...")
            client.stop()
        finally:
            time.sleep(5)


if __name__ == "__main__":
    main()
