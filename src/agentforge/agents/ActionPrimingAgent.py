from agentforge.agent_types.TaskAgent import TaskAgent


class ActionPrimingAgent(TaskAgent):

    def build_output(self):
        try:
            formatted_result = self.get_formatted_result()
            self.output = self.functions.parsing.string_to_dictionary(formatted_result)
        except Exception as e:
            raise ValueError(f"\n\nError while building output for agent: {e}")

    def get_formatted_result(self):
        result = self.result.replace('\n', '').replace('\t', '')
        return self.functions.parsing.extract_outermost_brackets(result)

    def save_result(self):
        pass
