from agentforge.modules.KnowledgeTraversal import KnowledgeTraversal

if __name__ == "__main__":
    kg = KnowledgeTraversal()
    kg_name = 'KnowledgeGraph'
    search_map = {"predicate": "predicate", "subject": "subject"}
    result = kg.query_knowledge(kg_name, "What are dogs", search_map, 5)
    print(result)
