from agentforge.utils.chroma_utils import ChromaUtils

storage = ChromaUtils()
print('hi')

var = storage.search_storage_by_threshold("Actions","search web", threshold=1.5)
print(var)
print("\n\n\n")
var2 = storage.peek("Actions")
print(var2)
