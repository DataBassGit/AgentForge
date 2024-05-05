from agentforge.agent import Agent


class ActionPrimingAgent(Agent):
    def build_output(self):
        """
        Overrides the build_output method from the Agent class to parse the result string into a structured format.

        This method attempts to parse the result (assumed to be in YAML format) using the agent's utility functions
        and sets the parsed output as the agent's output.

        Raises:
            Exception: If there's an error during parsing, it logs the error and re-raises the exception.
        """
        try:
            # The 'parse_yaml_string' method takes a YAML formatted string and returns a structured object
            self.output = self.functions.agent_utils.parse_yaml_string(self.result)
        except Exception as e:
            self.logger.parsing_error(self.result, e)
            raise

    def save_result(self):
        """
        Overrides the save_result method from the Agent class to provide custom behavior for saving results.

        For this custom agent, the method is intentionally left empty to bypass the default saving mechanism,
        indicating that this agent does not require saving its results in the same manner as the base Agent class.
        """
        pass
