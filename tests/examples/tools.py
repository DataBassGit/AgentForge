from agentforge.utils.storage_interface import StorageInterface
# from agentforge.utils.toolselect import SemanticComparator



search = "The 'Intelligent Chunk' tool splits"
storage = StorageInterface().storage_utils


peek = storage.peek('tools')

# similarities = storage.query_memory(search)

print(peek)