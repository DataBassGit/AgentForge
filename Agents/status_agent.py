from Agents.Func.agent_functions import AgentFunctions


# def parse_results(text):
#     lines = text.split('\n')
#     result_dict = {}
#
#     for line in lines:
#         if line.startswith("Status:"):
#             result_dict["status"] = line.split("Status:")[1].strip().lower()
#         elif line.startswith("Reason:"):
#             result_dict["reason"] = line.split("Reason:")[1].strip()
#
#     return result_dict




class StatusAgent:
    agent_data = None
    agent_funcs = None
    storage = None

    def __init__(self):
        self.agent_funcs = AgentFunctions('StatusAgent')
        self.agent_data = self.agent_funcs.agent_data
        self.storage = self.agent_data['storage'].storage_utils

    def run_status_agent(self, data):
        # This function will be the main entry point for your agent.

        # 1. Start Console Feedback
        with self.agent_funcs.thinking():

            # 3. Get prompt formats
            prompt_formats = self.get_prompt_formats(data)

            # 4. Generate prompt
            prompt = self.generate_prompt(prompt_formats)
            print(f"\n\nStatus Prompt: {prompt}\n\n")

            result = self.execute_task(prompt)

            status = result.split("Status: ")[1].split("\n")[0]
            reason = result.split("Reason: ")[1].rstrip()

            print(f"\n\nParsed Status: {status}")
            print(f"\n\nParsed Reason: {reason}")

            if status != 'completed':
                return reason
            else:
                #self.update_task_status(task, status)
                pass


            # quit()

    def load_data_from_storage(self):
        # Load necessary data from storage and return it as a dictionary
        result_collection = self.storage.load_collection({
            'collection_name': "results",
            'collection_property': "documents"
        })
        result = result_collection[0] if result_collection else ["No results found"]

        task_collection = self.storage.load_collection({
            'collection_name': "tasks",
            'collection_property': "documents"
        })

        task_list = task_collection if task_collection else []
        task = task_list[0] if task_collection else None

        return {'result': result, 'task': task, 'task_list': task_list}
        pass

    def get_prompt_formats(self, data):
        # Create a dictionary of prompt formats based on the loaded data
        prompt_formats = {
            'SystemPrompt': {'objective': self.agent_data['objective']},
            'ContextPrompt': {
                'current_task': data['current_task'],
                'task_result': data['task_result'],
                'context': data['context']
            }
        }
        return prompt_formats
    pass

    def generate_prompt(self, prompt_formats):
        # Generate the prompt using prompt_formats and return it.
        # Load Prompts
        system_prompt = self.agent_data['prompts']['SystemPrompt']
        context_prompt = self.agent_data['prompts']['ContextPrompt']
        instruction_prompt = self.agent_data['prompts']['InstructionPrompt']
        # feedback_prompt = self.agent_data['prompts']['FeedbackPrompt'] if feedback != "" else ""

        # Format Prompts
        system_prompt = system_prompt.format(**prompt_formats.get('SystemPrompt', {}))
        context_prompt = context_prompt.format(**prompt_formats.get('ContextPrompt', {}))
        # feedback_prompt = feedback_prompt.format(feedback=feedback)

        prompt = [
            {"role": "system", "content": f"{system_prompt}"},
            {"role": "user", "content": f"{context_prompt}{instruction_prompt}"}
        ]

        # print(f"\nPrompt: {prompt}")
        return prompt
        pass

    def execute_task(self, prompt):
        return self.agent_data['generate_text'](prompt, self.agent_data['model'], self.agent_data['params']).strip()

    def update_task_status(self, status):
        self.storage.save_tasks({'result': result, 'collection_name': "results"})
        pass

