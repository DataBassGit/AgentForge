from agentforge.agent import Agent


class LearnKGAgent(Agent):

    def build_output(self):
        try:
            self.output = self.functions.agent_utils.parse_yaml_string(self.result)
        except Exception as e:
            self.logger.log("It is very likely the model did not respond in the desired format", 'error')
            self.logger.log(f"Error building output: {e}", 'error')
