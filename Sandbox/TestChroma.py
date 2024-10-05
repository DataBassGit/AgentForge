from agentforge.utils.ChromaUtils import ChromaUtils

storage = ChromaUtils()
print('hi')

var = storage.search_storage_by_threshold("Actions","search web", threshold=0.8, num_results=5)
print(var)
