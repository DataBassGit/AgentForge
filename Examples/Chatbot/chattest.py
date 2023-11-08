from layers.Chat import Chatbot
from agentforge.utils.function_utils import Functions

chat = Chatbot()
functions = Functions()


class ChatTest:
    def run(self, message):
        print(message)
        return chat.run(message)


if __name__ == "__main__":
    chattest = ChatTest()

    while True:
        message = functions.user_interface.get_user_input()
        result = chattest.run(message=message)
        print(f"\n\n\nUser: {message}\nChatbot: {result}")