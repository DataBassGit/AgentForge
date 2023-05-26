from .agent import Agent


class TaskCreationAgent(Agent):
    def __init__(self, agent_name):
        super().__init__('TaskCreationAgent', log_level="info")

    def run_task_creation_agent(self):
        self.logger.log(f"Running Agent...", 'info')

        data = self.load_data_from_storage()
        prompt_formats = self.get_prompt_formats(data)
        prompt = self.generate_prompt(prompt_formats)

        with self.agent_funcs.thinking():
            ordered_tasks = self.order_tasks(prompt)

        task_desc_list = [task['task_desc'] for task in ordered_tasks]

        self.save_tasks(ordered_tasks, task_desc_list)

        self.agent_funcs.stop_thinking()

        self.agent_funcs.print_task_list(ordered_tasks)

        self.logger.log(f"Agent Done!", 'info')

    def load_data_from_storage(self):
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
        prompt_formats = {
            'SystemPrompt': {'objective': self.agent_data['objective']},
            'ContextPrompt': {
                'result': data['result'],
                'task': data['task'],
                'task_list': ', '.join(data['task_list']),
            }
        }
        return prompt_formats

    def order_tasks(self, prompt):
        new_tasks = self.agent_data['generate_text'](
            prompt, self.agent_data['model'],
            self.agent_data['params']
        ).strip().split("\n")

        result = [{"task_desc": task_desc} for task_desc in new_tasks]
        filtered_results = [task for task in result if task['task_desc'] and task['task_desc'][0].isdigit()]

        try:
            order_tasks = [{
                'task_order': int(task['task_desc'].split('. ', 1)[0]),
                'task_desc': task['task_desc'].split('. ', 1)[1]
            } for task in filtered_results]
        except Exception as e:
            raise ValueError(f"\n\nError ordering tasks. Error: {e}")

        return order_tasks

    def save_tasks(self, ordered_results, task_desc_list):
        collection_name = "tasks"
        self.storage.clear_collection(collection_name)

        self.storage.save_tasks({
            'tasks': ordered_results,
            'results': task_desc_list,
            'collection_name': collection_name
        })
