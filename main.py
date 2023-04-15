import uuid
from collections import deque
from Agents.execution_agent import ExecutionAgent
from Agents.task_creation_agent import TaskCreationAgent
from Agents.prioritization_agent import PrioritizationAgent
from Agents.context_agent import context_agent
from Personas.load_persona_data import load_persona_data
from Utilities import function_utils as func

# Load Agents
executionAgent = ExecutionAgent()
taskCreationAgent = TaskCreationAgent()
prioritizationAgent = PrioritizationAgent()

# Load persona data
persona_data = load_persona_data('Personas/default.json')
params = persona_data['Params']
objective = persona_data['Objective']
first_task = persona_data['Tasks'][0]

# Task list
# task_list = deque([])

# first_task = {"task_id": uuid.uuid4(), "task_order": 1, "task_desc": first_task, "task_status": "pending"}
# func.add_task(task_list, first_task)

# Main loop
result = "None"
task_id_counter = 1
task = {"list_id": uuid.uuid4(), "task_order": 1, "task_desc": first_task, "task_status": "pending"}
task_list = []

# Add the first task


# create_tasks = taskCreationAgent.run_task_creation_agent(objective, ["None"], first_task, [], params)
# print(f"Task Agent: {create_tasks}")
#
# quit()

while True:
    # print(f"\nPrinting Current Tasklist: {task_list} ")
    # if len(task_list) == 0:
    #     print("\n\nStopped!")
    #     quit()
    # else:

    # Print the task list
    task_list = taskCreationAgent.run_task_creation_agent(objective, result, task, task_list, params)
    func.print_task_list(task_list)
    # print(f"Task Agent: {create_tasks}")

    task_list = prioritizationAgent.run_prioritization_agent(task["task_order"], task_list, objective, params)
    func.print_task_list(task_list)

    # print(f"Prior Agent: {task_list}")

    # task_list = deque(prioritize_tasks)

    # Step 1: Pull the first task
    # task = task_list.popleft()
    # func.print_next_task(task)
    #
    # result = executionAgent.run_execution_agent(objective, task, ["None"], params)
    # func.print_result(result)

    quit()

