from agentforge.agent import Agent


class SummarizationAgent(Agent):

    def run(self, text=None, query=None):
        if query:
            return self.run_query(query)
        else:
            return self.summarize(text)

    def run_query(self, query):
        text = self.get_search_results(query)
        if text:
            return self.summarize(text)

    def get_search_results(self, query):
        params = {'collection_name': "Results", 'query': query}
        search_results = self.storage.query_memory(params, 5)['documents']

        # Rework Pending: ChromaDB updated how their collections work breaking this code,
        # it used to look at most recent items now it always looks at the first 5
        # if search_results == 'No Results!': search_results =
        # self.storage.peek(params['collection_name'])['documents']

        text = None
        if search_results != 'No Results!':
            text = "\n".join(search_results[0])

        return text

    def summarize(self, text):
        # Simply summarize the given text
        return super().run(text=text)

