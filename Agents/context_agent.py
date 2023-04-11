import configparser
from Utilities import embedding_utils

# Read configuration file
config = configparser.ConfigParser()
config.read('Config/config.ini')
storage_api = config.get('StorageAPI', 'library')


def context_agent(task, result, collection):

    if storage_api == 'chroma':
        results = collection.query(
            result_id=[task["task_id"]],
            tasks=[task],
            result=[result]
        )

        return results

    elif storage_api == 'pinecone':  # NEEDS REWORK
        # context = context_agent(OBJECTIVE, collection_name, 5, embedding_utils.get_ada_embedding, storage_utils.get_storage_index())
        pass
        # query_embedding = embedding_utils.get_ada_embedding(query)
        # results = pinecone_index.query(
        #     query_embedding.tolist(), top_k=n, include_metadata=True
        # )
        # sorted_results = sorted(
        #     results.matches, key=lambda x: x.score, reverse=True
        # )
        #
        # return [str(item.metadata["task"]) for item in sorted_results]
    else:
        raise ValueError(f"Unsupported Storage API library: {storage_api}")