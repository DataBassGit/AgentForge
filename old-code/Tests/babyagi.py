from agentforge.agent.TaskCreationAgent import TaskCreationAgent
from agentforge.utils.function_utils import Functions
from agentforge.utils.storage_interface import StorageInterface

storage = StorageInterface().storage_utils
functions = Functions()
functions.set_auto_mode()
reflex = None
context = None
result = None
data = None

task_creation_agent = TaskCreationAgent()

while True:
    functions.show_task_list('Salience')
    feedback = functions.get_user_input()

    data = task_creation_agent.run()
    functions.print_result(data, "Task Creation Results")


    # data = PrioritizationAgent().run() #Optional
    # functions.show_task_list('Tasks')
    # feedback = functions.check_auto_mode()
    # result = ExecutionAgent().run(feedback=feedback)
    # functions.print_result(result['result'], desc="Execution Agent")
