from agentforge.utils.functions.Logger import Logger
from agentforge.utils.storage_interface import StorageInterface
from collections import Counter


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

        results = self.storage.query_memory(collection_name=knowledge_base_name, query=query, num_results=2)
        print(f"Initial Results:\n{results}")

        try:
            #metadatas = results['metadatas'][0][0]
            metadatas = results['metadatas'][0]
            print(f"Metadatas: {metadatas}")
        except:
            return ""

        # results3 = {}
        # results3 = self.merge_dictionaries(results, results3)

        for metadata in metadatas:
            print(f"Metadata:{metadata}")
            where_map = [{haystack: metadata.get(needle)} for haystack, needle in metadata_map.items()]


            count = len(where_map)
            if count > 1:
                where_map = {"$and": [where_map]}
            else:
                where_map = where_map[0]

            print(f"\nQuery:\n\nCollection name:{knowledge_base_name}\nQuery: {query}\nFilter:{where_map}\n")
            results2 = self.storage.query_memory(collection_name=knowledge_base_name, query=query,
                                                 filter_condition=where_map,
                                                 num_results=number_results)
            print(f"Secondary Results:\n{results2}")
            results3 = self.merge_dictionaries(results2,results)

        return results3

    @staticmethod
    def merge_dictionaries(dict1, dict2):
        """
        Merges two dictionaries with the same structure into a single dictionary.

        Args:
        - dict1 (dict): The first dictionary.
        - dict2 (dict): The second dictionary, to be merged with the first.

        Returns:
        - dict: The merged dictionary.
        """
        merged_dict = {}

        # Assuming dict1 and dict2 have the same structure
        for key in dict1:
            if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                # If the value is a dictionary, merge it recursively
                merged_dict[key] = merge_dictionaries(dict1[key], dict2[key])
            else:
                # If not a dictionary, just take the value from the second dictionary
                # This assumes we want to prioritize values in dict2 when there's a conflict
                merged_dict[key] = dict2[key]

        return merged_dict

        #
        # params = {
        #     "collection_name": knowledge_base_name,
        #     "query": query,
        # }
