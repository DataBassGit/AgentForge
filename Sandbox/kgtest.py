from agentforge.modules.KnowledgeTraversal import KnowledgeTraversal
# from agentforge.utils.storage_interface import StorageInterface

if __name__ == "__main__":
    kg = KnowledgeTraversal()
    # storage = StorageInterface().storage_utils
    kg_name = 'knowledge_graph'
    search_map = {"predicate": "predicate", "subject": "subject"}
    result = kg.query_knowledge(kg_name, "tell me about bots.", search_map, 5)
    # data = storage.peek(kg_name)
    # print(f"Data: {data}\n\n")
    print(result)
