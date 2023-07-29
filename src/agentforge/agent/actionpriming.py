from .agent import Agent, _show_task
from termcolor import cprint
from colorama import init
init(autoreset=True)


def extract_metadata(results):
    # extract the 'metadatas' key from results
    metadata_list = results['metadatas']

    # iterate over each metadata entry in the list
    # each entry is a list where the first item is the dictionary we want
    extracted_metadata = metadata_list[0][0]

    return extracted_metadata


class ActionPrimingAgent(Agent):

    # def parse_output(self, result, **kwargs):

    def load_additional_data(self, data):
        # Add 'objective' to the data
        # data['objective'] = self.agent_data.get('objective')
        # data['task'] = self.load_current_task()['task']
        tool_data = data['action']['Tools'].split(', ')

        tools = {tool: self.load_tool(tool) for tool in tool_data}

        print(tools)
        quit()
        return tools

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
