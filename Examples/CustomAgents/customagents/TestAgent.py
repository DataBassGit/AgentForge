from agentforge.agent import Agent


class TestAgent(Agent):
    def save_result(self):
        pass

    def load_additional_data(self):
        self.data['task'] = self.functions.task_handling.get_current_task()['document']
