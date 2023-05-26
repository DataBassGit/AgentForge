from .agent import Agent


class HeuristicReflectionAgent(Agent):
    heuristic_imperatives = """
        1. Reduce suffering in the universe: Guiding AI systems to reduce harm, address inequalities, and alleviate pain and distress for all sentient beings, including humans, animals, and other life forms.
        2. Increase prosperity in the universe: Encouraging AI systems to promote well-being, flourishing, and economic growth for all life forms, fostering a thriving ecosystem where all can coexist harmoniously.
        3. Increase understanding in the universe: Inspiring AI systems, as well as humans and other life forms, to expand knowledge, foster wisdom, and facilitate better decision-making through learning and the sharing of information.
    """.strip()

    def __init__(self):
        super().__init__("HeuristicReflectionAgent", log_level="info")

    def parse_output(self, result, botid, data):
        # criteria = result.split("MEETS CRITERIA: ")[1].split("\n")[0].lower()
        # edit = result.split("RECOMMENDED EDIT: ")[1].split("\n")[0].lower()
        # response = result.split("RESPONSE: ")[1].strip()

        if "MEETS CRITERIA: " in result:
            criteria = result.split("MEETS CRITERIA: ")[1].split("\n")[0].lower()
        else:
            criteria = "n/a"
            # Handle the case when "RESPONSE: " is not in the result
            print("Unable to find 'MEETS CRITERIA: ' in the result string")

        if "RECOMMENDED EDIT: " in result:
            edit = result.split("RECOMMENDED EDIT: ")[1].strip()
        else:
            edit = "No recommended edits found."
            # Handle the case when "RESPONSE: " is not in the result
            print("Unable to find 'RECOMMENDED EDIT: ' in the result string")

        if "RESPONSE: " in result:
            response = result.split("RESPONSE: ")[1].strip()
        else:
            response = "No Response"
            # Handle the case when "RESPONSE: " is not in the result
            print("Unable to find 'RESPONSE: ' in the result string")

        return {'criteria': criteria, 'edit': edit, 'response': response,
                'botid': botid, 'data': data}

    def get_prompt_formats(self, data):
        return {
            'ContextPrompt': {
                'seta': data['seta'],
                'setb': data['setb'],
            },
        }

    def run_agent(self, set_a, botid, feedback=None):
        data = {
            "seta": set_a,
            "setb": self.heuristic_imperatives,
        }

        # self.logger.log(f"Data:\n{data}", 'debug')

        prompt_formats = self.get_prompt_formats(data)

        # self.logger.log(f"Prompt Formats:\n{prompt_formats}", 'debug')

        prompt = self.generate_prompt(prompt_formats, feedback)

        # self.logger.log(f"Prompt:\n{prompt}", 'debug')

        # Execute task
        with self.agent_funcs.thinking():
            result = self.execute_task(prompt)

        self.agent_funcs.stop_thinking()

        parsed_data = self.parse_output(result, botid, data)
        self.save_results(parsed_data)
        self.agent_funcs.print_result(parsed_data)
        return parsed_data
