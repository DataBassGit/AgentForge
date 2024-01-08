from agentforge.agent import Agent
import uuid


class TaskCreationAgent(Agent):

    def parse_result(self):
        # Parse the YAML content from the result
        parsed_yaml = self.functions.agent_utils.parse_yaml_string(self.result)

        if parsed_yaml is None or 'tasks' not in parsed_yaml:
            raise ValueError("No valid 'tasks' key found in the YAML content")

        tasks = parsed_yaml['tasks']

        # Create task metadata
        ordered_tasks = [{
            'Order': index + 1,  # Assuming order starts from 1
            'Description': task
        } for index, task in enumerate(tasks)]

        self.result = ordered_tasks

    def save_result(self):
        self.save_tasks(self.result)

    def save_tasks(self, task_list):
        collection_name = "Tasks"
        self.storage.delete_collection(collection_name)

        metadatas = [{
            "Status": "not completed",
            "Order": task["Order"],
            "Description": task["Description"],
            "List_ID": str(uuid.uuid4())
        } for task in task_list]

        task_orders = [str(task["Order"]) for task in task_list]
        task_desc = [task["Description"] for task in task_list]

        params = {
            "collection_name": collection_name,
            "ids": task_orders,
            "data": task_desc,
            "metadata": metadatas,
        }

        self.storage.save_memory(params)

    def build_output(self):
        pass


