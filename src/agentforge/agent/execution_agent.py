from .agent import Agent


class ExecutionAgent(Agent):

    def __init__(self):
        super().__init__('ExecutionAgent', log_level='info')

    def run_execution_agent(self, context, feedback):
        self.logger.log(f"Running Agent...", 'info')
        self.logger.log(f"Context:{context}", 'info')

        task = self.load_data_from_memory()
        data = {'task': task, 'context': context}
        self.logger.log(f"Data:\n{data}", 'debug')

        prompt_formats = self.get_prompt_formats(data)
        self.logger.log(f"Execution Agent Prompt: {prompt_formats}\n"
                   f"Feedback: {feedback}", "debug")
        prompt = self.generate_prompt(prompt_formats, feedback, context)
        with self.agent_funcs.thinking():
            result = self.execute_task(prompt)

        self.save_results(result)
        self.agent_funcs.stop_thinking()
        self.agent_funcs.print_result(result)

        self.logger.log(f"Agent Done!", 'info')
        return result

    def load_data_from_memory(self):
        task_list = self.storage.load_collection({
            'collection_name': "tasks",
            'collection_property': "documents"
        })
        task = task_list[0]
        return {'task': task}
