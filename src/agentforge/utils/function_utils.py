from .functions.AgentUtils import AgentUtils
from .functions.ParsingUtils import ParsingUtils
from .functions.PromptHandling import PromptHandling
from .functions.ToolUtils import ToolUtils
from .functions.UserInterface import UserInterface
from agentforge.utils.functions.Logger import Logger


class Functions:
    """
    A class that aggregates various utility functions and classes to provide streamlined access
    to common functionalities across the application.

    This class initializes utility classes related to agent operations, prompt handling,
    tool utilities, and user interface interactions. It serves as a centralized point for accessing
    these utilities, ensuring that they are readily available throughout the application.

    Attributes:
        agent_utils (AgentUtils): An instance of the AgentUtils class for agent-related operations.
        prompt_handling (PromptHandling): An instance of the PromptHandling class for managing prompt templates and
        rendering.
        tool_utils (ToolUtils): An instance of the ToolUtils class for tool-related operations and interactions.
        user_interface (UserInterface): An instance of the UserInterface class for user interface interactions.
        logger (Logger): An instance of the Logger class for logging information and errors.
    """

    def __init__(self):
        """
        Initializes the Functions class by creating instances of utility classes and handling any exceptions
        that occur during their initialization.
        """
        # self.config = None
        self.logger = Logger(name=self.__class__.__name__)

        try:
            self.agent_utils = AgentUtils()
            self.parsing_utils = ParsingUtils()
            self.prompt_handling = PromptHandling()
            self.tool_utils = ToolUtils()
            self.user_interface = UserInterface()
        except Exception as e:
            self.logger.log(f"Error initializing Functions: {e}", 'error')
            raise
