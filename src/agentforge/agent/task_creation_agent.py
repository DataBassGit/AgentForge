from .agent import Agent


class TaskCreationAgent(Agent):
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

    def parse_output(self, result, bot_id, data):
        new_tasks = result.split("\n")

        result = [{"task_desc": task_desc} for task_desc in new_tasks]
        filtered_results = [task for task in result if task['task_desc'] and task['task_desc'][0].isdigit()]

        try:
            order_tasks = [{
                'task_order': int(task['task_desc'].split('. ', 1)[0]),
                'task_desc': task['task_desc'].split('. ', 1)[1]
            } for task in filtered_results]
        except Exception as e:
            raise ValueError(f"\n\nError ordering tasks. Error: {e}")

        return {"tasks": order_tasks}

