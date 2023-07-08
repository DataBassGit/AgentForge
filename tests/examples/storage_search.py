from agentforge.utils.storage_interface import StorageInterface
from scipy.spatial import distance

storage = StorageInterface().storage_utils


def search_storage_by_threshold(params, num_results=1):
    from scipy.spatial import distance

    collection_name = params.pop('collection_name', None)
    threshold = params.pop('threshold', 0.7)
    query_text = params.pop('query', None)

    query_emb = storage.return_embedding(query_text)

    params = {
        "collection_name": collection_name,
        "embeddings": query_emb,
        "include": ["embeddings", "documents", "metadatas", "distances"]
    }

    results = storage.query_memory(params, num_results)

    dist = distance.cosine(query_emb[0], results['embeddings'][0][0])

    if dist >= threshold:
        results = {'documents': f"No results found within threshold: {threshold}!\nCosine Distance: {dist}"}
    else:
        results['cosine_distance'] = dist
        results['embeddings'] = None

    return results


if __name__ == '__main__':
    # query = "What's the recipe for making a universe?"
    # query = "How can I find something online?"
    query = "I need to search something online"
    # query = "The 'GoogleSearch' tool searches the web for a specified query and retrieves a set number of results. Each result consists of a URL and a short snippet describing its contents."

    params = {
        "collection_name": 'actions',
        "query": query,
        "threshold": 0.7,  # optional
        "num_results": 1,  # optional
    }

    search = search_storage_by_threshold(params)

    print('')
    print('Query:')
    print(query)

    print('')
    print('Search:')
    # print(search)
    print(search['documents'][0][0])

    if 'cosine_distance' in search:
        print(search['cosine_distance'])
