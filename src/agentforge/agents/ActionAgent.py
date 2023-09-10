from agentforge.agent import Agent


class ActionAgent(Agent):

    actions = {}

    def load_additional_data(self):
        self.data['task'] = self.functions.get_current_task()['document']
        self.load_actions()

    def load_actions(self):
        threshold = 1
        num_results = 10
        params = {
            "collection_name": 'Actions',
            "query": self.data['task'],
            "threshold": threshold,
            "num_results": num_results
        }

        self.actions = self.storage.search_storage_by_threshold(params)

    def format_actions(self):
        formatted_actions = []

        for action_name, metadata in self.actions.items():
            action_desc = metadata.get("Description", "No Description")
            formatted_action = f"Action: {action_name}\nDescription: {action_desc}\n"
            formatted_actions.append(formatted_action)

        self.data['action_list'] = "\n".join(formatted_actions)

    def process_data(self):
        self.reformat_actions()
        self.format_actions()

    def parse_result(self):
        self.result = self.functions.string_to_dictionary(self.result)

    def build_output(self):
        selected_action = self.result['action']
        result = f"{selected_action}: {self.actions[selected_action]['Description']}"
        self.functions.print_result(result, 'Action Selected')

    def reformat_actions(self):
        reformatted_actions = {}

        for metadata in self.actions.get("metadatas", [])[0]:
            action_name = metadata.get("Name")
            if action_name:  # Check if the action name is not None or empty
                # Remove the timestamp as you don't seem to want it in the final output
                metadata.pop('timestamp', None)
                reformatted_actions[action_name] = metadata

        self.actions = reformatted_actions

    def save_result(self):
        pass
