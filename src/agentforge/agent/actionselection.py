from .agent import Agent, _get_data, _set_task_order, _show_task, _order_task_list
from .. import config


class ActionSelectionAgent(Agent):

    def parse_output(self, result, bot_id, data):  # Remember to incorporate bot_if and data later on
        params = {
            "collection_name": 'Actions',
            "query": result,
            "threshold": 0.7,  # optional
            "num_results": 1,  # optional
        }

        search = self.storage.search_storage_by_threshold(params)

        return {"tools": f"{search['metadatas'][0][0]['Tools']}",
                "result": f"{search['documents'][0][0]}"}

    def load_additional_data(self, data):
        # Add 'objective' to the data
        data['objective'] = self.agent_data.get('objective')
        data['task'] = self.load_current_task()['task']

        _show_task(data)
