import os
from datetime import datetime
from pynput import keyboard

from .storage_interface import StorageInterface
from ..logs.logger_config import Logger

from .. import config

from termcolor import colored, cprint
from colorama import init
init(autoreset=True)

logger = Logger(name="Function Utils")


class Functions:
    mode = None
    storage = None

    def __init__(self):
        self.mode = None
        self.storage = StorageInterface()
        # Start the listener for 'Esc' key press
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

    def on_press(self, key):
        try:
            # If 'Esc' is pressed and mode is 'auto', switch to 'manual'
            if key == keyboard.Key.esc and self.mode == 'auto':
                # print("\nSwitching to Manual Mode...")
                cprint("\nSwitching to Manual Mode...", 'green', attrs=['bold'])
                self.mode = 'manual'
        except AttributeError:
            pass  # Handle a special key that we don't care about

    def set_auto_mode(self):
        # print("\nEnter Auto or Manual Mode? (a/m)")
        while True:
            user_input = input("\nEnter Auto or Manual Mode? (a/m):")
            if user_input.lower() == 'a':
                self.mode = 'auto'
                cprint(f"\nAuto Mode Set - Press 'Esc' to return to Manual Mode!", 'yellow', attrs=['bold'])
                break

            elif user_input.lower() == 'm':
                cprint(f"\nManual Mode Set.", 'green', attrs=['bold'])
                self.mode = 'manual'
                break

            else:
                cprint(f"\nPlease select a valid option!", 'red', attrs=['bold'])

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
                result = None
                completed = status['status']

                if 'not completed' in completed:
                    result = status['reason']
                    # user_input = input(f"Feedback:{feedback}\n\nSend this feedback to the execution agent? (y/n): ")
                    # if user_input.lower() == 'y':
                else:
                    result = None

                return result
            # elif self.mode == 'auto':
            #     return status

    def get_auto_mode(self):
        return self.mode

    def print_result(self, result, desc):
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
        self.write_file(log_folder, log_file, result)

    def show_tasks(self, desc):
        objective = config.persona()['Objective']
        self.storage.storage_utils.select_collection("Tasks")

        task_collection = self.storage.storage_utils.collection.get()
        task_list = task_collection["metadatas"]

        # Sort the task list by task order
        task_list.sort(key=lambda x: x["Order"])

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

        cprint(f"\n*****\n", 'blue', attrs=['bold'])

    def write_file(self, folder, file, result):
        with open(os.path.join(folder, file), "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} - TASK RESULT:\n{result}\n\n")

    def read_file(self, file_path):
        with open(file_path, 'r') as file:
            text = file.read()
        return text
