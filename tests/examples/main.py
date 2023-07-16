from agentforge.agent.task import TaskCreationAgent
from agentforge.agent.prioritization import PrioritizationAgent
from agentforge.agent.execution import ExecutionAgent
from agentforge.utils.function_utils import Functions
from agentforge.agent.reflexion import ReflexionAgent

functions = Functions()
functions.set_auto_mode()
reflex = None
context = None
result = None
while True:
    data = TaskCreationAgent().run(result=result)
    functions.print_result(data, desc="Task Creation Agent")
    # data = PrioritizationAgent().run() #Optional
    # functions.print_result(data, desc="Prioritization Agent") #Optional
    feedback = functions.check_auto_mode()
    result = ExecutionAgent().run(feedback=feedback)
    functions.print_result(result, desc="Execution Agent")