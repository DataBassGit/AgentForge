from agentforge.agent import Agent
# from agentforge.utils.functions.TaskHandling import get_current_task


class ExecutionAgent(Agent):

    def load_additional_data(self):
        self.data['task'] = self.functions.task_handling.get_current_task()['document']
