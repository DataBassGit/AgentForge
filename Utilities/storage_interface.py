import configparser

# Read configuration file
config = configparser.ConfigParser()
config.read('Config/config.ini')
storage_api = config.get('StorageAPI', 'library')

global storage_utils


def initialize_storage():
    global storage_utils

    if storage_api == 'chroma':
        from Utilities import chroma_utils as storage_utils

    elif storage_api == 'pinecone':  # NEEDS REWORK
        from Utilities import pinecone_utils as storage_utils

    else:
        raise ValueError(f"Unsupported Storage API library: {storage_api}")

    # Initialize Chroma
    storage_utils.init_storage()

    # Create Pinecone index
    storage_utils.create_storage()

    return storage_utils


def get_storage():
    if storage_api == 'chroma':
        return storage_utils.get_collection()

    elif storage_api == 'pinecone':  # NEEDS REWORK
        return storage_utils.get_storage_index()

    else:
        raise ValueError(f"Unsupported Storage API library: {storage_api}")


def get_result(task):
    print(f"task: {task}")

    global storage_utils
    result = storage_utils.get_collection().query(
        query_texts=[task["task_name"]],
        n_results=1
    )

    return result


def save_result(task, result):
    global storage_utils

    task_id = f'result_{task["task_id"]}'

    if storage_api == 'chroma':
        storage_utils.save_to_collection(task_id, task, result)

    elif storage_api == 'pinecone':
        from Utilities import embedding_utils
        # Enrich result and store in Pinecone | THIS FEELS LIKE IT'S COMPLETELY USELESS
        enriched_result = {"data": result}
        vector = enriched_result["data"]

        storage_utils.get_storage_index().upsert(
            [
                (
                    task_id,
                    embedding_utils.get_ada_embedding(vector).tolist(),
                    {"task": task["task_name"], "result": result},
                )
            ]
        )

    else:
        raise ValueError(f"Unsupported Storage API library: {storage_api}")
