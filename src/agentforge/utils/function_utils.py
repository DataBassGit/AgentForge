import os
from datetime import datetime
from pynput import keyboard
from typing import Dict, Any

from .storage_interface import StorageInterface
from ..logs.logger_config import Logger

from .. import config
from ..config import Config

from termcolor import colored, cprint
from colorama import init

init(autoreset=True)

logger = Logger(name="Function Utils")


class Functions:
    mode = None
    storage = None

    def __init__(self):
        self.mode = 'manual'
        self.config = Config()
        self.storage = StorageInterface()

        # Start the listener for 'Esc' key press
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

    def check_auto_mode(self, feedback_from_status=None):
        context = None

        # Check if the mode is manual
        if self.mode == 'manual':
            user_input = input("\nAllow AI to continue? (y/n/auto) or provide feedback: ")
            if user_input.lower() == 'y':
                context = feedback_from_status
                pass
            elif user_input.lower() == 'n':
                quit()
            elif user_input.lower() == 'auto':
                self.mode = 'auto'
                cprint(f"\nAuto Mode Set - Press 'Esc' to return to Manual Mode!", 'yellow', attrs=['bold'])
            else:
                context = user_input

        return context

    def check_status(self, status):
        if status is not None:
            if self.mode != 'auto':
                completed = status['status']

                if 'not completed' in completed:
                    result = status['reason']
                else:
                    result = None

                return result

    def get_auto_mode(self):
        return self.mode

    def get_current_task(self):
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

    def get_ordered_task_list(self):
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

    def get_task_list(self):
        return self.storage.storage_utils.load_collection({'collection_name': "Tasks",
                                                           'include': ["documents", "metadatas"]})

    def load_agent_data(self, agent_name):
        self.config.load()
        persona_data = self.config.persona  # Load persona data
        defaults = persona_data['Defaults']

        agent = self.config.agents[agent_name]
        api = agent.get('API', defaults['API'])
        params = agent.get('Params', defaults['Params'])

        # Initialize agent data
        agent_data: Dict[str, Any] = dict(
            name=agent_name,
            llm=self.config.get_llm(api, agent_name),
            objective=persona_data['Objective'],
            prompts=agent['Prompts'],
            params=params,
            storage=StorageInterface().storage_utils,
        )

        return agent_data

    def on_press(self, key):
        try:
            # If 'Esc' is pressed and mode is 'auto', switch to 'manual'
            if key == keyboard.Key.esc and self.mode == 'auto':
                cprint("\nSwitching to Manual Mode...", 'green', attrs=['bold'])
                self.mode = 'manual'
        except AttributeError:
            pass  # Handle a special key that we don't care about

    def prepare_objective(self):
        while True:
            user_input = input("\nDefine Objective (leave empty to use defaults):")
            if user_input.lower() == '':
                return None
            else:
                self.config.persona['Objective'] = user_input
                return user_input

    def show_task_list(self, desc):
        objective = self.config.persona['Objective']
        self.storage.storage_utils.select_collection("Tasks")

        task_collection = self.storage.storage_utils.collection.get()
        task_list = task_collection["metadatas"]

        # Sort the task list by task order
        task_list.sort(key=lambda x: x["Order"])
        result = f"Objective: {objective}\n\nTasks:\n"

        cprint(f"\n***** {desc} - TASK LIST *****\n\nObjective: {objective}", 'blue', attrs=['bold'])

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

        cprint(f"\n*****\n", 'blue', attrs=['bold'])

        self.log_tasks(result)

        return result

    @staticmethod
    def calculate_next_task_order(this_task_order):
        return int(this_task_order) + 1

    @staticmethod
    def handle_prompt_type(prompts, prompt_type):
        """Handle each type of prompt and return template and vars."""
        prompt_data = prompts.get(prompt_type, {})
        if prompt_data:
            return [(prompt_data['template'], prompt_data['vars'])]
        return []

    @staticmethod
    def log_tasks(tasks):
        filename = "./Logs/results.txt"
        with open(filename, "a") as file:
            file.write(tasks)

    @staticmethod
    def print_result(result, desc):
        # Print the task result
        cprint(f"***** {desc} - RESULT *****\n", 'green', attrs=['bold'])
        print(result)
        cprint(f"\n*****", 'green', attrs=['bold'])

        # Save the result to a log.txt file in the /Logs/ folder
        log_folder = "Logs"
        log_file = "log.txt"

        # Create the Logs folder if it doesn't exist
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)

        # Save the result to the log file
        # self.write_file(log_folder, log_file, result)

    @staticmethod
    def read_file(file_path):
        with open(file_path, 'r') as file:
            text = file.read()
        return text

    @staticmethod
    def remove_prompt_if_none(prompts, kwargs):
        prompts_copy = prompts.copy()
        for prompt_type, prompt_data in prompts_copy.items():
            required_vars = prompt_data.get('vars', [])
            # If there are no required vars or all vars are empty, we keep the prompt
            if not required_vars or all(not var for var in required_vars):
                continue
            for var in required_vars:
                if kwargs.get(var) is None:
                    prompts.pop(prompt_type)
                    break  # Exit this loop, the dictionary has been changed

    @staticmethod
    def render_template(template, variables, data):
        temp = template.format(
            **{k: v for k, v in data.items() if k in variables}
        )

        return temp

    @staticmethod
    def set_task_order(data):
        task_order = data.get('this_task_order')
        if task_order is not None:
            data['next_task_order'] = Functions.calculate_next_task_order(task_order)

    @staticmethod
    def show_task(data):
        if 'task' in data:
            cprint(f'\nTask: {data["task"]}', 'green', attrs=['dark'])

    @staticmethod
    def write_file(folder, file, result):
        with open(os.path.join(folder, file), "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} - TASK RESULT:\n{result}\n\n")
