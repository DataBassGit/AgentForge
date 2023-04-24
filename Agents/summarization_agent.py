from Agents.Func.agent_functions import AgentFunctions


class SummarizationAgent:
    agent_data = None
    agent_funcs = None

    def __init__(self):
        self.agent_funcs = AgentFunctions('SummarizationAgent')
        self.agent_data = self.agent_funcs.agent_data
        self.storage = self.agent_data['storage'].storage_utils

    def run_summarization_agent(self, text):
        # This function will be the main entry point for your agent.

        # 1. Start Console Feedback
        with self.agent_funcs.thinking():

            # 2. Get prompt formats
            prompt_formats = {'InstructionPrompt': {'text': text}}

            # 3. Generate prompt
            prompt = self.generate_prompt(prompt_formats)

            # 4. Execute the main task of the agent
            result = self.agent_funcs.run_llm(prompt)

            # 5. Stop Console Feedback
            self.agent_funcs.stop_thinking()

            # 6. Print the result or any other relevant information
            self.agent_funcs.print_result(result)

        return result

    def generate_prompt(self, prompt_formats):
        # Load Prompts
        system_prompt = self.agent_data['prompts']['SystemPrompt']
        instruction_prompt = self.agent_data['prompts']['InstructionPrompt']

        # Format Prompts
        instruction_prompt = instruction_prompt.format(**prompt_formats.get('InstructionPrompt', {}))

        prompt = [
            {"role": "system", "content": f"{system_prompt}"},
            {"role": "user", "content": f"{instruction_prompt}"}
        ]

        # print(f"\nPrompt: {prompt}")
        return prompt
