from agentforge.utils.storage_interface import StorageInterface
from scipy.spatial import distance
from sklearn.metrics.pairwise import cosine_distances

# query = "How do I cook a potatoe?"
query = "Lesbians do not eat potatoes"
# query = "takes a query string and a number of results as inputs."

storage = StorageInterface().storage_utils

print(storage.return_embedding_function())

test_emb = storage.return_embedding([query])

params = {
    "collection_name": 'tools',
    "query": query,
}

similarities = storage.query_memory(params)
print('')
print('Text')
print(similarities)


params = {
    "collection_name": 'tools',
    "embeddings": test_emb,
}

similarities2 = storage.return_embedding(query)
print('')
print('Embeddings')
print(similarities2)

# print('')
# distance2 = cosine_distances(similarities2[0])
# print(distance2)

print('')
distance2 = distance.cosine(similarities2[0], similarities['embeddings'][0][0])
print(distance2)


# print('')
# print('Embeddings2')
# print(similarities['embeddings'][0][0])

# storage.return_embedding(params)