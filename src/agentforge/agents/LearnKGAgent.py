from agentforge.agent import Agent


class LearnKGAgent(Agent):

    def build_output(self):
        self.output = self.functions.agent_utils.parse_yaml_string(self.result)
