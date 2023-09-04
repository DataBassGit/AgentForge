from agentforge.agent import Agent
from ast import literal_eval as eval


class ActionPrimingAgent(Agent):

    def build_output(self):
        try:
            formatted_result = self.result.replace('\n', '').replace('\t', '')
            self.output = eval(formatted_result)
        except Exception as e:
            self.logger.log(self.result, 'error')
            raise ValueError(f"\n\nError while building output for agent: {e}")

    def load_additional_data(self):
        self.data['task'] = self.functions.get_current_task()['document']

    def save_result(self):
        pass
