from .functions.AgentUtils import AgentUtils
from .functions.Parsing import Parsing
from .functions.Printing import Printing
from .functions.PromptHandling import PromptHandling
from .functions.TaskHandling import TaskHandling
from .functions.ToolUtils import ToolUtils
from .functions.UserInferface import UserInterface


class Functions:

    def __init__(self):
        self.agent_utils = AgentUtils()
        self.parsing = Parsing()
        self.printing = Printing()
        self.prompt_handling = PromptHandling()
        self.task_handling = TaskHandling()
        self.tool_utils = ToolUtils()
        self.user_interface = UserInterface()


