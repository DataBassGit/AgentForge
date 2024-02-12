import os
from ..storage_interface import StorageInterface
from .Logger import Logger

from termcolor import colored, cprint
from colorama import init
init(autoreset=True)


class TaskHandling:

    def __init__(self):
        self.logger = Logger(name=self.__class__.__name__)
        self.storage = StorageInterface()
        # self.config = Configs()

    def get_current_task(self):
        try:
            ordered_list = self.get_ordered_task_list()

            current_task = None
            # iterate over sorted_metadatas
            for i, metadata in enumerate(ordered_list['metadatas']):
                # check if the Task Status is not completed
                if metadata['Status'] == 'not completed':
                    current_task = {'id': ordered_list['ids'][i], 'document': ordered_list['documents'][i],
                                    'metadata': metadata}
                    break  # break the loop as soon as we find the first not_completed task

            return current_task
        except Exception as e:
            self.logger.log(f"Error in fetching current task: {e}", 'error')
            return None

    def get_ordered_task_list(self):
        try:
            # Load Tasks
            self.storage.storage_utils.select_collection("Tasks")

            task_collection = self.storage.storage_utils.load_collection({'collection_name': "Tasks",
                                                                          'include': ["documents", "metadatas"]})

            # first, pair up 'ids', 'documents' and 'metadatas' for sorting
            paired_up_tasks = list(zip(task_collection['ids'], task_collection['documents'], task_collection['metadatas']))

            # sort the paired up tasks by 'Order' in 'metadatas'
            sorted_tasks = sorted(paired_up_tasks, key=lambda x: x[2]['Order'])

            # split the sorted tasks back into separate lists
            sorted_ids, sorted_documents, sorted_metadatas = zip(*sorted_tasks)

            # create the ordered results dictionary
            ordered_list = {'ids': list(sorted_ids),
                            'embeddings': task_collection['embeddings'],
                            'documents': list(sorted_documents),
                            'metadatas': list(sorted_metadatas)}

            return ordered_list
        except Exception as e:
            self.logger.log(f"Error in fetching ordered task list: {e}", 'error')
            return {'ids': [], 'embeddings': [], 'documents': [], 'metadatas': []}

    def log_tasks(self, tasks):
        try:
            filename = "./Logs/results.txt"

            if not os.path.exists("./Logs"):
                os.makedirs("./Logs")

            with open(filename, "a") as file:
                file.write(tasks)
        except Exception as e:
            self.logger.log(f"Error in logging tasks: {e}", 'error')

    def show_task_list(self, desc):
        try:
            selected_persona = self.storage.config.data['settings']['configuration']['Persona']
            objective = self.storage.config.data['personas'][selected_persona]['Objective']
            self.storage.storage_utils.select_collection("Tasks")

            task_collection = self.storage.storage_utils.collection.get()
            task_list = task_collection["metadatas"]

            # Sort the task list by task order
            task_list.sort(key=lambda x: x["Order"])
            result = f"Objective: {objective}\n\nTasks:\n"

            cprint(f"\n***** {desc} - TASK LIST *****\nObjective: {objective}", 'blue', attrs=['bold'])

            for task in task_list:
                task_order = task["Order"]
                task_desc = task["Description"]
                task_status = task["Status"]

                if task_status == "completed":
                    status_text = colored("completed", 'green')
                else:
                    status_text = colored("not completed", 'red')

                print(f"{task_order}: {task_desc} - {status_text}")
                result = result + f"\n{task_order}: {task_desc}"

            cprint(f"*****", 'blue', attrs=['bold'])

            self.log_tasks(result)

            return result
        except Exception as e:
            self.logger.log(f"Error in showing task list: {e}", 'error')
            return ""
