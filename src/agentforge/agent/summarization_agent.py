from .agent import Agent


class SummarizationAgent(Agent):
    def run(self, text):
        # This function will be the main entry point for your agent.
        self.logger.log(f"Running Agent...", 'info')

        # 2. Get prompt formats
        data = {'text': text}

        # 3. Generate prompt
        prompt = self.generate_prompt(**data)

        # 4. Execute the main task of the agent
        with self.agent_funcs.thinking():
            result = self.agent_funcs.run_llm(prompt)

        # 5. Stop Console Feedback
        self.agent_funcs.stop_thinking()

        # 6. Print the result or any other relevant information
        self.agent_funcs.print_result(result)

        self.logger.log(f"Agent Done!", 'info')
        return result
