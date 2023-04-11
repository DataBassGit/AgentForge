from collections import deque
from Agents.execution_agent import execution_agent
from Agents.task_creation_agent import task_creation_agent
from Agents.prioritization_agent import prioritization_agent
from Agents.context_agent import context_agent
from Personas.load_persona_data import load_persona_data
from Utilities import storage_interface as storage
from Utilities import function_utils as func

# Load Storage
storage.initialize_storage()

# Load persona data
persona_data = load_persona_data('Personas/default.json')
PARAMS = persona_data['Params']
OBJECTIVE = persona_data['Objective']
YOUR_FIRST_TASK = persona_data['Tasks'][0]

# Task list
task_list = deque([])

# Add the first task
first_task = {"task_id": 1, "task_name": YOUR_FIRST_TASK}
func.add_task(task_list, first_task)

# Main loop
result = "None"
task_id_counter = 1

while True:
    print(f"\nPrinting Current Tasklist: {task_list} ")
    if len(task_list) == 0:
        print("\n\nStopped!")
        quit()
    else:
        # Print the task list
        func.print_task_list(task_list)
        
        
        
        # Step 1: Pull the first task
        task = task_list.popleft()
        func.print_next_task(task)

        # Send to execution function to complete the task based on the context | Need to discuss what to do with agents
        # context = context_agent(task, result, storage.get_storage())
        # result = execution_agent(OBJECTIVE, task["task_name"], context, PARAMS)

        result = execution_agent(OBJECTIVE, task["task_name"], ["None"], PARAMS)
        func.print_result(result)

        this_task_id = int(task["task_id"])

        try:
            storage.save_result(task, result)

        except Exception as e:
            print("Error during upsert:", e)
        
        create_tasks = task_creation_agent(OBJECTIVE, result, task["task_name"], task, PARAMS)
        
        #debug
        #print(create_tasks)
        
        try:
            storage.save_result(task, create_tasks)

        except Exception as e:
            print("Error during upsert:", e)
            
        prioritize_tasks = prioritization_agent(task["task_id"], task_list, OBJECTIVE, PARAMS)
        
        #debug
        print(prioritize_tasks)
        task_list = deque(prioritize_tasks)
        
        try:
            
            storage.save_result(task, prioritize_tasks)
            
        except Exception as e:
            print("Error during upsert:", e)
        
        
        #print(storage.get_result(task))