def context_agent(query: str, index: str, n: int, get_ada_embedding, pinecone_index):
    query_embedding = get_ada_embedding(query)
    results = pinecone_index.query(
        query_embedding.tolist(), top_k=n, include_metadata=True
    )

    sorted_results = sorted(
        results.matches, key=lambda x: x.score, reverse=True
    )

    # print(sorted_results)
    # raise ValueError("Stopped")

    print([str(item.metadata["task"]) for item in sorted_results])
    raise ValueError("Stopped")
    return [str(item.metadata["task"]) for item in sorted_results]



# def context_agent(query: str, index: str, n: int, get_ada_embedding, pinecone_index):
#     query_embedding = get_ada_embedding(query)
#     results = pinecone_index.query(
#         query_embedding.tolist(), top_k=n, include_metadata=True
#     )
#     sorted_results = sorted(
#         results.matches, key=lambda x: x.score, reverse=True
#     )
#     return [str(item.metadata["task"]) for item in sorted_results]
