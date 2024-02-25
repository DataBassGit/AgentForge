from agentforge.modules.KnowledgeTraversal import KnowledgeTraversal


kg = KnowledgeTraversal()
kg_name = 'KnowledgeGraph'
map = {"object":"object","predicate":"predicate"}
result = kg.query_knowledge(kg_name," ",map,5)
print(result)
