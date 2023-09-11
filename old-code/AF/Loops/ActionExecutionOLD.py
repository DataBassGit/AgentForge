from agentforge.agents.ActionSelectionAgent import ActionSelectionAgent
from agentforge.agents.ActionPrimingAgent import ActionPrimingAgent
from agentforge.utils.function_utils import Functions
from agentforge.utils.storage_interface import StorageInterface


def parse_tools_data(tool_name, tool_info):
    tool = f"Tool: {tool_name}\n" + '\n'.join([f'{key}: {value}' for key, value in tool_info.items()])
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
        action_results = self.action_agent.run()

        if 'documents' in action_results:
            self.handle_action_selected(action_results)
        else:
            self.handle_no_relevant_action(frustration)

    def handle_action_selected(self, action_results):
        action = self.functions.extract_metadata(action_results)
        self.functions.print_result(action['Description'], 'Action Selected')

        tool_data = action['Tools'].split(', ')
        tools = {tool: self.load_tool(tool) for tool in tool_data}

        self.run_tools_in_sequence(tools)

    def run_tools_in_sequence(self, tools):
        tool_result = None
        for tool_name, tool_info in tools.items():
            tool_call = tool_info.pop('Script')
            tool = parse_tools_data(tool_name, tool_info)
            payload = self.priming_agent.run(tool=tool, results=tool_result)
            self.functions.print_primed_tool(tool_name, payload)

            self.functions.print_message(f"\nRunning {tool_name} ...")
            tool_result = self.functions.dyna_tool(tool_call.lower(), payload)
            self.functions.print_result(tool_result, f"{tool_name} Result")

    def handle_no_relevant_action(self, frustration):
        self.functions.print_result(f'No Relevant Action Found! - Frustration: {frustration}', 'Selection Results')

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


