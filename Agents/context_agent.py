def context_agent(result_id, task, result, collection):
    results = collection.query(
        result_id=[result_id],
        tasks=[task],
        result=[result]
    )

    print(results)
    return results


# def context_agent(query: str, index: str, n: int, get_ada_embedding, pinecone_index):
#     query_embedding = get_ada_embedding(query)
#     results = pinecone_index.query(
#         query_embedding.tolist(), top_k=n, include_metadata=True
#     )
#     sorted_results = sorted(
#         results.matches, key=lambda x: x.score, reverse=True
#     )

    # return [str(item.metadata["task"]) for item in sorted_results]
