from .agent import Agent, _get_data, _set_task_order, _show_task
from .. import config


class ActionSelectionAgent(Agent):

    def get_completed_tasks(self):
        task_list = self.get_task_list()

        completed_tasks = [task for task in task_list["metadatas"] if task["Status"] == "completed"]
        #
        # if completed_tasks
        # completed_tasks.sort(key=lambda x: x["Order"])

        result = "\n".join(f'{task["Order"]}. {task["Description"]}' for task in completed_tasks)
        return result

    def load_and_process_data(self, **kwargs):

        objective = self.agent_data['objective']
        task_list = self.get_completed_tasks()
        task = self.load_current_task()

        # Load data
        data = {}
        data.update(self.agent_data, **kwargs)

        data = data.update({'objective': objective, 'task': task})
        # data = _get_data("task", self.load_current_task, kwargs, data)

        # data.update()

        _show_task(data)

        return data

    pass

