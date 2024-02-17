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
            self.logger.log_result('No Relevant Action Found', 'Selection Results')
            return None

    def set_threshold(self, new_threshold):
        self.threshold = new_threshold

    def set_number_of_results(self, new_num_results):
        self.num_results = new_num_results

    def load_additional_data(self):
        try:
            self.load_actions()
        except Exception as e:
            self.logger.log(f"Error loading additional data: {e}", 'error')

    def load_actions(self):
        try:
            params = {
                "collection_name": 'Actions',
                "query": self.data['task'],
                "threshold": self.threshold,
                "num_results": self.num_results
            }
            self.actions = self.storage.search_storage_by_threshold(params)
        except Exception as e:
            self.logger.log(f"Error loading actions: {e}", 'error')
            self.actions = {}

    def stop_execution_on_no_action(self):
        if 'failed' in self.actions:
            raise StopExecution("No actions found, stopping execution.")

    def format_actions(self):
        try:
            if 'failed' not in self.actions:
                formatted_actions = []

                for action_name, metadata in self.actions.items():
                    action_desc = metadata.get("Description", "No Description")
                    formatted_action = f"Action: {action_name}\nDescription: {action_desc}\n"
                    formatted_actions.append(formatted_action)

                self.data['action_list'] = "\n".join(formatted_actions)
        except Exception as e:
            self.logger.log(f"Error Formatting Actions:\n{self.actions}\n\nError: {e}", 'error')

    def process_data(self):
        try:
            self.stop_execution_on_no_action()
            self.parse_actions()
            self.format_actions()
        except Exception as e:
            self.logger.log(f"Error processing data: {e}", 'error')

    def parse_result(self):
        try:
            self.result = self.functions.agent_utils.parse_yaml_string(self.result)
        except Exception as e:
            self.logger.parsing_error(self.result, e)

    def build_output(self):
        try:
            selected_action = self.result['action']
            if selected_action in self.actions:
                self.output = self.actions[selected_action]
            else:
                self.output = (f"The '{selected_action}' action does not exist. It is very likely the agent did not "
                               f"correctly choose an action from the given list.")
        except Exception as e:
            self.logger.parsing_error(self.result, e)

    def parse_actions(self):
        parsed_actions = {}

        try:
            if 'failed' not in self.actions:
                for metadata in self.actions.get("metadatas", [])[0]:
                    action_name = metadata.get("Name")
                    if action_name:
                        metadata.pop('timestamp', None)
                        parsed_actions[action_name] = metadata

                self.actions = parsed_actions
        except Exception as e:
            self.logger.log(f"Error Parsing Actions:\n{self.actions}\n\nError: {e}", 'error')
            self.actions = {}

    def save_result(self):
        pass
