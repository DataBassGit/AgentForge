from .func.agent_functions import AgentFunctions
from ..logs.logger_config import Logger

logger = Logger(name="Prioritization Agent")


def calculate_next_task_order(this_task_order):
    next_task_order = int(this_task_order)
    next_task_order += 1

    return next_task_order


def order_tasks(task_list):
    filtered_results = [task for task in task_list if task['task_order'].isdigit()]

    ordered_results = [
        {'task_order': int(task['task_order']), 'task_desc': task['task_desc']}
        for task in filtered_results]

    return ordered_results


class PrioritizationAgent:
    agent_data = None
    agent_funcs = None
    storage = None

    def __init__(self):
        self.agent_funcs = AgentFunctions('PrioritizationAgent')
        self.agent_data = self.agent_funcs.agent_data
        self.storage = self.agent_data['storage'].storage_utils
        logger.set_level('debug')

    def run_prioritization_agent(self):
        logger.log(f"Running Agent...", 'info')

        data = self.load_data_from_storage()
        next_task_order = calculate_next_task_order(data['this_task_order'])
        prompt_formats = self.get_prompt_formats(data['task_list'], next_task_order)
        prompt = self.generate_prompt(prompt_formats)

        with self.agent_funcs.thinking():
            task_list = self.process_new_tasks(prompt)

        ordered_tasks = order_tasks(task_list)
        task_desc_list = [task['task_desc'] for task in ordered_tasks]

        self.save_tasks(ordered_tasks, task_desc_list)

        self.agent_funcs.stop_thinking()

        self.agent_funcs.print_task_list(ordered_tasks)

        logger.log(f"Agent Done!", 'info')
        return ordered_tasks

    # Additional functions
    def load_data_from_storage(self):
        collection_name = "tasks"

        task_list = self.storage.load_collection({
            'collection_name': collection_name,
            'collection_property': "documents"
        })

        this_task_order = self.storage.load_collection({
            'collection_name': collection_name,
            'collection_property': "ids"
        })[0]

        data = {
            'task_list': task_list,
            'this_task_order': this_task_order
        }

        return data

    def get_prompt_formats(self, task_list, next_task_order):
        prompt_formats = {
            'SystemPrompt': {'task_list': task_list},
            'ContextPrompt': {'objective': self.agent_data['objective']},
            'InstructionPrompt': {'next_task_order': next_task_order}
        }

        return prompt_formats

    def generate_prompt(self, prompt_formats, feedback=""):
        # Load Prompts
        system_prompt = self.agent_data['prompts']['SystemPrompt']
        context_prompt = self.agent_data['prompts']['ContextPrompt']
        instruction_prompt = self.agent_data['prompts']['InstructionPrompt']

        # Format Prompts
        system_prompt = system_prompt.format(**prompt_formats.get('SystemPrompt', {}))
        context_prompt = context_prompt.format(**prompt_formats.get('ContextPrompt', {}))
        instruction_prompt = instruction_prompt.format(**prompt_formats.get('InstructionPrompt', {}))

        prompt = [
            {"role": "system", "content": f"{system_prompt}"},
            {"role": "user", "content": f"{context_prompt}{instruction_prompt}"}
        ]

        logger.log(f"Prompt:\n{prompt}")
        return prompt

    def process_new_tasks(self, prompt):
        new_tasks = self.agent_data['generate_text'](
            prompt, self.agent_data['model'],
            self.agent_data['params']
        ).strip().split("\n")

        task_list = []
        for task_string in new_tasks:
            task_parts = task_string.strip().split(".", 1)
            if len(task_parts) == 2:
                task_order = task_parts[0].strip()
                task_desc = task_parts[1].strip()
                task_list.append({"task_order": task_order, "task_desc": task_desc})

        return task_list

    def save_tasks(self, ordered_results, task_desc_list):
        collection_name = "tasks"
        self.storage.clear_collection(collection_name)

        self.storage.save_tasks({
            'tasks': ordered_results,
            'results': task_desc_list,
            'collection_name': collection_name
        })
