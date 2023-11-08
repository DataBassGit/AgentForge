from agentforge.agent import Agent


class TaskAgent(Agent):

    def load_agent_type_data(self):
        self.data['task'] = self.functions.task_handling.get_current_task()['document']
