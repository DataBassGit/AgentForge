from agentforge.modules.KnowledgeTraversal import KnowledgeTraversal
from agentforge.utils.Logger import Logger

logger = Logger(name="KGTest")

if __name__ == "__main__":
    kg = KnowledgeTraversal()
    kg_name = 'knowledge_graph'
    query = "llm"
    search_map = {"predicate": "predicate"}
    print(f"Metadata Map:{search_map}")

    # result = kg.query_knowledge(kg_name, "llm", search_map, 3, 3)
    result = kg.query_knowledge(knowledge_base_name=kg_name,
                                query=query,
                                metadata_map=search_map,
                                initial_num_results=3,
                                subquery_num_results=3)

    print(f"Agent Results: {result}")
