from .agent import Agent


class ToolSelectionAgent(Agent):

    def run(self, **params):
        action = self.storage.storage_utils.load_collection(
            collection_name='actions',
            limit=1,
        )
        tools_used = action["metadatas"][0]['tools_used']

        tools = self.storage.storage_utils.query_memory(
            collection_name='tools',
            where={'tools_used': tools_used},
            include=['metadatas'],
        )

        for tool in tools['metadatas']:
            print(tool)
