from Agents.Func.agent_functions import AgentFunctions


class PrioritizationAgent:
    agent_data = None
    agent_funcs = None

    def __init__(self):
        self.agent_funcs = AgentFunctions('PrioritizationAgent')
        self.agent_data = self.agent_funcs.agent_data

    def run_prioritization_agent(self):
        self.agent_data['storage'].sel_collection("tasks")
        task_descs = self.agent_data['storage'].get_storage().get()['documents']
        this_task_order = self.agent_data['storage'].get_storage().get()['ids'][0]

        next_task_order = int(this_task_order)
        next_task_order += 1

        # Go over these prompts with Data
        prompt_formats = {
            'SystemPrompt': {'task_descs': task_descs},
            'ContextPrompt': {'objective': self.agent_data['objective']},
            'InstructionPrompt': {'next_task_order': next_task_order}
        }

        prompt = self.generate_prompt(prompt_formats)

        new_tasks = self.agent_data['generate_text'](prompt, self.agent_data['model'], self.agent_data['params']).strip().split("\n")
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

        self.save_tasks(ordered_results, task_desc_list)
        self.agent_funcs.print_task_list(ordered_results)

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

        # print(f"\nPrompt: {prompt}")
        return prompt

    def save_tasks(self, ordered_results, task_desc_list):
        col_name = "tasks"
        try:
            self.agent_data['storage'].delete_col(col_name)
            self.agent_data['storage'].create_col(col_name)
        except Exception as e:
            print("Error deleting table:", e)

        self.agent_data['storage'].save_tasks(ordered_results, task_desc_list, col_name)
