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
        where_map = [{key, value} for key, value in metadata_map.items()]

        results = self.storage.query_memory(collection_name=knowledge_base_name, query=query, where=where_map,
                                            num_results=number_results)

        return results

        #
        # params = {
        #     "collection_name": knowledge_base_name,
        #     "query": query,
        # }


