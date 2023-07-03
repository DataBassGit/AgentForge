from agentforge.utils.storage_interface import StorageInterface

storage = StorageInterface().storage_utils

params = {
    "collection_name": 'Tools',
    "query": "The 'Intelligent Chunk' tool splits",
}

similarities = storage.query_memory(params)
print(similarities)
