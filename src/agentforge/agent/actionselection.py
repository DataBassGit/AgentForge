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

    # def load_and_process_data(self, **kwargs):
    #
    #     objective = self.agent_data['objective']
    #     task_list = self.get_completed_tasks()
    #     task = self.load_current_task()
    #
    #     # Load data
    #     data = {}
    #     data.update(self.agent_data, **kwargs)
    #
    #     data = _get_data("task", self.load_current_task, kwargs, data)
    #     data = data.update({'objective': objective})
    #     data = data.update({'task_list': task_list})
    #
    #     data.update()
    #
    #     _show_task(data)
    #
    #     return data
    #
    # pass

