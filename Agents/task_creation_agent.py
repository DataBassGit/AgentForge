from typing import Dict, List
from Agents.Func.initialize_agent import set_model_api
from Agents.Func.initialize_agent import language_model_api
from Utilities.storage_interface import StorageInterface


class TaskCreationAgent:
    generate_text = None
    storage = None

    def __init__(self):
        # Add your initialization code here
        self.generate_text = set_model_api()
        self.storage = StorageInterface()

    def run_task_creation_agent(self, objective: str, result: Dict, task: [], task_list: List[str], params: Dict):
        if language_model_api == 'openai_api':
            prompt = [
                {"role": "system",
                 "content": f"You are a task creation AI that uses the result of an execution agent to create new tasks with the following objective: {objective}, "},
                {"role": "user",
                 "content": f"The last completed task has the result: {result}. This result was based on this task description: {task['task_desc']}. "
                            f"These are incomplete tasks: {', '.join(task_list)}. "
                            f"Based on the result, create new tasks to be completed by the AI system that do not overlap with incomplete tasks. Return the tasks as an array"},
            ]

        else:
            print('\nLanguage Model Not Found!')
            raise ValueError('Language model not found. Please check the language_model_api variable.')

        new_tasks = self.generate_text(prompt, params).strip().split("\n")
        # print(f"\nNew Tasks: {new_tasks}")

        result = [{"task_desc": task_desc} for task_desc in new_tasks]
        # print(f"\nResult: {result}")

        filtered_results = [task for task in result if task['task_desc'] and task['task_desc'][0].isdigit()]
        # print(f"\nFilters: {filtered_results}\n\n")

        ordered_results = [
            {'task_order': int(task['task_desc'].split('. ', 1)[0]), 'task_desc': task['task_desc'].split('. ', 1)[1]}
            for task in filtered_results]

        print(f"\nOrdered: {ordered_results}\n\n")

        # quit()

        # try:
        #     self.storage.save_result(task, result)
        #
        # except Exception as e:
        #     print("Error during upsert:", e)

        # print(self.storage.get_result(task))

        return ordered_results




