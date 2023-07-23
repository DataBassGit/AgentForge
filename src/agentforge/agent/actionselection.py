from .agent import Agent, _get_data, _set_task_order, _show_task, _order_task_list
from .. import config


class ActionSelectionAgent(Agent):

    def get_completed_tasks(self):
        task_list = self.get_task_list()

        completed_tasks = [task for task in task_list["metadatas"] if task["Status"] == "completed"]

        if completed_tasks:
            # Sort tasks by order
            # completed_tasks.sort(key=lambda x: x["Order"])
            _order_task_list(completed_tasks)

            # Generate a string for the completed tasks
            task_str = "\n".join([f"{task['Order']}. {task['Description']}" for task in completed_tasks])
            return task_str
        else:
            return None

    def load_additional_data(self, data):
        # Add 'objective' to the data
        data['objective'] = self.agent_data.get('objective')
        data['task_list'] = self.get_completed_tasks()
        data['task'] = self.load_current_task()['task']

        _show_task(data)
