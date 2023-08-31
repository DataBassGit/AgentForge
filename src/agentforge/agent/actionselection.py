from .agent import Agent

from colorama import init
init(autoreset=True)


class ActionSelectionAgent(Agent):

    def parse_result(self, result, **kwargs):  # Remember to incorporate bot_if and data later on
        frustration = kwargs['data'].get('frustration', 0)
        max_threshold = 0.8
        threshold = 0.3 + frustration
        threshold = min(threshold, max_threshold)

        # threshold = 0.99

        print(f'\nFrustration Threshold: {threshold}')

        params = {
            "collection_name": 'Actions',
            "query": result,
            "threshold": threshold,
            "num_results": 1,  # optional
        }

        search = self.storage.search_storage_by_threshold(params)

        return search

    def save_parsed_result(self, parsed_data):
        pass
