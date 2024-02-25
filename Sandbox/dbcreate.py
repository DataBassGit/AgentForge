# from agentforge.modules.KnowledgeTraversal import KnowledgeTraversal
from agentforge.utils.storage_interface import StorageInterface

# config = Config(config_path="D:\Github\AgentForge\src")
storage = StorageInterface().storage_utils
kg_name = 'KnowledgeGraph'
params1 = {
    "collection_name": kg_name,
    "data": "dogs are animals",
    "ids": ["1"],
    "metadata": [{
        "subject": "dogs",
        "predicate": "are",
        "object": "animals"
    }]
}
params2 = {
    "collection_name": kg_name,
    "data": "dogs are animals",
    "ids": ["2"],
    "metadata": [{
        "subject": "cats",
        "predicate": "are",
        "object": "animals"
    }]
}

print("\nSaving Memory 1...\n")
storage.save_memory(params1)
print("\nSaving Memory 2...\n")
storage.save_memory(params2)
print("\nMemory saved...\n")
data = storage.peek(kg_name)
print(f"Data: {data}")
