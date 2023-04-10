from typing import Dict


def add_task(task_list, task: Dict):
    task_list.append(task)


def print_task_list(task_list):
    # Print the task list
    print("\033[95m\033[1m" + "\n*****TASK LIST*****\n" + "\033[0m\033[0m")
    for t in task_list:
        print(str(t["task_id"]) + ": " + t["task_name"])


def print_next_task(task):
    # Print the next task
    print("\033[92m\033[1m" + "\n*****NEXT TASK*****\n" + "\033[0m\033[0m")
    print(str(task["task_id"]) + ": " + task["task_name"])


def print_result(result):
    # Print the task result
    print("\033[93m\033[1m" + "\n*****TASK RESULT*****\n" + "\033[0m\033[0m")
    print(result)