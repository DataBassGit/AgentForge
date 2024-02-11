from agentforge.agent import Agent


class ExecutionAgent(Agent):

    def load_additional_data(self):
        try:
            self.data['objective'] = self.agent_data['persona'].get('Objective', None)
            self.data['task'] = self.functions.task_handling.get_current_task()['document']
        except Exception as e:
            self.logger.log(f"Error loading additional data: {e}", 'error')

# # Test Agent
# if __name__ == '__main__':
#     exe = ExecutionAgent()
#     objective = "Build a space sandwich"
#     summary = ""
#     context = ""
#     feedback = ""
#     task = ""
#     result = exe.run(objective=objective, summary=summary, context=context, feedback=feedback, task=task)
#     print(result)
