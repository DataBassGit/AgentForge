import time
from collections import deque
from typing import Dict, List
import pinecone_utils
import embedding_utils
import task_agents

# Set Variables
YOUR_TABLE_NAME = "test-table"
OBJECTIVE = "Write a program for an AI to use to search the internet."
YOUR_FIRST_TASK = "Develop a task list."
PARAMS = {
    'max_new_tokens': 200,
    'temperature': 0.5,
    'top_p': 0.9,
    'typical_p': 1,
    'n': 1,
    'stop': None,
    'do_sample': True,
    'return_prompt': False,
    'return_metadata': False,
    'typical_p': 0.95,
    'repetition_penalty': 1.05,
    'encoder_repetition_penalty': 1.0,
    'top_k': 0,
    'min_length': 0,
    'no_repeat_ngram_size': 2,
    'num_beams': 1,
    'penalty_alpha': 0,
    'length_penalty': 1.0,
    'early_stopping': False,
    'pad_token_id': None,  # Padding token ID, if required
    'eos_token_id': None,  # End-of-sentence token ID, if required
    'use_cache': True,     # Whether to use caching
    'num_return_sequences': 1,  # Number of sequences to return for each input
    'bad_words_ids': None,  # List of token IDs that should not appear in the generated text
    'seed': -1,
}

# Initialize Pinecone
pinecone_utils.init_pinecone()

# Create Pinecone index
pinecone_utils.create_pinecone_index(YOUR_TABLE_NAME)

# Task list
task_list = deque([])

def add_task(task: Dict):
    task_list.append(task)

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
        context = task_agents.context_agent(OBJECTIVE, YOUR_TABLE_NAME, 5, embedding_utils.get_ada_embedding, pinecone_utils.pinecone_index)
        result = task_agents.execution_agent(OBJECTIVE, task["task_name"], context, PARAMS)
        this_task_id = int(task["task_id"])
        print(
            "\033[93m\033[1m" + "\n*****TASK RESULT*****\n" + "\033[0m\033[0m"
        )
        print(result)

        # Step 2: Enrich result and store in Pinecone
        enriched_result = {"data": result}
        result_id = f'result_{task["task_id"]}'
        vector = enriched_result["data"]
        pinecone_utils.pinecone_index.upsert(
            [
                (
                    result_id,
                    embedding_utils.get_ada_embedding(vector).tolist(),
                    {"task": task["task_name"], "result": result},
                )
            ]
        )

    # Step 3: Create new tasks and reprioritize task list
    new_tasks = task_agents.task_creation_agent(OBJECTIVE, enriched_result, task["task_name"], [t["task_name"] for t in task_list], PARAMS)
    for new_task in new_tasks:
        task_id_counter += 1
        new_task.update({"task_id": task_id_counter})
        add_task(new_task)
    task_list = deque(task_agents.prioritization_agent(this_task_id, task_list, OBJECTIVE, PARAMS))

    time.sleep(1)  # Sleep before checking the task list again
