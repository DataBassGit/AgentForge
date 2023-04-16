from typing import Dict, List
from Agents.Func.initialize_agent import set_model_api
from Agents.Func.initialize_agent import language_model_api
from Utilities.storage_interface import StorageInterface
from Personas.load_persona_data import load_persona_data

# Load persona data
persona_data = load_persona_data('Personas/default.json')
objective = persona_data['Objective']
params = persona_data['TaskCreationAgent']['Params']
system_prompt = persona_data['TaskCreationAgent']['Prompts']['SystemPrompt'].format(objective=objective)
instruction_prompt = persona_data['TaskCreationAgent']['Prompts']['InstructionPrompt']


class TaskCreationAgent:
    generate_text = None
    storage = None

    def __init__(self):
        # Add your initialization code here
        self.generate_text = set_model_api()
        self.storage = StorageInterface()

    def run_task_creation_agent(self):
        try:
            self.storage.sel_collection("results")
            result = self.storage.get_storage().get()['documents'][0]
        except:
            result = ["No results found"]
        self.storage.sel_collection("tasks")
        task = self.storage.get_storage().get()['documents'][0]
        task_list = self.storage.get_storage().get()['documents']

        context_prompt = persona_data['TaskCreationAgent']['Prompts']['ContextPrompt'].format(
            result=result,
            task=task,
            task_list=', '.join(task_list)
        )

        prompt = [
            {"role": "system",
             "content": f"{system_prompt}"},
            {"role": "user",
             "content": f"{context_prompt}"
                        f"{instruction_prompt}"},
        ]
        # print(f"\nPrompt: {prompt}")

        new_tasks = self.generate_text(prompt, params).strip().split("\n")
        # print(f"\nNew Tasks: {new_tasks}")

        result = [{"task_desc": task_desc} for task_desc in new_tasks]
        # print(f"\nResult: {result}")

        filtered_results = [task for task in result if task['task_desc'] and task['task_desc'][0].isdigit()]
        # print(f"\nFilters: {filtered_results}\n\n")

        ordered_results = []

        try:
            ordered_results = [
                {'task_order': int(task['task_desc'].split('. ', 1)[0]), 'task_desc': task['task_desc'].split('. ', 1)[1]}
                for task in filtered_results]
        except Exception as e:
            print(f"Error: {e}")

        # print(f"\nOrdered: {ordered_results}\n\n")

        return ordered_results




