from .agent import Agent


class StatusAgent(Agent):
    def parse_output(self, result, bot_id, data):
        status = result.split("Status: ")[1].split("\n")[0].lower().strip()
        reason = result.split("Reason: ")[1].rstrip()
        task = {
            "task_id": data['current_task']['id'],
            "description": data['current_task']['metadata']['Description'],
            "status": status,
            "order": data['current_task']['metadata']['Order'],
        }

        # Log results
        if status == "completed":
            filename = "./Logs/results.txt"
            separator = "\n\n\n\n---\n\n\n\n"
            task_to_append = "\nTask: " + data['current_task']['metadata']['Description'] + "\n\n"
            text_to_append = data['result']
            with open(filename, "a") as file:
                file.write(separator + task_to_append + text_to_append)

        return {
            "task": task,
            "status": status,
            "reason": reason,
        }

    # def load_data_from_storage(self):
    #     # Load necessary data from storage and return it as a dictionary
    #     result_collection = self.storage.load_collection({
    #         'collection_name': "Results",
    #         'include': ["documents"],
    #     })
    #     result = result_collection[0] if result_collection else ["No results found"]
    #
    #     task_collection = self.storage.load_collection({
    #         'collection_name': "Tasks",
    #         'include': ["documents"],
    #     })
    #
    #     task_list = task_collection if task_collection else []
    #     task = task_list[0] if task_collection else None
    #
    #     return {'result': result, 'task': task, 'task_list': task_list}
