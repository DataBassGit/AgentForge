from agentforge.agent import Agent


def log_task_results(task, text_to_append):
    filename = "./Logs/results.txt"
    separator = "\n\n\n\n---\n\n\n\n"
    task_to_append = "\nTask: " + task['description'] + "\n\n"
    with open(filename, "a") as file:
        file.write(separator + task_to_append + text_to_append)


class StatusAgent(Agent):

    def load_additional_data(self):
        self.data['task'] = self.functions.task_handling.get_current_task()['document']

    def parse_result(self):
        # Parse the YAML content from the result
        parsed_yaml = self.functions.agent_utils.parse_yaml_string(self.result)

        if parsed_yaml is None:
            raise ValueError("No valid YAML content found in the result")

        status = parsed_yaml.get("status", "").lower().strip()
        reason = parsed_yaml.get("reason", "").strip()

        task = {
            "task_id": self.data['current_task']['id'],
            "description": self.data['current_task']['metadata']['Description'],
            "status": status,
            "order": self.data['current_task']['metadata']['Order'],
        }

        # Log results if the task is completed
        if status == "completed":
            log_task_results(task, self.data['task_result'])

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
