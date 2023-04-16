from typing import Dict, List
from Agents.Func.initialize_agent import set_model_api
from Agents.Func.initialize_agent import language_model_api
from Utilities.storage_interface import StorageInterface
from Personas.load_persona_data import load_persona_data
from Utilities.function_utils import Functions

# Load persona data
persona_data = load_persona_data('Personas/default.json')
params = persona_data['PrioritizationAgent']['Params']
objective = persona_data['Objective']

#init functions
functions = Functions()


class PrioritizationAgent:
    generate_text = None
    storage = None

    def __init__(self):
        # Add your initialization code here
        self.generate_text = set_model_api()
        self.storage = StorageInterface()

    def run_prioritization_agent(self):
        # task_descs = [t["task_desc"] for t in task_list]

        self.storage.sel_collection("tasks")
        task_descs = self.storage.get_storage().get()['documents']
        this_task_order = self.storage.get_storage().get()['ids'][0]

        # print(f"\nTask Descriptions: {task_descs}")
        # print(f"This task order: {this_task_order}")

        next_task_order = int(this_task_order)
        next_task_order += 1

        system_prompt = persona_data['PrioritizationAgent']['Prompts']['SystemPrompt'].format(task_descs=task_descs)
        context_prompt = persona_data['PrioritizationAgent']['Prompts']['ContextPrompt'].format(objective=objective)
        instruction_prompt = persona_data['PrioritizationAgent']['Prompts']['InstructionPrompt'].format(
            next_task_order=next_task_order)

        prompt = [
            {"role": "system",
             "content": f"{system_prompt}"},
            {"role": "user",
             "content": f"{context_prompt}"
                        f"{instruction_prompt}"},
        ]
        # print(f"\nPrompt: {prompt}")

        new_tasks = self.generate_text(prompt, params).strip().split("\n")
        task_list = []
        for task_string in new_tasks:
            task_parts = task_string.strip().split(".", 1)
            if len(task_parts) == 2:
                task_order = task_parts[0].strip()
                task_desc = task_parts[1].strip()
                task_list.append({"task_order": task_order, "task_desc": task_desc})

        result = task_list

        # Filter tasks based on the task_order
        filtered_results = [task for task in result if task['task_order'].isdigit()]

        ordered_results = [
            {'task_order': int(task['task_order']), 'task_desc': task['task_desc']}
            for task in filtered_results]

        task_desc_list = [task['task_desc'] for task in ordered_results]

        try:
            self.storage.delete_col("tasks")
            self.storage.create_col("tasks")
        except Exception as e:
            print("Error deleting table:", e)

        self.storage.save_tasks(ordered_results, task_desc_list, "tasks")

        functions.print_task_list(ordered_results)

