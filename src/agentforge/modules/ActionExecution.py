from agentforge.agents.ActionPrimingAgent import ActionPrimingAgent
from agentforge.utils.function_utils import Functions
from agentforge.utils.storage_interface import StorageInterface


class Action:
    def __init__(self):
        self.storage = StorageInterface().storage_utils
        self.functions = Functions()
        self.priming_agent = ActionPrimingAgent()
        self.action = {}
        self.tools = {}
        self.tool = {}
        self.results = {}
        self.context = {}

    def run(self, action, context=None):
        if action:
            self.context = context
            self.action = action
            self.load_action_tools()
            self.run_tools_in_sequence()
            self.save_action_results()
            return self.results

    def load_action_tools(self):
        tools = self.action['Tools'].split(', ')
        self.tools = {tool: self.load_tool(tool) for tool in tools}

    def run_tools_in_sequence(self):
        self.tool['Result'] = None
        for self.tool['Name'], self.tool['Data'] in self.tools.items():
            self.get_tool_script()
            self.process_tool_data()
            self.prime_tool()
            self.execute_tool()
            self.parse_tool_result()

    def get_tool_script(self):
        self.tool['Script'] = self.tool['Data'].pop('Script')

    def process_tool_data(self):
        tool_info = '\n'.join([f'{key}: {value}' for key, value in self.tool['Data'].items() if key != 'Name'])
        self.tool['Prompt'] = f"Tool: {self.tool['Name']}\n{tool_info}"

    def prime_tool(self):
        # Load the paths into a dictionary
        paths_dict = self.storage.config.settings['paths']

        # Construct the work_paths string by iterating over the dictionary
        work_paths = "\n".join(f"{key}: {value}" for key, value in paths_dict.items())

        self.tool['Payload'] = self.priming_agent.run(tool=self.tool['Prompt'],
                                                      path=work_paths,
                                                      results=self.tool['Result'],
                                                      context=self.context)
        self.functions.tool_utils.show_primed_tool(self.tool['Name'], self.tool['Payload'])

    def execute_tool(self):
        self.tool['Payload']['command'] = self.tool['Data']['Command']
        self.tool['Result'] = self.functions.tool_utils.dynamic_tool(self.tool['Script'], self.tool['Payload'])

    def parse_tool_result(self):
        self.results[self.tool['Name']] = self.tool['Result']

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
        filtered = self.functions.parsing.extract_metadata(results)
        filtered.pop('timestamp', None)

        return filtered



