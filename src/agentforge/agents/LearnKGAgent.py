from agentforge.agent import Agent
from agentforge.utils.ParsingUtils import ParsingUtils

class LearnKGAgent(Agent):
    def build_output(self):
        """
        Overrides the build_output method from the Agent class to parse the result string into a structured format.

        This method attempts to parse the result (assumed to be in YAML format) using the agent's utility functions
        and sets the parsed output as the agent's output. If parsing fails, it logs the error using the agent's
        logger.

        Raises:
            Exception: If there's an error during parsing, it logs the error using a specialized logging method
            provided by the logger and re-raises the exception to signal failure to the calling context.
        """
        try:
            self.output = ParsingUtils().parse_yaml_content(self.result)
        except Exception as e:
            self.logger.parsing_error(self.result, e)
