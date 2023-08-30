from .agent import Agent
import uuid


class TaskCreationAgent(Agent):

    def load_additional_data(self, data):
        if data['goal'] is None:
            data['goal'] = self.agent_data.get('objective')

    def parse_result(self, result, **kwargs):
        new_tasks = result.split("\n")

        result = [{"Description": task_desc} for task_desc in new_tasks]
        filtered_results = [task for task in result if task['Description'] and task['Description'][0].isdigit()]

        try:
            order_tasks = [{
                'Order': int(task['Description'].split('. ', 1)[0]),
                'Description': task['Description'].split('. ', 1)[1]
            } for task in filtered_results]
        except Exception as e:
            raise ValueError(f"\n\nError ordering tasks. Error: {e}")

        return order_tasks

    def save_parsed_result(self, parsed_data):
        self.save_tasks(parsed_data)

    def save_tasks(self, task_list):
        collection_name = "Tasks"
        self.storage.clear_collection(collection_name)

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

    def build_output(self, parsed_data):
        pass


