from agentforge.agent import Agent


class StatusAgent(Agent):

    def load_additional_data(self):
        try:
            self.data['task'] = self.functions.task_handling.get_current_task()['document']
        except Exception as e:
            self.logger.log(f"Error building output: {e}", 'error')

    def log_task_results(self, task, text_to_append):
        try:
            filename = "./Logs/results.txt"
            separator = "\n\n\n\n---\n\n\n\n"
            task_to_append = "\nTask: " + task['description'] + "\n\n"
            with open(filename, "a") as file:
                file.write(separator + task_to_append + text_to_append)
        except Exception as e:
            self.logger.log(f"Error logging task results: {e}", 'error')

    def parse_result(self):
        try:
            # Parse the YAML content from the result
            parsed_yaml = self.functions.agent_utils.parse_yaml_string(self.result)

            if parsed_yaml is None:
                self.logger.log("No valid YAML content found in the result:", 'error')
                raise

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
                self.log_task_results(task, self.data['task_result'])

            self.result = {
                "task": task,
                "status": status,
                "reason": reason,
            }
        except ValueError as e:
            self.logger.log('Parsing Value Error', 'warning')
            self.logger.parsing_error(self.result, e)
            self.result = {}
        except Exception as e:
            self.logger.parsing_error(self.result, e)
            self.result = {}

    def save_status(self):
        try:
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
        except Exception as e:
            self.logger.log(f"Error in saving status: {e}", 'error')

    def save_result(self):
        try:
            self.save_status()
        except Exception as e:
            self.logger.log(f"Error saving result: {e}", 'error')
