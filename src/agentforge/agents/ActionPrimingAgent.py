from agentforge.agent import Agent


class ActionPrimingAgent(Agent):

    def load_additional_data(self):
        try:
            self.data['task'] = self.functions.task_handling.get_current_task()['document']
        except Exception as e:
            self.logger.log(f"Error loading additional data: {e}", 'error')

    def build_output(self):
        try:
            self.output = self.functions.agent_utils.parse_yaml_string(self.result)
        except Exception as e:
            self.logger.log("It is very likely the model did not respond in the desired format", 'error')
            self.logger.log(f"Error while building output for agent: {e}", 'error')
            raise

    def save_result(self):
        pass
