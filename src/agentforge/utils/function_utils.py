from .functions.AgentUtils import AgentUtils
from .functions.PromptHandling import PromptHandling
# from .functions.TaskHandling import TaskHandling
from .functions.ToolUtils import ToolUtils
from .functions.UserInterface import UserInterface
from agentforge.utils.functions.Logger import Logger


class Functions:

    def __init__(self, ):
        self.logger = Logger(name=self.__class__.__name__)

        try:
            self.agent_utils = AgentUtils()
            self.prompt_handling = PromptHandling()
            self.tool_utils = ToolUtils()
            self.user_interface = UserInterface()
        except Exception as e:
            self.logger.log(f"Error initializing storage: {e}", 'error')
            raise
