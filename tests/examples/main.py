from agentforge.agent.task import TaskCreationAgent
from agentforge.agent.prioritization import PrioritizationAgent
from agentforge.agent.execution import ExecutionAgent
from agentforge.utils.function_utils import Functions

functions = Functions()
functions.set_auto_mode()
while True:
    data = ExecutionAgent().run()
    functions.print_result(data)
    feedback = functions.check_auto_mode()
    data = TaskCreationAgent().run()
    functions.print_result(data)
    data = PrioritizationAgent().run()
    functions.print_result(data)


