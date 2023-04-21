from Agents.Func.agent_functions import AgentFunctions

class TaskCreationAgent:
    agent_data = None
    agent_funcs = None

    def __init__(self):
        self.agent_funcs = AgentFunctions('TaskCreationAgent')
        self.agent_data = self.agent_funcs.agent_data

    def run_task_creation_agent(self):
        data = self.load_data_from_storage()

        prompt_formats = self.get_prompt_formats(data)

        prompt = self.generate_prompt(prompt_formats)

        ordered_tasks = self.order_tasks(prompt)

        task_desc_list = [task['task_desc'] for task in ordered_tasks]

        self.save_tasks(ordered_tasks, task_desc_list)
        # self.agent_funcs.print_task_list(ordered_results)

    def load_data_from_storage(self):
        try:
            self.agent_data['storage'].storage_utils.select_collection("results")
            result = self.agent_data['storage'].storage_utils.get_collection().get()['documents'][0]
        except Exception as e:
            # print(f"Error loading results data: {e}")
            result = ["No results found"]

        try:
            self.agent_data['storage'].storage_utils.select_collection("tasks")
            task = self.agent_data['storage'].storage_utils.get_collection().get()['documents'][0]
            task_list = self.agent_data['storage'].storage_utils.get_collection().get()['documents']
        except Exception as e:
            # print(f"Error loading tasks data: {e}")
            task = None
            task_list = []

        return {'result': result, 'task': task, 'task_list': task_list}

    def get_prompt_formats(self, data):
        prompt_formats = {
            'SystemPrompt': {'objective': self.agent_data['objective']},
            'ContextPrompt': {'result': data['result'], 'task': data['task'], 'task_list': ', '.join(data['task_list'])}
        }
        return prompt_formats

    def generate_prompt(self, prompt_formats):
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

    def order_tasks(self, prompt):
        new_tasks = self.agent_data['generate_text'](
            prompt, self.agent_data['model'],
            self.agent_data['params']
        ).strip().split("\n")

        result = [{"task_desc": task_desc} for task_desc in new_tasks]

        filtered_results = [task for task in result if task['task_desc'] and task['task_desc'][0].isdigit()]

        order_tasks = []

        try:
            order_tasks = [
                {'task_order': int(task['task_desc'].split('. ', 1)[0]),
                 'task_desc': task['task_desc'].split('. ', 1)[1]}
                for task in filtered_results]
        except Exception as e:
            print(f"Error: {e}")

        return order_tasks

    def save_tasks(self, ordered_results, task_desc_list):
        # Note: this change seems to work, but it doesn't really stop the debug message
        col_name = "tasks"
        self.agent_data['storage'].storage_utils.clear_collection(col_name)
        self.agent_data['storage'].storage_utils.save_tasks(ordered_results, task_desc_list, col_name)
