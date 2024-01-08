from agentforge.utils.function_utils import Functions

class Memory:
    def __init__(self, storage):
        self.functions = Functions()
        self.agent_data = self.functions.agent_utils.load_agent_data(self.agent_name)
        self.storage = self.agent_data['storage']
    def save_memory(self, memory: str, collection: str):
        """This method saves the LLM Result to memory"""
        params = {'data': memory, 'collection_name': collection}
        self.storage.save_memory(params)
        return None
        
    def load_memory(self, collection: str, query: str):
        params = {'collection_name': collection, 'query': query}
        search_results = self.storage.query_memory(params, 5)['documents']
        return memory