from .agent import Agent, _set_task_order, _show_task


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
            text_to_append = data['task_result']
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

        # Load the context data
        context_data = data.get('context') or {}
        data['context'] = context_data.get('result', None)

        _set_task_order(data)
        _show_task(data)
