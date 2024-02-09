from agentforge.agent import Agent


class LearnKGAgent(Agent):

    def build_output(self):
        try:
            self.output = self.functions.agent_utils.parse_yaml_string(self.result)
        except Exception as e:
            self.logger.parsing_error(self.result, e)
