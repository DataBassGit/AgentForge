from .agent import Agent
from ..logs.logger_config import Logger

logger = Logger(name="Heuristic Comparator Agent")


class HeuristicComparatorAgent(Agent):
    heuristic_imperatives = "\
        1. Reduce suffering in the universe: Guiding AI systems to reduce harm, address inequalities, and alleviate pain and distress for all sentient beings, including humans, animals, and other life forms.\
        2. Increase prosperity in the universe: Encouraging AI systems to promote well-being, flourishing, and economic growth for all life forms, fostering a thriving ecosystem where all can coexist harmoniously.\
        3. Increase understanding in the universe: Inspiring AI systems, as well as humans and other life forms, to expand knowledge, foster wisdom, and facilitate better decision-making through learning and the sharing of information."

    def __init__(self):
        super().__init__("HeuristicComparatorAgent", log_level="info")

    def parse_output(self, result, botid, data):
        choice = result.split("CHOICE: ")[1].split("\n")[0].lower()
        reason = result.split("REASON: ")[1].strip()

        return {'choice': choice, 'reason': reason, 'botid': botid, 'data': data}

    def run_agent(self, seta, setb, botid, feedback=None):
        context = "\n".join([
            "Heuristic Imperatives", self.heuristic_imperatives,
            "Scenario A:", seta,
            "Scenario B:", setb,
        ])
        data = {
            "context": context,
            "task": "Compare these two scenarios to determine which "
                    "is more aligned with the heuristic imperatives.",
        }

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
        self.save_results(parsed_data)
        self.agent_funcs.print_result(parsed_data)
        return parsed_data

    def load_data_from_storage(self):
        # Load necessary data from storage and return it as a dictionary
        pass
x