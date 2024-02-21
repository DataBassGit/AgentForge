from agentforge.utils.functions.Logger import Logger
from agentforge.utils.storage_interface import StorageInterface
from agentforge.config import Config


class KnowledgeTraversal:

    def __init__(self):
        """
        Initializes the KGTraversal class with its required components.
        """
        self.logger = Logger(name=self.__class__.__name__)
        self.storage = StorageInterface().storage_utils

    def query_knowledge(self, knowledge_base_name, query, metadata_map, number_results):
        params = {
            "collection_name": knowledge_base_name,
            "query": query,
        }

        results = self.storage.query_memory(params, number_results)

        return results

        #
        # params = {
        #     "collection_name": knowledge_base_name,
        #     "query": query,
        # }


if __name__ == "__main__":
    config = Config(config_path="D:\Github\AgentForge\src")
    storage = StorageInterface().storage_utils
    kg_name = 'KnowledgeGraph'
    params1 = {
        "collection_name": kg_name,
        "data": "dogs are animals",
        "ids": [1],
        "metadata": [{
            "subject": "dogs",
            "predicate": "are",
            "object": "animals"
        }]
    }
    params2 = {
        "collection_name": kg_name,
        "data": "dogs are animals",
        "ids": [1],
        "metadata": [{
            "subject": "cats",
            "predicate": "are",
            "object": "animals"
        }]
    }

    storage.save_memory(params1)
    storage.save_memory(params2)

    data = storage.load_collection(kg_name)
    print(data)


