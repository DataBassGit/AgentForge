from customagents.GenerateAgent import GenerateAgent
from customagents.ReflectAgent import ReflectAgent
from customagents.TheoryAgent import TheoryAgent
from customagents.ThoughtAgent import ThoughtAgent
from agentforge.utils.guiutils.listenforui import BotApi as ListenForUI
from agentforge.utils.guiutils.sendtoui import ApiClient

thou = ThoughtAgent()
gen = GenerateAgent()
theo = TheoryAgent()
ref = ReflectAgent()

class Chatbot:

    def __init__(self):

        pass
    def run(self,message):
        print(message)
        ApiClient().send_message("layer_update", 0, message)

if __name__ == '__main__':
    print("Starting")

    api = ListenForUI(callback=Chatbot().run)

    # Add a simple input loop to keep the main thread running
    while True:
        try:
            # Use input or sleep for some time, so the main thread doesn't exit immediately
            user_input = input("Press Enter to exit...")
            if user_input:
                break
        except KeyboardInterrupt:
            break
