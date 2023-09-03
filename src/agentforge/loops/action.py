from agentforge.agent.actionselection import ActionSelectionAgent
from agentforge.agent.actionpriming import ActionPrimingAgent
from agentforge.utils.function_utils import Functions
from agentforge.utils.storage_interface import StorageInterface

import importlib
from termcolor import cprint
from colorama import init
init(autoreset=True)


def dyna_tool(tool, payload):
    command = payload['command']['name']  # Hard code the command
    args = payload['command']['args']

    msg = f"agentforge.tools.{tool}"

    module = importlib.import_module(msg)
    command_func = getattr(module, command)

    result = command_func(**args)

    return result


def extract_metadata(data):
    # extract the 'metadatas' key from results
    extracted_metadata = data['metadatas'][0][0]

    return extracted_metadata


def parse_tools_data(tool_info):
    tool = '\n'.join([f'{key}: {value}' for key, value in tool_info.items()])
    return tool


class Action:
    def __init__(self):
        # Summarize the Search Results
        self.action_agent = ActionSelectionAgent()
        self.priming_agent = ActionPrimingAgent()
        self.storage = StorageInterface().storage_utils
        self.functions = Functions()

    def run(self, context, **kwargs):

        frustration = kwargs.get('frustration', 0)

        action_results = self.action_agent.run(context=context, frustration=frustration)

        if 'documents' in action_results:
            action = extract_metadata(action_results)
            selection = action['Description']
            self.functions.print_result(selection, 'Action Selection Agent')

            tool_data = action['Tools'].split(', ')
            tools = {tool: self.load_tool(tool) for tool in tool_data}

            payloads = {}
            tool_result = None
            for tool_name, tool_info in tools.items():
                tool = parse_tools_data(tool_info)
                payload = self.priming_agent.run(tool=tool, results=tool_result)

                self.functions.print_result(payload, 'Action Agent - PAYLOAD')

                tool_result = dyna_tool(tool_name.lower(), payload)

                self.functions.print_result(tool_result, 'Action Agent - TOOLS')

                # do something with payload here if needed
                payloads[tool_name] = payload

        else:
            self.functions.print_result(f'No Relevant Action Found with Frustration Level: {frustration}', 'Action Selection Agent')

    def load_tool(self, tool):
        params = {
            "collection_name": 'Tools',
            "query": tool,
            "include": ["documents", "metadatas"]
        }

        results = self.storage.query_memory(params)
        filtered = extract_metadata(results)
        filtered.pop('timestamp', None)

        return filtered



