from .agent import Agent


class StatusAgent(Agent):
    def parse_output(self, result, bot_id, data):
        status = result.split("Status: ")[1].split("\n")[0].lower()
        reason = result.split("Reason: ")[1].rstrip()
        task = {
            "task_id": data['current_task']['id'],
            "description": data['current_task']['metadata']['task_desc'],
            "status": status,
            "order": data['current_task']['metadata']['task_order'],
        }
        return {
            "task": task,
            "status": status,
            "reason": reason,
        }

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
