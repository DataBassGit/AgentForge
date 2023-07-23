from .agent import Agent, _show_task
from agentforge.utils.storage_interface import StorageInterface


class SummarizationAgent(Agent):

    def get_search_results(self, text):
        params = {'collection_name': "Results", 'query': text['document']}
        search_results = self.storage.query_memory(params, 5)['documents']

        if search_results == 'No Results!':
            search_results = self.storage.peek(params['collection_name'])['documents']

        text = None
        if search_results != 'No Results!':
            text = "\n".join(search_results[0])

        return text

    def run(self, **kwargs):
        text = self.get_search_results(kwargs['query'])
        if text is not None:
            summary = super().run(text=text)
            return summary['result']
