from .agent import Agent
import uuid


class TaskCreationAgent(Agent):

    def load_additional_data(self, data):
        if data['goal'] is None:
            data['goal'] = self.agent_data.get('objective')

    # def load_data_from_memory(self, goal):
    #     print(self.agent_data)
    #
    #     result_collection = self.storage.load_collection({
    #         'collection_name': "Results",
    #         'include': ["documents"]
    #     })
    #
    #     try:
    #         result = result_collection[0] if result_collection else ["No results found"]
    #     except Exception as e:
    #         result = ["No results found"]
    #
    #     task_collection = self.storage.load_collection({
    #         'collection_name': goal,
    #         'include': ["documents"],
    #     })
    #
    #     x = 0
    #     task_list = []
    #     for task in task_collection['documents']:
    #         task_list.append(f"{x+1}. {task_collection['documents'][x]}")
    #         x += 1
    #     # print(task_list)
    #     # task_list = [task['documents'] for task in task_collection]
    #
    #     # task_list = task_collection if task_collection else []
    #     # task = task_list[0] if task_collection else None
    #
    #     return {'result': result, 'task_list': task_list}

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

    def save_parsed_data(self, parsed_data):
        self.save_tasks(parsed_data)

    def save_tasks(self, task_list, **kwargs):
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

        # ids = [str(order) for order in task_orders]

        params = {
            "collection_name": collection_name,
            "ids": task_orders,
            "data": task_desc,
            "metadata": metadatas,
        }

        self.storage.save_memory(params)

    # def save_tasks(self, ordered_results, task_desc_list):
    #     collection_name = "Tasks"
    #     self.storage.clear_collection(collection_name)
    #
    #     metadatas = [{
    #         "Status": "not completed",
    #         "Description": task["Description"],
    #         "List_ID": str(uuid.uuid4()),
    #         "Order": task["Order"]
    #     } for task in ordered_results]
    #
    #     task_orders = [task["Order"] for task in ordered_results]
    #
    #     params = {
    #         "collection_name": collection_name,
    #         "ids": [str(order) for order in task_orders],
    #         "data": task_desc_list,
    #         "metadata": metadatas,
    #     }
    #
    #     self.storage.save_memory(params)

    # def build_output(self, parsed_data):
    #     pass


