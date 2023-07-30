from agentforge.agent.task import TaskCreationAgent
from agentforge.agent.prioritization import PrioritizationAgent
from agentforge.agent.execution import ExecutionAgent
from agentforge.utils.function_utils import Functions

functions = Functions()
functions.set_auto_mode()
reflex = None
context = None
result = None
while True:
    data = TaskCreationAgent().run(result=result)
    data = PrioritizationAgent().run() #Optional
    functions.show_task_list('Tasks')
    feedback = functions.check_auto_mode()
    result = ExecutionAgent().run(feedback=feedback)
    functions.print_result(result['result'], desc="Execution Agent")