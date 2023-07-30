from .agent import Agent


class PrioritizationAgent(Agent):
    # Additional functions
    def load_data_from_memory(self):
        collection_name = "Tasks"

        task_list = self.storage.load_collection({
            'collection_name': collection_name,
            'include': ["documents"]
        })

        # this_task_order = self.storage.load_collection({
        #     'collection_name': collection_name,
        #     'include': ["ids"]
        # })
        #
        data = {
            'task_list': task_list['documents'],
            'this_task_order': task_list['ids'][0]
        }

        return data

    def parse_result(self, result, **kwargs):
        new_tasks = result.split("\n")

        task_list = []
        for task_string in new_tasks:
            task_parts = task_string.strip().split(".", 1)
            if len(task_parts) == 2:
                task_order = task_parts[0].strip()
                task_desc = task_parts[1].strip()
                task_list.append({
                    "Order": task_order,
                    "Description": task_desc,
                })

        return {"Tasks": task_list}
