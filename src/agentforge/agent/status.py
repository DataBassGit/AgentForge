from .agent import Agent, _set_task_order, _show_task


class StatusAgent(Agent):
    def parse_result(self, result, **kwargs):
        status = result.split("Status: ")[1].split("\n")[0].lower().strip()
        reason = result.split("Reason: ")[1].rstrip()
        task = {
            "task_id": kwargs['data']['current_task']['id'],
            "description": kwargs['data']['current_task']['metadata']['Description'],
            "status": status,
            "order": kwargs['data']['current_task']['metadata']['Order'],
        }

        # Log results
        if status == "completed":
            filename = "./Logs/results.txt"
            separator = "\n\n\n\n---\n\n\n\n"
            task_to_append = "\nTask: " + kwargs['data']['current_task']['metadata']['Description'] + "\n\n"
            text_to_append = kwargs['data']['task_result']
            with open(filename, "a") as file:
                file.write(separator + task_to_append + text_to_append)

        return {
            "task": task,
            "status": status,
            "reason": reason,
        }

    def load_additional_data(self, data):
        data['objective'] = self.agent_data.get('objective')
        data['task'] = self.load_current_task()['task']

        _show_task(data)

    def save_status(self, status, parsed_data):
        task_id = parsed_data["task"]["task_id"]
        text = parsed_data["task"]["description"]
        task_order = parsed_data["task"]["order"]

        params = {
            'collection_name': "Tasks",
            'ids': [task_id],
            'data': [text],
            'metadata': [{"Status": status, "Description": text, "Order": task_order}]
        }

        self.storage.save_memory(params)

    def get_save_operations(self, parsed_data):
        save_operations = {
            "status": (lambda status: self.save_status(status, parsed_data))
        }

        return save_operations

    def get_build_operations(self, parsed_data):
        build_operations = {
            "status": (lambda data: data)
        }

        return build_operations
