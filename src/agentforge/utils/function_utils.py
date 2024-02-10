from .functions.AgentUtils import AgentUtils
from .functions.PromptHandling import PromptHandling
from .functions.TaskHandling import TaskHandling
from .functions.ToolUtils import ToolUtils
from .functions.UserInterface import UserInterface
from agentforge.utils.functions.Logger import Logger

logger = Logger(name="Function Utils")
logger.set_level('info')


class Functions:

    def __init__(self, log_level='info'):
        self.logger = Logger(name="Function Utils")
        self.logger.set_level(log_level)

        try:
            self.agent_utils = AgentUtils()
            self.prompt_handling = PromptHandling()
            self.task_handling = TaskHandling()
            self.tool_utils = ToolUtils()
            self.user_interface = UserInterface()
        except Exception as e:
            self.logger.log(f"Error initializing storage: {e}", 'error')
            raise
