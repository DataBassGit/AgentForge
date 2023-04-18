from Agents.Func.agent_functions import AgentFunctions


class ExecutionAgent:
    agent_data = None
    agent_funcs = None

    def __init__(self):
        self.agent_funcs = AgentFunctions('ExecutionAgent')
        self.agent_data = self.agent_funcs.agent_data

    def run_execution_agent(self, feedback):
        self.agent_data['storage'].sel_collection("tasks")

        try:
            context = self.agent_data['storage'].get_storage().get()['documents']
        except Exception as e:
            context = []

        try:
            task = self.agent_data['storage'].get_storage().get()['documents'][0]
        except Exception as e:
            print("failed to get task:", e)
            task = self.agent_data['objective']

        prompt_formats = {
            'SystemPrompt': {'objective': self.agent_data['objective']},
            'ContextPrompt': {'context': context},
            'InstructionPrompt': {'task': task}
        }

        prompt = self.generate_prompt(prompt_formats, feedback=feedback)
        result = self.agent_data['generate_text'](prompt, self.agent_data['model'], self.agent_data['params']).strip()

        self.save_results(result)
        self.agent_funcs.print_result(result)

    def generate_prompt(self, prompt_formats, feedback=""):
        # Load Prompts
        system_prompt = self.agent_data['prompts']['SystemPrompt']
        context_prompt = self.agent_data['prompts']['ContextPrompt']
        instruction_prompt = self.agent_data['prompts']['InstructionPrompt']

        if feedback != "":
            feedback_prompt = self.agent_data['prompts']['FeedbackPrompt']
        else:
            feedback_prompt = ""

        # Format Prompts
        system_prompt = system_prompt.format(**prompt_formats.get('SystemPrompt', {}))
        context_prompt = context_prompt.format(**prompt_formats.get('ContextPrompt', {}))
        instruction_prompt = instruction_prompt.format(**prompt_formats.get('InstructionPrompt', {}))
        feedback_prompt = feedback_prompt.format(feedback=feedback)

        prompt = [
            {"role": "system", "content": f"{system_prompt}"},
            {"role": "user", "content": f"{context_prompt}{instruction_prompt}{feedback_prompt}"}
        ]

        # print(f"\nPrompt: {prompt}")
        return prompt

    def save_results(self, result):
        col_name = "results"
        try:
            self.agent_data['storage'].sel_collection(col_name)
            self.agent_data['storage'].save_results(result, col_name)
        except Exception as e:
            self.agent_data['storage'].create_col(col_name)
            self.agent_data['storage'].save_results(result, col_name)
