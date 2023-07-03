from agentforge.utils.storage_interface import StorageInterface

storage = StorageInterface().storage_utils

params = {
    "collection_name": 'tools',
    "query": "The 'Intelligent Chunk' tool splits a provided text into smaller, manageable parts or 'chunks'. The user decides the size of these chunks based on their needs.",
}

similarities = storage.query_memory(params)
print('')
print(similarities)


params = {
    "collection_name": 'actions',
    "query": "How to figure something out?",
}

similarities = storage.query_memory(params)
print('')
print(similarities)
