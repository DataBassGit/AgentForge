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

    def query_knowledge(self, knowledge_base_name: str, query: str, metadata_map: dict, number_results: int = 1):
        """

        :param metadata_map:
        :type number_results: object
        :type knowledge_base_name: object
        :type query: object
        """
        knowledge_base_name = "Knowledge" if knowledge_base_name is None else knowledge_base_name

        results = self.storage.query_memory(collection_name=knowledge_base_name, query=query, num_results=1)
        print(results)

        object = results.object
        predicate = results.predicate
        subject = results.subject

        for i in metadata_map.items():
            mapping[i] = metadata_map.keys[i]

            {"object": object, "predicate": "are"}

        # results2 = self.storage.query_memory(collection_name=knowledge_base_name, query=query,
        #                                     filter_condition=metadata_map,
        #                                     num_results=number_results)

        return results

        #
        # params = {
        #     "collection_name": knowledge_base_name,
        #     "query": query,
        # }


