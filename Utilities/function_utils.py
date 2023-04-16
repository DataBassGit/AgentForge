class Functions:
    mode = None

    def __init__(self):
        # Add your initialization code here
        pass

    def set_auto_mode(self):
        self.mode = input("Enter Auto or Manual Mode? (a/m): ")

        if self.mode.lower() == 'a':
            self.mode = 'auto'
        else:
            self.mode = 'manual'

        print(self.mode)

    def check_auto_mode(self):
        context = None
        # Check if the mode is manual
        if self.mode == 'manual':
            user_input = input("Allow AI to continue? (y/n/auto) or enter context: ")
            if user_input.lower() == 'y':
                pass
            elif user_input.lower() == 'n':
                quit()
            elif user_input.lower() == 'auto':
                self.mode = 'auto'
            else:
                context = user_input

        return context

    def print_task_list(self, task_list):
        # Print the task list
        print("\033[95m\033[1m" + "\n*****TASK LIST*****\n" + "\033[0m\033[0m")
        for t in task_list:
            print(str(t["task_order"]) + ": " + t["task_desc"])

    def print_next_task(self, task):
        # Print the next task
        print("\033[92m\033[1m" + "\n*****NEXT TASK*****\n" + "\033[0m\033[0m")
        print(str(task["task_order"]) + ": " + task["task_desc"])

    def print_result(self, result):
        # Print the task result
        print("\033[93m\033[1m" + "\n*****TASK RESULT*****\n" + "\033[0m\033[0m")
        print(result)
