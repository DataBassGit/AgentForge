from customagents.GenerateAgent import GenerateAgent
from customagents.ReflectAgent import ReflectAgent
from customagents.TheoryAgent import TheoryAgent
from customagents.ThoughtAgent import ThoughtAgent
from agentforge.utils.guiutils.listenforui import BotApi as ListenForUI
from agentforge.utils.guiutils.sendtoui import ApiClient
from agentforge.utils.storage_interface import StorageInterface
from agentforge.modules.ActionExecution import Action
from agentforge.agents.ActionSelectionAgent import ActionSelectionAgent
from agentforge.utils.function_utils import Functions

import re


class Chatbot:
    storage = StorageInterface().storage_utils
    thou = ThoughtAgent()
    gen = GenerateAgent()
    theo = TheoryAgent()
    ref = ReflectAgent()
    chat_history = None
    result = None
    parsed_data = None
    memories = None
    chat_response = None
    message = None
    cat = None
    categories = None

    def __init__(self):

        self.chat_history = self.storage.select_collection("chat_history")
        self.action_execution = Action()
        self.action_selection = ActionSelectionAgent()
        self.selected_action = None
        self.functions = Functions()
        self.reflection = None
        self.theory = None
        self.generate = None
        self.thought = None

    def run(self, message):
        print(message)
        self.message = message

        # save message to chat history
        history = self.chatman(message)

        # run thought agent
        self.thought_agent(message, history)

        # run generate agent
        self.gen_agent(message, history)

        # run theory agent
        self.theory_agent(message, history)

        # run reflect agent
        self.reflect_agent(message, history)
        self.memories = []

    def thought_agent(self, message, history):
        self.result = self.thou.run(user_message=message,
                                    history=history["documents"])
        ApiClient().send_message("layer_update", 1, f"Thought Agent:\n=====\n{self.result}\n=====\n")
        self.thought = self.parse_lines()
        print(f"self.thought: {self.thought}")
        self.categories = self.thought["Categories"].split(",")
        for category in self.categories:
            formatted_category = self.format_string(category)
            print(f"formatted_category: {formatted_category}")
            self.memory_recall(formatted_category, message)

    def gen_agent(self, message, history):
        self.result = self.gen.run(user_message=message,
                                   history=history["documents"],
                                   memories=self.memories,
                                   emotion=self.thought["Emotion"],
                                   reason=self.thought["Reason"],
                                   thought=self.thought["Inner Thought"])
        ApiClient().send_message("layer_update", 1, f"Generate Agent:\n=====\n{self.result}\n=====\n")
        self.generate = self.parse_lines()
        print(f"self.thought: {self.generate}")
        self.chat_response = self.result

    def theory_agent(self, message, history):
        self.result = self.theo.run(user_message=message,
                                    history=history["documents"])
        ApiClient().send_message("layer_update", 1, f"Theory Agent:\n=====\n{self.result}\n=====\n")
        self.theory = self.parse_lines()
        print(f"self.thought: {self.theory}")

    def reflect_agent(self, message, history):
        if "What" not in self.theory:
            self.theory = {"What": "Don't Know.", "Why": "Not enough information."}

        self.result = self.ref.run(user_message=message,
                                   history=history["documents"],
                                   memories=self.memories,
                                   emotion=self.thought["Emotion"],
                                   reason=self.thought["Reason"],
                                   thought=self.thought["Inner Thought"],
                                   what=self.theory["What"],
                                   why=self.theory["Why"],
                                   response=self.chat_response)
        ApiClient().send_message("layer_update", 1, f"Reflect Agent:\n=====\n{self.result}\n=====\n")
        self.reflection = self.parse_lines()
        print(f"self.thought: {self.reflection}")

        if self.reflection["Choice"] == "respond":
            ApiClient().send_message("layer_update", 0, f"Chatbot: {self.chat_response}\n")
            self.save_memory(self.chat_response)
        elif self.reflection["Choice"] == "nothing":
            ApiClient().send_message("layer_update", 0, f"Chatbot: ...\n")
        else:
            new_response = self.gen.run(user_message=message,
                                        history=history["documents"],
                                        memories=self.memories,
                                        emotion=self.thought["Emotion"],
                                        reason=self.thought["Reason"],
                                        thought=self.thought["Inner Thought"],
                                        what=self.theory["What"],
                                        why=self.theory["Why"],
                                        feedback=self.reflection["Reason"],
                                        response=self.chat_response)
            ApiClient().send_message("layer_update", 0, f"Chatbot: {new_response}\n")
            self.save_memory(new_response)

    def save_memory(self, bot_response):
        # Existing chat history saving logic
        size = self.storage.count_collection("chat_history")
        bot_message = f"Chatbot: {bot_response}"
        user_chat = f"User: {self.message}"

        # New logic for saving to each category collection
        for category in self.categories:
            formatted_category = self.format_string(category)

            # Re-assign the values to params for each iteration
            params = {
                "collection_name": formatted_category,
                "data": [user_chat],
                "ids": [str(size + 1)],
                "metadata": [{
                    "id": size + 1,
                    "Character Response": bot_message,
                    "EmotionalResponse": self.thought["Emotion"],
                    "Inner_Thought": self.thought["Inner Thought"]
                }]
            }
            self.storage.save_memory(params)  # Save to the category-specific collection

        # Optionally, if you want to reset params["collection_name"] to "chat_history" after the loop
        params = {
            "collection_name": "chat_history",
            "data": [user_chat],
            "ids": [str(size + 1)],
            "metadata": [{
                "id": size + 1,
                "Character Response": bot_message,
                "EmotionalResponse": self.thought["Emotion"],
                "Inner_Thought": self.thought["Inner Thought"]
            }]
        }

        self.storage.save_memory(params)

    def chatman(self, message):
        size = self.storage.count_collection("chat_history")
        qsize = max(size - 10, 1)
        print(f"qsize: {qsize}")
        params = {
            "collection_name": "chat_history",
            "filter": {"id": {"$gte": qsize}}
        }
        history = self.storage.load_collection(params)
        user_message = f"User: {message}"
        print(f"history: {history}")
        params = {
            "collection_name": "chat_history",
            "data": [user_message],
            "ids": [str(size + 1)],
            "metadata": [{"id": size + 1}]
        }
        if size == 0:
            history["documents"].append("No Results!")
        self.storage.save_memory(params)
        ApiClient().send_message("layer_update", 0, f"User: {message}\n")
        return history

    def parse_lines(self):
        result_dict = {}
        lines = self.result.strip().split('\n')
        for line in lines:
            parts = line.split(':')
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                result_dict[key] = value
        return result_dict

    def memory_recall(self, categories, message, count=10):
        params = {
            "collection_name": categories,
            "query": message
        }
        new_memories = self.storage.query_memory(params, count)
        if new_memories["documents"] != 'No Results!':
            if new_memories is None:
                new_memories = []
            if not hasattr(self, 'memories') or self.memories is None:
                self.memories = []
            self.memories.extend([new_memories])
        return self.memories

    @staticmethod
    def format_string(input_str):
        # Remove leading and trailing whitespace
        input_str = input_str.strip()

        # Replace non-alphanumeric, non-underscore, non-hyphen characters with underscores
        input_str = re.sub("[^a-zA-Z0-9_-]", "_", input_str)

        # Replace consecutive periods with a single period
        while ".." in input_str:
            input_str = input_str.replace("..", ".")

        # Ensure it's not a valid IPv4 address
        if re.match(r'^\d+\.\d+\.\d+\.\d+$', input_str):
            input_str = "a" + input_str

        # Ensure length is between 3 and 63 characters
        while len(input_str) < 3:
            input_str += input_str
        if len(input_str) > 63:
            input_str = input_str[:63]

        # Ensure it starts and ends with an alphanumeric character
        if not input_str[0].isalnum():
            input_str = "a" + input_str[1:]
        if not input_str[-1].isalnum():
            input_str = input_str[:-1] + "a"

        return input_str

    def check_for_actions(self):
        self.select_action()

        if self.selected_action:
            self.execute_action()
        else:
            pass

    def execute_action(self):
        action_results = self.action_execution.run(action=self.selected_action, context=self.message)
        self.functions.printing.print_result(action_results, 'Action Results')

    def select_action(self):
        self.selected_action = None
        self.selected_action = self.action_selection.run(feedback=self.message)

        if self.selected_action:
            result = f"{self.selected_action['Name']}: {self.selected_action['Description']}"
            self.functions.printing.print_result(result, 'Action Selected')

    @staticmethod
    def format_action_results(action_results):
        formatted_strings = []
        for key, value in action_results.items():
            formatted_string = f"{key}: {value}\n\n---\n"
            formatted_strings.append(formatted_string)

        return "\n".join(formatted_strings).strip('---\n')


if __name__ == '__main__':
    print("Starting")

    api = ListenForUI(callback=Chatbot().run)

    # Add a simple input loop to keep the main thread running
    while True:
        try:
            user_input = input("Press Enter to exit...")
            if user_input:
                break
        except KeyboardInterrupt:
            break
