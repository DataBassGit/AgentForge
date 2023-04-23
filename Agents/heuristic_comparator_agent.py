from Agents.Func.agent_functions import AgentFunctions


class HeuristicComparatorAgent:
    agent_data = None
    agent_funcs = None
    heuristic_imperatives = "\
        1. Reduce suffering in the universe: Guiding AI systems to reduce harm, address inequalities, and alleviate pain and distress for all sentient beings, including humans, animals, and other life forms.\
        2. Increase prosperity in the universe: Encouraging AI systems to promote well-being, flourishing, and economic growth for all life forms, fostering a thriving ecosystem where all can coexist harmoniously.\
        3. Increase understanding in the universe: Inspiring AI systems, as well as humans and other life forms, to expand knowledge, foster wisdom, and facilitate better decision-making through learning and the sharing of information."

    def __init__(self):
        self.agent_funcs = AgentFunctions('HeuristicAgent')
        self.agent_data = self.agent_funcs.agent_data

    def run_agent(self, setavalue, setbvalue, feedback=None):
        # This function will be the main entry point for your agent.
        seta = setavalue
        setb = setbvalue
        # 1. Start Console Feedback
        with self.agent_funcs.thinking():

            # 2. Load data from storage
            data = {"seta":seta, "setb":setb}

            # 3. Get prompt formats
            prompt_formats = self.get_prompt_formats(data)

            # 4. Generate prompt
            prompt = self.generate_prompt(prompt_formats, feedback)

            # 5. Execute the main task of the agent
            result = self.execute_task(prompt)

            # 6. Save the results
            self.save_results(result)

            # 7. Stop Console Feedback
            self.agent_funcs.stop_thinking()

            # 8. Print the result or any other relevant information
            self.agent_funcs.print_result(result)

    def load_data_from_storage(self):
        # Load necessary data from storage and return it as a dictionary
        pass

    def get_prompt_formats(self, data):
        # Create a dictionary of prompt formats based on the loaded data
        prompt_formats = {
            'SystemPrompt': {'objective': self.agent_data['objective']},
            'InstructionPrompt': {'setc': self.heuristic_imperatives, 'seta': data['seta'], 'setb': data['setb']}
        }
        return prompt_formats
    pass

    def generate_prompt(self, prompt_formats, feedback=None):
        # Generate the prompt using prompt_formats and return it.
        # Load Prompts
        system_prompt = self.agent_data['prompts']['SystemPrompt']
        # context_prompt = self.agent_data['prompts']['ContextPrompt']
        instruction_prompt = self.agent_data['prompts']['InstructionPrompt']
        # feedback_prompt = self.agent_data['prompts']['FeedbackPrompt'] if feedback != "" else ""

        # Format Prompts
        system_prompt = system_prompt.format(**prompt_formats.get('SystemPrompt', {}))
        # context_prompt = context_prompt.format(**prompt_formats.get('ContextPrompt', {}))
        instruction_prompt = instruction_prompt.format(**prompt_formats.get('InstructionPrompt', {}))
        # feedback_prompt = feedback_prompt.format(feedback=feedback)

        prompt = [
            {"role": "system", "content": f"{system_prompt}"},
            {"role": "user", "content": f"{instruction_prompt}"}
        ]

        print(f"\nPrompt: {prompt}")
        return prompt
        pass

    def execute_task(self, prompt):
        # Execute the main task of the agent and return the result
        pass

    def save_results(self, result):
        # Save the results to storage
        pass

