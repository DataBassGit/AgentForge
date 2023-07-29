from .agent import Agent, _show_task
from agentforge.utils.function_utils import Functions

from termcolor import cprint
from colorama import init
init(autoreset=True)


def extract_metadata(results):
    # extract the 'metadatas' key from results
    extracted_metadata = results['metadatas'][0][0]

    return extracted_metadata


class ActionPrimingAgent(Agent):
    functions = Functions()

    # def parse_output(self, result, **kwargs):

    def load_additional_data(self, data):
        # Add 'objective' to the data
        data['objective'] = self.agent_data.get('objective')
        data['task'] = self.load_current_task()['task']
        tool_data = data['action']['Tools'].split(', ')

        data['tools'] = {tool: self.load_tool(tool) for tool in tool_data}

        _show_task(data)

        print(data['tools'])

    def load_tool(self, tool):
        params = {
            "collection_name": 'Tools',
            "query": tool,
            "include": ["documents", "metadatas"]
        }

        results = self.storage.query_memory(params)
        filtered = extract_metadata(results)

        return filtered

    # def save_parsed_data(self, parsed_data):
    #     return parsed_data
