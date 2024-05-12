from agentforge.utils.functions.Logger import Logger
from agentforge.utils.storage_interface import StorageInterface
from typing import Any, Dict


def merge_dictionaries_by_appending_unique_entries(target_dict: dict, source_dict: dict) -> dict:
    """
    Merges two dictionaries by appending non-duplicate entries from the source dictionary to the target dictionary.

    This function is specifically designed to merge entries based on unique ID values. It appends data from the source
    dictionary to the target dictionary only for those IDs that are unique to the source dictionary, ensuring there is
    no duplication of IDs and their corresponding data is properly concatenated.

    Parameters:
        - target_dict (dict): The dictionary into which data will be merged. It should follow a specific structure:
            a list containing a single list of IDs under the 'ids' key, and similar list-based structures under other
            keys.
        - source_dict (dict): The dictionary from which data will be extracted and merged into the target dictionary.
            It should follow the same structural format as the target dictionary.

    Returns:
        - dict: The updated target dictionary, now including the original data plus any unique, non-duplicated data
            from the source dictionary.

    The function iterates over the IDs and corresponding data in the source dictionary. If the data under any key is
    not None it appends the data associated with those IDs from the source dictionary to the respective keys in the
    target dictionary.

    Notes:
        - The function assumes that each 'ids' list contains unique identifiers.
        - It is presumed that the data structure under each key across both dictionaries is consistent, typically
          lists containing a single sublist of any data type.
        - The function also assumes that the order of IDs and their corresponding data points is maintained across
          all keys in both dictionaries.
    """

    target_ids_set = set(target_dict['ids'][0])
    new_ids = [id_ for id_ in source_dict['ids'][0] if id_ not in target_ids_set]

    for key, values in source_dict.items():
        if key not in target_dict:
            target_dict[key] = [[]]

        if values:
            for id_ in new_ids:
                index = source_dict['ids'][0].index(id_)
                target_dict[key][0].extend(values[0][index:index + 1])

    return target_dict


class KnowledgeTraversal:

    def __init__(self):
        """
        Initializes the KnowledgeTraversal class.

        This constructor sets up the KnowledgeTraversal instance with essential components for querying
        and logging within a knowledge base environment. It establishes a logger specific to the class
        for tracking events and interactions and initializes a storage interface for accessing the
        knowledge base.
        """
        self.logger = Logger(name=self.__class__.__name__)
        self.storage = StorageInterface().storage_utils

    def query_knowledge(self, knowledge_base_name: str, query: str, metadata_map: Dict[str, str],
                        initial_num_results: int = 1, subquery_num_results: int = 1) -> Dict[str, Any]:
        """
        Queries the knowledge base using a specified query and metadata mappings to retrieve and
        aggregate results.

        This method performs an initial query to the specified knowledge base and then conducts
        further sub-queries based on the initial results. It merges all obtained results while
        avoiding duplicates, primarily focusing on unique metadata entries.

        Parameters:
            knowledge_base_name (str): The name of the knowledge base collection to query.
            query (str): The query string to be executed against the knowledge base.
            metadata_map (Dict[str, str]): A mapping of metadata field names that dictate how the
                                           results should be filtered and merged.
            initial_num_results (int): The number of results to retrieve from the initial query.
            subquery_num_results (int): The number of results to retrieve for each sub-query based
                                        on the metadata.

        Returns:
            Dict[str, Any]: An aggregated set of query results, which includes unique entries from
                            both the initial query and all performed sub-queries.

        Raises:
            KeyError: If 'metadatas' key is not found in the initial query results, indicating an
                      issue with the expected result structure.
        """
        initial_results = self.storage.query_memory(collection_name=knowledge_base_name,
                                                    query=query,
                                                    num_results=initial_num_results)

        self.logger.log(f"Initial Results:\n{initial_results}", 'debug')

        try:
            metadatas = initial_results['metadatas'][0]
        except KeyError:
            self.logger.log(f"Metadata not found in the results:\n{initial_results}", 'error')
            return {}

        final_results = initial_results.copy()
        for metadata in metadatas:
            where_map = [{haystack: metadata.get(needle)} for haystack, needle in metadata_map.items()]

            if len(where_map) > 1:
                where_map = {"$and": where_map}
            else:
                where_map = where_map[0]

            self.logger.log(f"Collection name: {knowledge_base_name}\n"
                            f"Query: {query}\n"
                            f"Filter: {where_map}\n",
                            'debug')

            sub_results = self.storage.query_memory(collection_name=knowledge_base_name,
                                                    query=query,
                                                    filter_condition=where_map,
                                                    num_results=subquery_num_results)

            self.logger.log(f"Sub Results:\n{sub_results}", 'debug')

            final_results = merge_dictionaries_by_appending_unique_entries(final_results, sub_results)

        return final_results



