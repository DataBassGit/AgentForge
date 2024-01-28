from agentforge.agent import Agent
import uuid


class TaskCreationAgent(Agent):

    def parse_result(self):
        try:
            parsed_yaml = self.functions.agent_utils.parse_yaml_string(self.result)

            if parsed_yaml is None or 'tasks' not in parsed_yaml:
                self.logger.log("No valid 'tasks' key found in the YAML content", 'error')
                raise

            tasks = parsed_yaml['tasks']
            ordered_tasks = [{'Order': index + 1, 'Description': task} for index, task in enumerate(tasks)]
            self.result = ordered_tasks
        except ValueError as e:
            self.logger.log("It is very likely the model did not respond in the desired format", 'error')
            self.logger.log(f"Parsing value error: {e}", 'error')
            self.result = []
        except Exception as e:
            self.logger.log("It is very likely the model did not respond in the desired format", 'error')
            self.logger.log(f"Parsing result error: {e}", 'error')
            self.result = []

    def save_result(self):
        try:
            self.save_tasks(self.result)
        except Exception as e:
            self.logger.log(f"Error saving result: {e}", 'error')

    def save_tasks(self, task_list):
        try:
            collection_name = "Tasks"
            self.storage.delete_collection(collection_name)

            metadatas = [{"Status": "not completed",
                          "Order": task["Order"],
                          "Description": task["Description"],
                          "List_ID": str(uuid.uuid4())} for task in task_list]
            task_orders = [str(task["Order"]) for task in task_list]
            task_desc = [task["Description"] for task in task_list]

            params = {"collection_name": collection_name, "ids": task_orders, "data": task_desc, "metadata": metadatas}
            self.storage.save_memory(params)
        except Exception as e:
            self.logger.log(f"Error saving tasks: {e}", 'error')

    def build_output(self):
        pass


