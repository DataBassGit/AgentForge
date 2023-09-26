from agentforge.agent import Agent


class StatusAgent(Agent):

    def load_additional_data(self):
        self.data['task'] = self.functions.task_handling.get_current_task()['document']

    def parse_result(self):
        status = self.result.split("Status: ")[1].split("\n")[0].lower().strip()
        reason = self.result.split("Reason: ")[1].rstrip()

        task = {
            "task_id": self.data['current_task']['id'],
            "description": self.data['current_task']['metadata']['Description'],
            "status": status,
            "order": self.data['current_task']['metadata']['Order'],
        }

        # Log results
        if status == "completed":
            filename = "./Logs/results.txt"
            separator = "\n\n\n\n---\n\n\n\n"
            task_to_append = "\nTask: " + self.data['current_task']['metadata']['Description'] + "\n\n"
            text_to_append = self.data['task_result']
            with open(filename, "a") as file:
                file.write(separator + task_to_append + text_to_append)

        self.result = {
            "task": task,
            "status": status,
            "reason": reason,
        }

    def save_status(self):
        status = self.result["status"]
        task_id = self.result["task"]["task_id"]
        text = self.result["task"]["description"]
        task_order = self.result["task"]["order"]

        params = {
            'collection_name': "Tasks",
            'ids': [task_id],
            'data': [text],
            'metadata': [{"Status": status, "Description": text, "Order": task_order}]
        }

        self.storage.save_memory(params)

    def save_result(self):
        self.save_status()
