from agentforge.utils import storage_interface
# from agentforge.utils.toolselect import SemanticComparator



search = "The 'Intelligent Chunk' tool splits"
similarities = storage_interface().StorageInterface.query(search)

print(similarities)