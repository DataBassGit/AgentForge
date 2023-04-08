import configparser
import time
from collections import deque
from typing import Dict, List
import task_agents

# Read configuration file
config = configparser.ConfigParser()
config.read('config.ini')
language_model_api = config.get('LanguageModelAPI', 'library')
storage_api = config.get('StorageAPI', 'library')
embedding_library = config.get('EmbeddingLibrary', 'library')

if language_model_api == 'oobabooga_api':
    from oobabooga_api import generate_text
elif language_model_api == 'openai_api':
    from openai_api import generate_text
else:
    raise ValueError(f"Unsupported Language Model API library: {language_model_api}")

if storage_api == 'pinecone':
    import pinecone_utils as storage_utils
else:
    raise ValueError(f"Unsupported Storage API library: {storage_api}")

if embedding_library == 'sentence_transformers':
    import embedding_utils
else:
    raise ValueError(f"Unsupported Embedding Library: {embedding_library}")



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
storage_utils.init_storage()

# Create Pinecone index
storage_utils.create_storage_index(YOUR_TABLE_NAME)

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
        context = task_agents.context_agent(OBJECTIVE, YOUR_TABLE_NAME, 5, embedding_utils.get_ada_embedding, storage_utils.storage_index)
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
        storage_utils.storage_index.upsert(
            [
                (
                    result_id,
                    embedding_utils.get_ada_embedding(vector).tolist(),
                    {"task": task["task_name"], "result": result},
                )
            ]
        )
       