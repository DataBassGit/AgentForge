from agentforge.agent import Agent


class ActionSelectionAgent(Agent):

    def load_additional_data(self):
        self.data['task'] = self.functions.get_current_task()['document']

    def parse_result(self):
        frustration = self.data.get('frustration', 0)
        max_threshold = 0.8
        threshold = 0.3 + frustration
        threshold = min(threshold, max_threshold)
        threshold = 0.99

        params = {
            "collection_name": 'Actions',
            "query": self.result,
            "threshold": threshold,
            "num_results": 1,  # optional
        }

        self.result = self.storage.search_storage_by_threshold(params)

    def save_result(self):
        pass
