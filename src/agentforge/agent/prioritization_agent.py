from .agent import Agent


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


class PrioritizationAgent(Agent):
    def __init__(self):
        super().__init__("PrioritizationAgent", log_level="info")

    def run(self):
        self.logger.log(f"Running Agent...", 'info')

        data = self.load_data_from_storage()
        data['next_task_order'] = calculate_next_task_order(data['this_task_order'])
        prompt_formats = self.get_prompt_formats(data)
        prompt = self.generate_prompt(prompt_formats)

        with self.agent_funcs.thinking():
            task_list = self.process_new_tasks(prompt)

        ordered_tasks = order_tasks(task_list)
        task_desc_list = [task['task_desc'] for task in ordered_tasks]

        self.save_tasks(ordered_tasks, task_desc_list)

        self.agent_funcs.stop_thinking()

        self.agent_funcs.print_task_list(ordered_tasks)

        self.logger.log(f"Agent Done!", 'info')
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

    def get_prompt_formats(self, data):
        prompt_formats = {
            'SystemPrompt': {'task_list': data["task_list"]},
            'ContextPrompt': {'objective': self.agent_data['objective']},
            'InstructionPrompt': {'next_task_order': data["next_task_order"]}
        }

        return prompt_formats

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
