from agentforge.agents.ActionPrimingAgent import ActionPrimingAgent
from agentforge.utils.function_utils import Functions
from agentforge.utils.storage_interface import StorageInterface
from agentforge.utils.functions.Logger import Logger


def id_generator(data):
    return [str(i + 1) for i in range(len(data))]


def format_metadata(metadata_list):
    # Check if the input is a list
    if not isinstance(metadata_list, list):
        raise TypeError("Expected a list of dictionaries")

    # Iterate through each dictionary in the list
    for metadata in metadata_list:
        # Ensure each item in the list is a dictionary
        if not isinstance(metadata, dict):
            raise TypeError("Each item in the list should be a dictionary")

        # Format each dictionary
        for key, value in metadata.items():
            # Check if the value is a list (array)
            if isinstance(value, list):
                # Convert list elements into a comma-separated string
                # Update the dictionary with the formatted string
                metadata[key] = ', '.join(value)

    return metadata_list


class Action:
    def __init__(self):
        self.logger = Logger(name=self.__class__.__name__)
        self.storage = StorageInterface().storage_utils
        self.functions = Functions()
        self.priming_agent = ActionPrimingAgent()
        self.action = {}
        self.tools = {}
        self.tool = {}
        self.results = {}
        self.context = {}
        self.task = {}

        self.initialize_collection('Actions')
        self.initialize_collection('Tools')

    def run(self, task, action, context=None):
        try:
            if action:
                self.context = context
                self.action = action
                self.task = task
                self.load_action_tools()
                self.run_tools_in_sequence()
                self.save_action_results()
                return self.results
        except Exception as e:
            self.logger.log(f"Error in running action: {e}", 'error')
            return None

    def initialize_collection(self, collection_name):
        """Initializes the collection with pre-loaded data."""
        # try:
        data = self.functions.agent_utils.config.data[collection_name.lower()]

        ids = id_generator(data)

        description = [value['Description'] for key, value in data.items()]
        meta = [value for key, value in data.items()]
        metadata = format_metadata(meta)

        # storage system expects the data to be formatted.
        save_params = {
            "collection_name": collection_name,
            "ids": ids,
            "data": description,
            "metadata": metadata,
        }

        # Save the item into the selected collection
        self.storage.save_memory(save_params)

    def load_action_tools(self):
        try:
            tools = self.action['Tools'].split(', ')
            self.tools = {tool: self.load_tool(tool) for tool in tools}
        except Exception as e:
            self.logger.log(f"Error in loading action tools: {e}", 'error')
            self.tools = {}

    def run_tools_in_sequence(self):
        self.tool['Result'] = None
        try:
            for self.tool['Name'], self.tool['Data'] in self.tools.items():
                self.get_tool_script()
                self.process_tool_data()
                self.prime_tool()
                self.execute_tool()
                self.parse_tool_result()
        except Exception as e:
            self.logger.log(f"Error in running tools in sequence: {e}", 'error')

    def get_tool_script(self):
        self.tool['Script'] = self.tool['Data'].pop('Script')

    def process_tool_data(self):
        tool_info = '\n'.join([f'{key}: {value}' for key, value in self.tool['Data'].items() if key != 'Name'])
        self.tool['Prompt'] = f"Tool: {self.tool['Name']}\n{tool_info}"

    def prime_tool(self):
        try:
            # Load the paths into a dictionary
            paths_dict = self.storage.config.data['settings']['configuration']['Paths']

            # Construct the work_paths string by iterating over the dictionary
            work_paths = None
            if self.tool['Name'] == 'Read Directory':
                work_paths = "\n".join(f"{key}: {value}" for key, value in paths_dict.items())

            self.tool['Payload'] = self.priming_agent.run(task=self.task,
                                                          tool=self.tool['Prompt'],
                                                          path=work_paths,
                                                          results=self.tool['Result'],
                                                          context=self.context)
            self.functions.tool_utils.show_primed_tool(self.tool['Name'], self.tool['Payload'])
        except Exception as e:
            self.logger.log(f"Error in priming tool: {e}", 'error')

    def execute_tool(self):
        try:
            self.tool['Payload']['command'] = self.tool['Data']['Command']
            self.tool['Result'] = self.functions.tool_utils.dynamic_tool(self.tool['Script'], self.tool['Payload'])
        except Exception as e:
            self.logger.log(f"Error in executing tool: {e}", 'error')

    def parse_tool_result(self):
        try:
            self.results[self.tool['Name']] = self.tool['Result']
        except Exception as e:
            self.logger.log(f"Error in parsing tool result: {e}", 'error')

    def save_action_results(self):
        try:
            for key, result in self.results.items():
                params = {'data': [result], 'collection_name': 'Results'}
                self.storage.save_memory(params)
        except Exception as e:
            self.logger.log(f"Error in saving action results: {e}", 'error')

    def load_tool(self, tool):
        try:
            params = {
                "collection_name": 'Tools',
                "query": tool,
                "include": ["documents", "metadatas"]
            }

            results = self.storage.query_memory(params)
            filtered = results['metadatas'][0][0]
            filtered.pop('timestamp', None)

            return filtered
        except Exception as e:
            self.logger.log(f"Error in loading tool: {e}", 'error')
            return None

