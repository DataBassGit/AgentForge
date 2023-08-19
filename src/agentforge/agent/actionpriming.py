from .agent import Agent, _show_task

import json
import ast
from termcolor import cprint
from colorama import init
init(autoreset=True)


def extract_metadata(results):
    # extract the 'metadatas' key from results
    extracted_metadata = results['metadatas'][0][0]

    return extracted_metadata


class ActionPrimingAgent(Agent):

    def build_output(self, result, **kwargs):
        formatted_result = result.replace('\n', '').replace('\t', '')
        payload = ast.literal_eval(formatted_result)

        return payload

    def load_additional_data(self, data):
        # Add 'objective' to the data
        data['objective'] = self.agent_data.get('objective')
        data['task'] = self.load_current_task()['task']

        _show_task(data)

    def load_tool(self, tool):
        params = {
            "collection_name": 'Tools',
            "query": tool,
            "include": ["documents", "metadatas"]
        }

        results = self.storage.query_memory(params)
        filtered = extract_metadata(results)

        return filtered

    def save_parsed_data(self, parsed_data):
        pass

