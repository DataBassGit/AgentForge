from agentforge.agent import Agent


class ActionPrimingAgent(Agent):

    def build_output(self):
        try:
            formatted_result = self.get_formatted_result()
            self.output = self.functions.string_to_dictionary(formatted_result)
        except Exception as e:
            raise ValueError(f"\n\nError while building output for agent: {e}")

    def get_formatted_result(self):
        result = self.result.replace('\n', '').replace('\t', '')
        return self.functions.extract_outermost_brackets(result)

    def load_additional_data(self):
        self.data['task'] = self.functions.get_current_task()['document']

    def save_result(self):
        pass
