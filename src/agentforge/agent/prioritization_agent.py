from .agent import Agent


def calculate_next_task_order(this_task_order):
    return int(this_task_order) + 1


def order_tasks(task_list):
    filtered_results = [task for task in task_list if task['task_order'].isdigit()]

    ordered_results = [
        {'task_order': int(task['task_order']), 'task_desc': task['task_desc']}
        for task in filtered_results]

    return ordered_results


class PrioritizationAgent(Agent):
    # Additional functions
    def load_data_from_storage(self):
        collection_name = "tasks"

        task_list = self.storage.load_collection({
            'collection_name': collection_name,
            'collection_property': "documents"
        })

        this_task_order = self.storage.load_collection({
            'collection_name': collection_name,
            'collection_property': "ids"
        })[0]

        data = {
            'task_list': task_list,
            'this_task_order': this_task_order
        }

        return data

    def parse_output(self, result, bot_id, data):
        new_tasks = result.split("\n")

        task_list = []
        for task_string in new_tasks:
            task_parts = task_string.strip().split(".", 1)
            if len(task_parts) == 2:
                task_order = task_parts[0].strip()
                task_desc = task_parts[1].strip()
                task_list.append({
                    "task_order": task_order,
                    "task_desc": task_desc,
                })

        return {"tasks": task_list}
