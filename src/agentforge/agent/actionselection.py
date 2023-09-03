from .agent import Agent

from colorama import init
init(autoreset=True)


class ActionSelectionAgent(Agent):

    def parse_result(self):
        frustration = self.data.get('frustration', 0)
        max_threshold = 0.8
        threshold = 0.3 + frustration
        threshold = min(threshold, max_threshold)

        threshold = 0.99

        print(f'\nFrustration Threshold: {threshold}')

        params = {
            "collection_name": 'Actions',
            "query": self.result,
            "threshold": threshold,
            "num_results": 1,  # optional
        }

        self.result = self.storage.search_storage_by_threshold(params)

        # return search

    def save_result(self):
        pass
