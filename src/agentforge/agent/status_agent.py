from .agent import Agent


class StatusAgent(Agent):
    def __init__(self):
        super().__init__('StatusAgent', log_level="info")

    def run_status_agent(self, data):
        # This function will be the main entry point for your agent.
        self.logger.log(f"Running Agent...", 'info')
        # 1. Start Console Feedback

        task_id = data['current_task']['id']
        task_desc = data['current_task']['metadata']['task_desc']
        task_order = data['current_task']['metadata']['task_order']

        # 3. Get prompt formats
        prompt_formats = self.get_prompt_formats(data)

        # 4. Generate prompt
        prompt = self.generate_prompt(prompt_formats)
        self.logger.log(f"Prompt:\n{prompt}", 'debug')

        with self.agent_funcs.thinking():
            result = self.execute_task(prompt)

        status = result.split("Status: ")[1].split("\n")[0].lower()
        reason = result.split("Reason: ")[1].rstrip()

        print("\n")
        self.logger.log(
            f"\nCurrent Task: {task_desc}"
            f"\nCurrent Task ID: {task_id}"
            f"\nParsed Status: {status}"
            f"\nParsed Reason: {reason}",
            'info'
        )

        # For now, we always save the status
        # | We need to add a Try -Exception in Chroma Utils
        self.save_status(status, task_id, task_desc, task_order)

        self.logger.log(f"Agent Done!", 'info')
        return reason

    def load_data_from_storage(self):
        # Load necessary data from storage and return it as a dictionary
        result_collection = self.storage.load_collection({
            'collection_name': "results",
            'collection_property': "documents"
        })
        result = result_collection[0] if result_collection else ["No results found"]

        task_collection = self.storage.load_collection({
            'collection_name': "tasks",
            'collection_property': "documents"
        })

        task_list = task_collection if task_collection else []
        task = task_list[0] if task_collection else None

        return {'result': result, 'task': task, 'task_list': task_list}

    def get_prompt_formats(self, data):
        # Create a dictionary of prompt formats based on the loaded data
        prompt_formats = {
            'SystemPrompt': {'objective': self.agent_data['objective']},
            'ContextPrompt': {
                'current_task': data['current_task']['metadata']['task_desc'],
                'task_result': data['task_result'],
                'context': data['context']
            }
        }
        return prompt_formats

    def save_status(self, status, task_id, text, task_order):
        self.logger.log(
            f"\nSave Task: {text}"
            f"\nSave ID: {task_id}"
            f"\nSave Order: {task_order}"
            f"\nSave Status: {status}",
            'debug'
        )
        self.storage.save_status(status, task_id, text, task_order)
