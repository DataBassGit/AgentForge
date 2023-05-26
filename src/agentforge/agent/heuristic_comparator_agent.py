from .agent import Agent


class HeuristicComparatorAgent(Agent):
    def __init__(self):
        super().__init__("HeuristicComparatorAgent", log_level="info")

    def parse_output(self, result, botid, data):
        choice = result.split("CHOICE: ")[1].split("\n")[0].lower()
        reason = result.split("REASON: ")[1].strip()

        return {'choice': choice, 'reason': reason, 'botid': botid, 'data': data}
