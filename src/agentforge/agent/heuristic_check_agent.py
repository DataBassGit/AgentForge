from .agent import Agent


class HeuristicCheckAgent(Agent):
    def __init__(self):
        super().__init__("HeuristicCheckAgent", log_level="info")

    def parse_output(self, result, botid, data):
        criteria = result.split("MEETS CRITERIA: ")[1].split("\n")[0].lower()
        reason = result.split("REASON: ")[1].rstrip()

        return {'criteria': criteria, 'reason': reason, 'botid': botid, 'data': data}
