import uuid
from Agents.execution_agent import ExecutionAgent
from Agents.task_creation_agent import TaskCreationAgent
from Agents.prioritization_agent import PrioritizationAgent
from Personas.load_persona_data import load_persona_data
from Utilities.function_utils import Functions
from Utilities.storage_interface import StorageInterface

# Load Agents
storage = StorageInterface()
executionAgent = ExecutionAgent()
taskCreationAgent = TaskCreationAgent()
prioritizationAgent = PrioritizationAgent()

# Load persona data
persona_data = load_persona_data('Personas/default.json')
first_task = persona_data['Tasks'][0]

# Main loop
result = "None"
task_id_counter = 1
task = {"list_id": uuid.uuid4(), "task_order": 1, "task_desc": first_task, "task_status": "pending"}
task_list = []

# Add a variable to set the mode
functions = Functions()
functions.set_auto_mode()

# Add a variable to store user feedback
feedback = ""

while True:
    # Create task list
    task_list = taskCreationAgent.run_task_creation_agent()
    functions.print_task_list(task_list)

    # Prioritize task list
    task_list = prioritizationAgent.run_prioritization_agent(task["task_order"], task_list)
    functions.print_task_list(task_list)

    feedback = functions.check_auto_mode()

    # Run Execution Agent
    result = executionAgent.run_execution_agent(feedback)
    functions.print_result(result)

