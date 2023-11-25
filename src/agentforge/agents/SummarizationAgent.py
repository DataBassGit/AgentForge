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

    def build_output(self):
        try:
            parsed_yaml = self.functions.agent_utils.parse_yaml_string(self.result)
            self.output = parsed_yaml.get("summary", "").lower().strip()
        except Exception as e:
            raise ValueError(f"\n\nError while building output for agent: {e}")
