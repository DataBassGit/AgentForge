from .agent import Agent, _show_task
from termcolor import cprint
from colorama import init
init(autoreset=True)


class ActionSelectionAgent(Agent):

    def parse_result(self, result, **kwargs):  # Remember to incorporate bot_if and data later on
        frustration = kwargs['data'].get('frustration', 0)
        max_threshold = 0.8
        threshold = 0.3 + frustration
        threshold = min(threshold, max_threshold)

        print(f'\nFrustration Threshold: {threshold}')

        params = {
            "collection_name": 'Actions',
            "query": result,
            "threshold": threshold,
            "num_results": 1,  # optional
        }

        search = self.storage.search_storage_by_threshold(params)

        return search

    def load_additional_data(self, data):
        # Add 'objective' to the data
        data['objective'] = self.agent_data.get('objective')
        data['task'] = self.load_current_task()['task']

        _show_task(data)

    def save_parsed_data(self, parsed_data):
        return parsed_data
