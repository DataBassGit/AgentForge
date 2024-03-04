from agentforge.modules.KnowledgeTraversal import KnowledgeTraversal
from agentforge.utils.functions.Logger import Logger

logger = Logger(name="KGTest")

if __name__ == "__main__":
    kg = KnowledgeTraversal()
    kg_name = 'knowledge_graph'
    search_map = {"predicate": "predicate"}
    print(f"Metadata Map:{search_map}")

    result = kg.query_knowledge(kg_name, "llm", search_map, 3, 3)

    print(f"Agent Results: {result}")
