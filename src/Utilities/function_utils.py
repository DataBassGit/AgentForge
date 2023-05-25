import os
import keyboard
import threading
from datetime import datetime
from Utilities.storage_interface import StorageInterface
from termcolor import colored

from Logs.logger_config import Logger

logger = Logger(name="Function Utils")

class Functions:
    mode = None
    storage = None

    # def __new__(cls):
        # cls.storage = StorageInterface()

    def __init__(self):
        self.mode = None
        self.storage = StorageInterface()
        # Start a separate thread to listen for 'Esc' key press
        self.listen_for_esc_lock = threading.Lock()
        self.listen_for_esc_thread = threading.Thread(target=self.listen_for_esc, daemon=True)
        self.listen_for_esc_thread.start()

    def listen_for_esc(self):
        while True:
            with self.listen_for_esc_lock:
                if keyboard.is_pressed('esc') and self.mode == 'auto':
                    print("\nSwitching to Manual Mode...")
                    self.mode = 'manual'
                    keyboard.read_event(suppress=True)  # Clear the event buffer

    def set_auto_mode(self):
        # print("\nEnter Auto or Manual Mode? (a/m)")
        while True:
            user_input = input("\nEnter Auto or Manual Mode? (a/m):")
            if user_input.lower() == 'a':
                self.mode = 'auto'
                print(f"\nAuto Mode Set - Press 'Esc' to return to Manual Mode!\n")
                break

            elif user_input.lower() == 'm':
                print(f"\nManual Mode Set.\n")
                self.mode = 'manual'
                break

            else:
                print("\nPlease select a valid option!\n")

    def check_auto_mode(self, feedback_from_status=None):
        context = None

        # Acquire the lock while this function is running
        with self.listen_for_esc_lock:
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
                    print(f"\nAuto Mode Set - Press 'Esc' to return to Manual Mode!\n")
                    keyboard.read_event(suppress=True)  # Clear the event buffer
                else:
                    context = user_input

        return context

    def check_status(self,status):
        if status is not None:
            user_input = input(f"\nSend this feedback to the execution agent? (y/n): {status}\n")
            if user_input.lower() == 'y':
                result = status
            else:
                result = None
            return result
    def get_auto_mode(self):
        return self.mode

    #Replace with show_tasks after hackathon
    def print_task_list(self, task_list):
        # Print the task list
        print("\033[95m\033[1m" + "\n*****TASK LIST*****\n" + "\033[0m\033[0m")
        for t in task_list:
            print(str(t["task_order"]) + ": " + t["task_desc"])

    # def print_next_task(self, task):
    #     # Print the next task
    #     print("\033[92m\033[1m" + "\n*****NEXT TASK*****\n" + "\033[0m\033[0m")
    #     print(str(task["task_order"]) + ": " + task["task_desc"])

    def print_result(self, result, desc):
        # Print the task result
        # print("\033[92m\033[1m" + "\n*****RESULT*****\n" + "\033[0m\033[0m")
        print(colored(f"\n\n***** {desc} - RESULT *****\n", 'green', attrs=['bold']))
        print(result)
        print(colored(f"\n*****\n", 'green', attrs=['bold']))
        # Save the result to a log.txt file in the /Logs/ folder
        log_folder = "Logs"
        log_file = "log.txt"

        # Create the Logs folder if it doesn't exist
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)

        # Save the result to the log file
        self.write_file(log_folder, log_file, result)

    def show_tasks(self, desc):
        self.storage.storage_utils.select_collection("tasks")

        task_collection = self.storage.storage_utils.collection.get()
        task_list = task_collection["metadatas"]

        # Sort the task list by task order
        task_list.sort(key=lambda x: x["task_order"])

        print(colored(f"\n\n***** {desc} - TASK LIST *****\n", 'magenta', attrs=['bold']))

        for task in task_list:
            task_order = task["task_order"]
            task_desc = task["task_desc"]
            task_status = task["task_status"]

            if task_status == "completed":
                status_text = colored("completed", 'green')
            else:
                status_text = colored("not completed", 'red')

            print(f"{task_order}: {task_desc} - {status_text}")

        print(colored(f"\n*****\n", 'magenta', attrs=['bold']))


    def write_file(self, folder, file, result):
        with open(os.path.join(folder, file), "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} - TASK RESULT:\n{result}\n\n")
            
    def read_file(file_path):
        with open(file_path, 'r') as file:
            text = file.read()
        return text
