from typing import Dict, List
from Agents.Func.initialize_agent import set_model_api
from Agents.Func.initialize_agent import language_model_api
from Utilities.storage_interface import StorageInterface


class PrioritizationAgent:
    generate_text = None
    storage = None

    def __init__(self):
        # Add your initialization code here
        self.generate_text = set_model_api()
        self.storage = StorageInterface()

    def run_prioritization_agent(self, this_task_order: int, task_list: List, objective: str, params: Dict):
        task_descs = [t["task_desc"] for t in task_list]
        # print("\n***This Task ID***: " + this_task_id)
        next_task_order = int(this_task_order)
        next_task_order += 1

        prompt = ""

        if language_model_api == 'openai_api':
            prompt = [
                {"role": "system",
                 "content": f"You are a task prioritization AI tasked with cleaning the formatting of and reprioritizing the following tasks: {task_descs}. "},
                {"role": "user",
                 "content": f"Consider the ultimate objective of your team: {objective}. Do not remove any tasks. Return the result as a numbered list, like:\n"
                            f"#. First task\n"
                            f"#. Second task\n"
                            f"Start the task list with number {next_task_order}."},
            ]

        else:
            print('\nLanguage Model Not Found!')
            raise ValueError('Language model not found. Please check the language_model_api variable.')

        new_tasks = self.generate_text(prompt, params).strip().split("\n")
        task_list = []
        for task_string in new_tasks:
            task_parts = task_string.strip().split(".", 1)
            if len(task_parts) == 2:
                task_order = task_parts[0].strip()
                task_desc = task_parts[1].strip()
                task_list.append({"task_order": task_order, "task_desc": task_desc})

        print(f"\n\nPrior: {task_list}")
        # quit()

        result = task_list
        print(f"\nResult: {result}")

        # Filter tasks based on the task_order
        filtered_results = [task for task in result if task['task_order'].isdigit()]
        # print(f"\nFilters: {filtered_results}\n\n")

        ordered_results = [
            {'task_order': int(task['task_order']), 'task_desc': task['task_desc']}
            for task in filtered_results]

        task_desc_list = [task['task_desc'] for task in ordered_results]

        try:
            self.storage.sel_collection("tasks")
            self.storage.save_results(ordered_results, task_desc_list)
        except Exception as e:
            print("Error during upsert:", e, "\nCreating table... Name: tasks")
            self.storage.create_collection("tasks")
            self.storage.save_results(ordered_results, task_desc_list)

        return task_list
