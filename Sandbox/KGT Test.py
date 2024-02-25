from agentforge.utils.storage_interface import StorageInterface
from agentforge.modules.KnowledgeTraversal import KnowledgeTraversal


if __name__ == "__main__":
    kgt = KnowledgeTraversal()
    storage = StorageInterface().storage_utils

    kg_name = 'KnowledgeGraph'
    size = storage.count_collection(kg_name)

    params1 = {
        "collection_name": kg_name,
        "data": "dogs are animals",
        "ids": [str(size + 1)],
        "metadata": [{
            "subject": "dogs",
            "predicate": "are",
            "object": "animals"
        }]
    }
    params2 = {
        "collection_name": kg_name,
        "data": "cats are animals",
        "ids": [str(size + 2)],
        "metadata": [{
            "subject": "cats",
            "predicate": "are",
            "object": "animals"
        }]
    }

    storage.save_memory(**params1)
    storage.save_memory(**params2)

    data = storage.load_collection(collection_name=kg_name)
    print(data)

    # query = 'dogs are animals'
    # meta_map = {
    #     'predicate': 'predicate',
    #     'object': 'object'
    # }
    #
    # knowledge = kgt.query_knowledge(kg_name, query, meta_map, 1)


