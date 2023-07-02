from agentforge.agent.task import TaskCreationAgent
from agentforge.agent.prioritization import PrioritizationAgent
from agentforge.agent.execution import ExecutionAgent
from agentforge.utils.function_utils import Functions
from agentforge.agent.reflexion import ReflexionAgent

functions = Functions()
functions.set_auto_mode()
reflex = None
context = None
while True:
    data = TaskCreationAgent().run(context=context)
    functions.print_result(data, desc="Task Creation Agent")
    feedback = functions.check_auto_mode()
    # data = PrioritizationAgent().run()
    result = ExecutionAgent().run()
    functions.print_result(result, desc="Execution Agent")





