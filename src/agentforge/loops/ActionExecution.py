from agentforge.agents.ActionPrimingAgent import ActionPrimingAgent
from agentforge.utils.function_utils import Functions
from agentforge.utils.storage_interface import StorageInterface


def parse_tools_data(tool_info):
    tool_name = tool_info.pop('Name')
    tool = f"Tool: {tool_name}\n" + '\n'.join([f'{key}: {value}' for key, value in tool_info.items()])
    return tool


class Action:
    def __init__(self):
        self.storage = StorageInterface().storage_utils
        self.functions = Functions()
        self.priming_agent = ActionPrimingAgent()
        self.action = {}
        self.tools = {}
        self.results = {}

    def run(self, action):
        if action:
            self.action = action
            self.load_action_tools()
            self.run_tools_in_sequence()
            self.save_action_results()
            return self.results

    def load_action_tools(self):
        tool_data = self.action['Tools'].split(', ')
        self.tools = {tool: self.load_tool(tool) for tool in tool_data}

    def run_tools_in_sequence(self):
        tool_result = None
        for tool_name, tool_info in self.tools.items():
            tool_script = tool_info.pop('Script')
            tool = parse_tools_data(tool_info)
            payload = self.priming_agent.run(tool=tool, results=tool_result)
            self.functions.print_primed_tool(tool_name, payload)

            tool_result = self.functions.dyna_tool(tool_script, payload)
            self.results[tool_name] = tool_result

    def save_action_results(self):
        for key, result in self.results.items():
            params = {'data': [result], 'collection_name': 'Results'}
            self.storage.save_memory(params)

    def load_tool(self, tool):
        params = {
            "collection_name": 'Tools',
            "query": tool,
            "include": ["documents", "metadatas"]
        }

        results = self.storage.query_memory(params)
        filtered = self.functions.extract_metadata(results)
        filtered.pop('timestamp', None)

        return filtered



