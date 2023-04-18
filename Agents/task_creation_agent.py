from Agents.Func.agent_functions import AgentFunctions


class TaskCreationAgent:
    agent_data = None
    agent_funcs = None

    def __init__(self):
        self.agent_funcs = AgentFunctions('TaskCreationAgent')
        self.agent_data = self.agent_funcs.agent_data

    def run_task_creation_agent(self):
        try:
            self.agent_data['storage'].sel_collection("results")
            result = self.agent_data['storage'].get_storage().get()['documents'][0]
        except:
            result = ["No results found"]

        self.agent_data['storage'].sel_collection("tasks")
        task = self.agent_data['storage'].get_storage().get()['documents'][0]
        task_list = self.agent_data['storage'].get_storage().get()['documents']

        prompt_formats = {
            'SystemPrompt': {'objective': self.agent_data['objective']},
            'ContextPrompt': {'result': result, 'task': task, 'task_list': ', '.join(task_list)}
        }

        prompt = self.generate_prompt(prompt_formats)

        new_tasks = self.agent_data['generate_text'](prompt, self.agent_data['model'], self.agent_data['params']).strip().split("\n")
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
        task_desc_list = [task['task_desc'] for task in ordered_results]

        self.save_tasks(ordered_results, task_desc_list)
        # self.agent_funcs.print_task_list(ordered_results)

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
