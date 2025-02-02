from agentforge.storage.chroma_storage import ChromaStorage

storage = ChromaStorage()
print('hi')

var = storage.search_storage_by_threshold("Actions","search web", threshold=0.8, num_results=5)
print(var)
