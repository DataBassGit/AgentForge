from agentforge.agent.actionselection import ActionSelectionAgent
from agentforge.agent.actionpriming import ActionPrimingAgent
from agentforge.utils.function_utils import Functions
from agentforge.utils.storage_interface import StorageInterface

from termcolor import cprint
from colorama import init
init(autoreset=True)

def dyna_tool(tool, payload, func="run"):
    import importlib
    module = importlib.import_module(tool)
    run = getattr(module, func)
    result = run(payload)
    return result


def extract_metadata(results):
    # extract the 'metadatas' key from results
    metadata_list = results['metadatas']

    # iterate over each metadata entry in the list
    # each entry is a list where the first item is the dictionary we want
    extracted_metadata = metadata_list[0][0]

    return extracted_metadata


class Action:
    def __init__(self):
        # Summarize the Search Results
        self.action_agent = ActionSelectionAgent()
        self.priming_agent = ActionPrimingAgent()
        self.storage = StorageInterface().storage_utils
        self.functions = Functions()

        log_tasks = self.functions.show_task_list('Objectives')
        filename = "./Logs/results.txt"
        with open(filename, "a") as file:
            file.write(log_tasks)

    def run(self, context, **kwargs):
        action = self.action_agent.run(context=context)

        if 'documents' in action:
            action = action['metadatas'][0][0]
            selection = action['Description']
        else:
            selection = 'No Relevant Action Found'

        self.functions.print_result(selection, 'Action Selection Agent')

        if 'Description' in action:
            testing = self.priming_agent.run(action=action)
            self.functions.print_result(testing, 'Action Priming Agent')

    def load_tool(self, tool):
        params = {
            "collection_name": 'Tools',
            "query": tool,
            "include": ["documents", "metadatas"]
        }

        results = self.storage.query_memory(params)
        filtered = extract_metadata(results)

        return filtered



