from agentforge.agent import Agent


class StopExecution(Exception):
    pass


class ActionSelectionAgent(Agent):

    actions = {}
    threshold = 0.6
    num_results = 10

    def run(self, **kwargs):
        try:
            return super().run(**kwargs)
        except StopExecution:
            self.functions.printing.print_result('No Relevant Action Found', 'Selection Results')
            return None

    def set_threshold(self, new_threshold):
        self.threshold = new_threshold

    def set_number_of_results(self, new_num_results):
        self.num_results = new_num_results

    def load_additional_data(self):
        self.data['task'] = self.functions.task_handling.get_current_task()['document']
        self.load_actions()

    def load_actions(self):
        params = {
            "collection_name": 'Actions',
            "query": self.data['task'],
            "threshold": self.threshold,
            "num_results": self.num_results
        }

        self.actions = self.storage.search_storage_by_threshold(params)

    def stop_execution_on_no_action(self):
        if 'failed' in self.actions:
            raise StopExecution("No actions found, stopping execution.")

    def format_actions(self):
        if 'failed' not in self.actions:
            formatted_actions = []

            for action_name, metadata in self.actions.items():
                action_desc = metadata.get("Description", "No Description")
                formatted_action = f"Action: {action_name}\nDescription: {action_desc}\n"
                formatted_actions.append(formatted_action)

            self.data['action_list'] = "\n".join(formatted_actions)

    def process_data(self):
        self.stop_execution_on_no_action()
        self.parse_actions()
        self.format_actions()

    def parse_result(self):
        self.result = self.functions.parsing.string_to_dictionary(self.result)

    def build_output(self):
        selected_action = self.result['action']
        if selected_action in self.actions:
            self.output = self.actions[selected_action]
        else:
            self.output = f"The '{selected_action}' action does not exist. It is very likely the agent did not correctly choose an action from the given list."

    def parse_actions(self):
        parsed_actions = {}

        if 'failed' not in self.actions:
            for metadata in self.actions.get("metadatas", [])[0]:
                action_name = metadata.get("Name")
                if action_name:
                    metadata.pop('timestamp', None)
                    parsed_actions[action_name] = metadata

            self.actions = parsed_actions

    def save_result(self):
        pass
