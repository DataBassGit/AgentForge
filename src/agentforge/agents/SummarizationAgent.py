from agentforge.agent import Agent


class SummarizationAgent(Agent):

    def run(self, text=None, query=None):
        try:
            if query:
                return self.run_query(query)
            else:
                return self.summarize(text)
        except Exception as e:
            self.logger.log(f"Error Running Summarization Agent: {e}", 'error')
            return None

    def run_query(self, query):
        try:
            text = self.get_search_results(query)
            if text:
                return self.summarize(text)
        except Exception as e:
            self.logger.log(f"Error running query: {e}", 'error')
            return None

    def get_search_results(self, query):
        try:
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
        except Exception as e:
            self.logger.log(f"Error fetching search results: {e}", 'error')
            return None

    def summarize(self, text):
        try:
            # Simply summarize the given text
            return super().run(text=text)
        except Exception as e:
            self.logger.log(f"Error summarizing text: {e}", 'error')
            return None

    def build_output(self):
        try:
            parsed_yaml = self.functions.agent_utils.parse_yaml_string(self.result)
            self.output = parsed_yaml.get("summary", "").lower().strip()
        except Exception as e:
            self.logger.parsing_error(self.result, e)
            self.output = self.result
