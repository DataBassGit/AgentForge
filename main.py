import time
from collections import deque
from typing import Dict, List
from oobabooga_api import generate_text
from sentence_transformers import SentenceTransformer

import pinecone_utils
import embedding_utils
import task_agents

# Set OBJECTIVE and YOUR_FIRST_TASK
OBJECTIVE = "Write a program for an AI to use to search the internet."
YOUR_FIRST_TASK = "Develop a task list."

# Print OBJECTIVE
print("\033[96m\033[1m" + "\n*****OBJECTIVE*****\n" + "\033[0m\033[0m")
print(OBJECTIVE)

# Initialize and configure Pinecone
pinecone_utils.init_pinecone()
pinecone_utils.create_pinecone_index()

# Connect to the index
index = pinecone_utils.connect_to_index()

# Task list
task_list = deque([])

def add_task(task: Dict):
    task_list.append(task)

model = SentenceTransformer('sentence-transformers/LaBSE')

# Add the first task
first_task = {"task_id": 1, "task_name": YOUR_FIRST_TASK}

add_task(first_task)
# Main loop
task_id_counter = 1
while True:
    if task_list:
        # Print the task list
        print(
            "\033[95m\033[1m" + "\n*****TASK LIST*****\n" + "\033[0m\033[0m"
        )
        for t in task_list:
            print(str(t["task_id"]) + ": " + t["task_name"])

        # Step 1: Pull the first task
        task = task_list.popleft()
        print(
            "\033[92m\033[1m" + "\n*****NEXT TASK*****\n" + "\033[0m\033[0m"
        )
        print(str(task["task_id"]) + ": " + task["task_name"])

        # Send to execution function to complete the task based on the context
        result = task_agents.execution_agent(OBJECTIVE, task["task_name"])
        this_task_id = int(task["task_id"])
        print(
            "\033[93m\033[1m" + "\n*****TASK RESULT*****\n" + "\033[0m\033[0m"
        )
        print(result)

        # Step 2: Enrich result and store in Pinecone
        enriched_result = {"data": result}
        result_id = f'result_{task["task_id"]}'
        vector = enriched_result["data"]
        index.upsert(
            [
                (
                    result_id,
                    embedding_utils.get_ada_embedding(vector).tolist(),
                    {"task": task["task_name"], "result": result},
                )
            ]
        )

    # Step 3: Create new tasks and reprioritize task list
    new_tasks = task_agents.task_creation_agent(
        OBJECTIVE, enriched_result, task["task_name"], [t["task_name"] for t in task_list]
    )

    for new_task in new_tasks:
        task_id_counter += 1
        new_task.update({"task_id": task_id_counter})
        add_task(new_task)
    task_agents.prioritization_agent(this_task_id)

    time.sleep(1)  # Sleep before checking the task list again
