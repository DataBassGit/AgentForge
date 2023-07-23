from .agent import Agent, _show_task
from agentforge.utils.storage_interface import StorageInterface


class SummarizationAgent(Agent):
    def __init__(self):
        super().__init__()
        self.storage = StorageInterface().storage_utils

    def load_additional_data(self, data):
        # Add 'objective' to the data
        data['objective'] = self.agent_data.get('objective')
        data['task'] = self.load_current_task()['task']

        _show_task(data)

    def get_search_results(self, text):
        params = {'collection_name': "Results", 'query': text['document']}
        search_results = self.storage.query_memory(params, 5)['documents']

        if search_results == 'No Results!':
            search_results = self.storage.peek(params['collection_name'])['documents']

        text = None
        if search_results != 'No Results!':
            text = "\n".join(search_results[0])

        return text

    # def run(self, text):
    #     text = self.get_search_results(text)
    #     summary = super().run(text=text)
    #
    #     result = summary['result']
    #
    #     return result
