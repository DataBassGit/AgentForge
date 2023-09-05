from agentforge.agent import Agent
import uuid


class TaskCreationAgent(Agent):

    def parse_result(self):
        new_tasks = self.result.split("\n")

        result = [{"Description": task_desc} for task_desc in new_tasks]
        filtered_results = [task for task in result if task['Description'] and task['Description'][0].isdigit()]

        try:
            ordered_tasks = [{
                'Order': int(task['Description'].split('. ', 1)[0]),
                'Description': task['Description'].split('. ', 1)[1]
            } for task in filtered_results]
        except Exception as e:
            raise ValueError(f"\n\nError ordering tasks. Error: {e}")

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


