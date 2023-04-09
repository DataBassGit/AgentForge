import configparser
from collections import deque
from typing import Dict
# from Agents import task_agents

from Agents.execution_agent import execution_agent
from Agents.context_agent import context_agent
from Personas.load_persona_data import load_persona_data

# Read configuration file
config = configparser.ConfigParser()
config.read('Config/config.ini')
storage_api = config.get('StorageAPI', 'library')
embedding_library = config.get('EmbeddingLibrary', 'library')

# Load Pinecone API | Discuss with Data
if storage_api == 'pinecone':
    from Utilities import pinecone_utils as storage_utils, embedding_utils
else:
    raise ValueError(f"Unsupported Storage API library: {storage_api}")

if embedding_library == 'sentence_transformers':
    pass
else:
    raise ValueError(f"Unsupported Embedding Library: {embedding_library}")


def add_task(task: Dict):
    task_list.append(task)


# Set Variables
YOUR_TABLE_NAME = storage_utils.YOUR_TABLE_NAME

# Load persona data
persona_data = load_persona_data('Personas/default.json')
PARAMS = persona_data['Params']
OBJECTIVE = persona_data['Objective']
YOUR_FIRST_TASK = persona_data['Tasks'][0]

# Initialize Pinecone
storage_utils.init_storage()

# Create Pinecone index
storage_utils.create_storage_index(storage_utils.YOUR_TABLE_NAME)

# Task list
task_list = deque([])

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
        context = context_agent(OBJECTIVE, YOUR_TABLE_NAME, 5, embedding_utils.get_ada_embedding, storage_utils.storage_index)
        result = execution_agent(OBJECTIVE, task["task_name"], context, PARAMS)
        this_task_id = int(task["task_id"])
        print(
            "\033[93m\033[1m" + "\n*****TASK RESULT*****\n" + "\033[0m\033[0m"
        )
        print(result)

        # Step 2: Enrich result and store in Pinecone
        enriched_result = {"data": result}
        # print(f"\n\n Enriched Result: {enriched_result}")

        result_id = f'result_{task["task_id"]}'
        # print(f"\n\n Result ID: {result_id}")

        vector = enriched_result["data"]
        # print(f"\n\n Vector: {vector}")

        storage_utils.storage_index.upsert(
            [
                (
                    result_id,
                    embedding_utils.get_ada_embedding(vector).tolist(),
                    {"task": task["task_name"], "result": result},
                )
            ]
        )

