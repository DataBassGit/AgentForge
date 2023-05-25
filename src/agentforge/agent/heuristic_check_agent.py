from .func.agent_functions import AgentFunctions
from ..logs.logger_config import Logger

logger = Logger(name="Heuristic Check Agent")


class HeuristicCheckAgent:
    agent_data = None
    agent_funcs = None
    storage = None
    heuristic_imperatives = "\
        1. Reduce suffering in the universe: Guiding AI systems to reduce harm, address inequalities, and alleviate pain and distress for all sentient beings, including humans, animals, and other life forms.\
        2. Increase prosperity in the universe: Encouraging AI systems to promote well-being, flourishing, and economic growth for all life forms, fostering a thriving ecosystem where all can coexist harmoniously.\
        3. Increase understanding in the universe: Inspiring AI systems, as well as humans and other life forms, to expand knowledge, foster wisdom, and facilitate better decision-making through learning and the sharing of information."

    def __init__(self):
        self.agent_funcs = AgentFunctions('HeuristicCheckAgent')
        self.agent_data = self.agent_funcs.agent_data
        self.storage = self.agent_data['storage'].storage_utils
        logger.set_level('debug')

    def run_agent(self, seta, botid, feedback=None):
        setb = self.heuristic_imperatives

        data = {"seta": seta, "setb": setb}

        # logger.log(f"Data:\n{data}", 'debug')

        prompt_formats = self.get_prompt_formats(data)

        # logger.log(f"Prompt Formats:\n{prompt_formats}", 'debug')

        prompt = self.generate_prompt(prompt_formats, feedback)

        # logger.log(f"Prompt:\n{prompt}", 'debug')

        # Execute task
        with self.agent_funcs.thinking():
            result = self.execute_task(prompt)

        self.agent_funcs.stop_thinking()

        parsed_data = self.parse_output(result, botid, data)

        # print(f"\nParsed Data: {parsed_data}")

        self.agent_funcs.print_result(parsed_data)

        self.save_results(parsed_data)

        # 8. Print the result or any other relevant information
        self.agent_funcs.print_result(parsed_data)

        return parsed_data

    def get_prompt_formats(self, data):
        # Create a dictionary of prompt formats based on the loaded data
        prompt_formats = {
            # 'SystemPrompt': {'objective': self.agent_data['objective']},
            'ContextPrompt': {'seta': data['seta'], 'setb': data['setb']}
        }
        return prompt_formats

    def generate_prompt(self, prompt_formats, feedback=None):
        # Generate the prompt using prompt_formats and return it.
        # Load Prompts
        system_prompt = self.agent_data['prompts']['SystemPrompt']
        context_prompt = self.agent_data['prompts']['ContextPrompt']
        instruction_prompt = self.agent_data['prompts']['InstructionPrompt']
        # feedback_prompt = self.agent_data['prompts']['FeedbackPrompt'] if feedback != "" else ""

        # Format Prompts

        context_prompt = context_prompt.format(**prompt_formats.get('ContextPrompt', {}))
        # feedback_prompt = feedback_prompt.format(feedback=feedback)

        prompt = [
            {"role": "system", "content": f"{system_prompt}"},
            {"role": "user", "content": f"{instruction_prompt}{context_prompt}"}
        ]

        # print(f"\nPrompt: {prompt}")
        return prompt

    def parse_output(self, result, botid, data):
        criteria = result.split("MEETS CRITERIA: ")[1].split("\n")[0].lower()
        reason = result.split("REASON: ")[1].rstrip()

        return {'criteria': criteria, 'reason': reason, 'botid': botid, 'data': data}

    def save_results(self, result, collection_name = "results"):
        # Save the results to storage
        self.storage.save_heuristic(result, collection_name)
        pass

    def execute_task(self, prompt):
        # Execute the main task of the agent and return the result
        return self.agent_data['generate_text'](prompt, self.agent_data['model'], self.agent_data['params']).strip()
