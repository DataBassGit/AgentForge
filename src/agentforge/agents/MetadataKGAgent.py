from agentforge.agent import Agent
from agentforge.utils.functions.ParsingUtils import parse_yaml_string


class MetadataKGAgent(Agent):
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
            # The 'parse_yaml_string' method takes a YAML formatted string and returns a structured object
            self.output = parse_yaml_string(self.functions.agent_utils.logger, self.result)
        except Exception as e:
            self.logger.parsing_error(self.result, e)
