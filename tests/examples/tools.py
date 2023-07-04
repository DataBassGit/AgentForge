from agentforge.utils.storage_interface import StorageInterface

query = "The 'Intelligent Chunk' tool splits a provided text into smaller, manageable parts or 'chunks'. The user decides the size of these chunks based on their needs."

storage = StorageInterface().storage_utils

print(storage.return_embedding_function())

test_emb = storage.return_embedding(query)

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

similarities = storage.query_embedding(params)
print('')
print('Embeddings')
print(similarities)

print('')


