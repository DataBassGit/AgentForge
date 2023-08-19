from .agent import Agent, _show_task


class SummarizationAgent(Agent):

    def run(self, **kwargs):
        text = self.get_search_results(kwargs['query'])
        if text is not None:
            summary = super().run(text=text)
            return summary['Result']

    def get_search_results(self, text):
        params = {'collection_name': "Results", 'query': text}
        search_results = self.storage.query_memory(params, 5)['documents']

        if search_results == 'No Results!':
            search_results = self.storage.peek(params['collection_name'])['documents']

        text = None
        if search_results != 'No Results!':
            text = "\n".join(search_results[0])

        return text

    # def parse_output(self, **kwargs):  # Remember to incorporate bot_if and data later on
    #     response = output = kwargs['result']
    #
    #     memory = {
    #         'collection_name': "Results",
    #         'data': response,
    #     }
    #
    #     parsed_data = {
    #         'response': response,
    #         'memory': memory,
    #         'output': output
    #     }
    #
    #     return parsed_data
