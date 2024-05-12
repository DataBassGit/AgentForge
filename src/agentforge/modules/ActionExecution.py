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
    """
    Manages the execution of actions by processing files, running tools in sequence based on the action's configuration,
    and saving the results into a database.

    This class orchestrates the flow from loading action-specific tools, executing these tools, to injecting the
    processed data into the knowledge graph.
    """
    def __init__(self):
        """
        Initializes the Action class, setting up logger, storage utilities, and loading necessary components for action processing.
        """
        self.logger = Logger(name=self.__class__.__name__)
        self.storage = StorageInterface().storage_utils
        self.functions = Functions()
        self.priming_agent = ActionPrimingAgent()
        self.action = {}
        self.tools = {}
        self.tool = {}
        self.results = {}
        self.context = {}
        self.objective = {}
        self.task = {}

        self.initialize_collection('Actions')
        self.initialize_collection('Tools')

    def run(self, objective, task, action, context=None):
        """
        Main method to process an action for a given task and objective, optionally within a provided context.

        Parameters:
            objective (dict): The objective information related to the action.
            task (dict): Task details that the action pertains to.
            action (dict): Action configuration including tools to be used.
            context (dict, optional): Contextual information to influence action processing.

        Returns:
            dict or None: The results of action processing, or None if an error occurs.

        Raises:
            Exception: If an error is encountered during action processing.
        """
        try:
            if action:
                self.context = context
                self.action = action
                self.objective = objective
                self.task = task
                self.load_action_tools()
                self.run_tools_in_sequence()
                self.save_action_results()
                return self.results
        except Exception as e:
            self.logger.log(f"Error in running action: {e}", 'error')
            return None

    def initialize_collection(self, collection_name):
        """
        Initializes a specified collection with preloaded data.

        Parameters:
            collection_name (str): The name of the collection to initialize.
        """
        # try:
        data = self.functions.agent_utils.config.data[collection_name.lower()]

        ids = id_generator(data)

        description = [value['Description'] for key, value in data.items()]
        meta = [value for key, value in data.items()]
        metadata = format_metadata(meta)

        # Save the item into the selected collection
        self.storage.save_memory(collection_name=collection_name, data=description, ids=ids, metadata=metadata)

    def load_action_tools(self):
        """
        Loads the tools specified in the action's configuration.

        Raises:
            Exception: If an error occurs while loading action tools.
        """
        try:
            tools = self.action['Tools'].split(', ')
            self.tools = {tool: self.load_tool(tool) for tool in tools}
        except Exception as e:
            self.logger.log(f"Error in loading action tools: {e}", 'error')
            self.tools = {}

    def run_tools_in_sequence(self):
        """
        Executes the loaded tools in sequence as configured for the action.

        Raises:
            Exception: If an error occurs during the sequential tool execution.
        """
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
        """
        Extracts the script path from the tool's data.
        """
        self.tool['Script'] = self.tool['Data'].pop('Script')

    def process_tool_data(self):
        """
        Prepares the tool data for execution, constructing the tool prompt from its configuration.
        """
        tool_info = '\n'.join([f'{key}: {value}' for key, value in self.tool['Data'].items() if key != 'Name'])
        self.tool['Prompt'] = f"Tool: {self.tool['Name']}\n{tool_info}"

    def prime_tool(self):
        """
        Prepares the tool for execution by running the ActionPrimingAgent.

        Raises:
            Exception: If an error occurs during tool priming.
        """
        try:
            # Load the paths into a dictionary
            paths_dict = self.storage.config.data['settings']['system']['Paths']

            # Construct the work_paths string by iterating over the dictionary
            work_paths = None
            if self.tool['Name'] == 'Read Directory':
                work_paths = "\n".join(f"{key}: {value}" for key, value in paths_dict.items())

            self.tool['Payload'] = self.priming_agent.run(objective=self.objective,
                                                          task=self.task,
                                                          tool=self.tool['Prompt'],
                                                          path=work_paths,
                                                          results=self.tool['Result'],
                                                          context=self.context)
            self.functions.tool_utils.show_primed_tool(self.tool['Name'], self.tool['Payload'])
        except Exception as e:
            self.logger.log(f"Error in priming tool: {e}", 'error')

    def execute_tool(self):
        """
        Executes the tool using the dynamic tool utility with the prepared payload.

        Raises:
            Exception: If an error occurs during tool execution.
        """
        try:
            self.tool['Payload']['command'] = self.tool['Data']['Command']
            self.tool['Result'] = self.functions.tool_utils.dynamic_tool(self.tool['Script'], self.tool['Payload'])
        except Exception as e:
            self.logger.log(f"Error in executing tool: {e}", 'error')

    def parse_tool_result(self):
        """
        Processes and stores the result of the tool execution.

        Raises:
            Exception: If an error occurs during result parsing.
        """
        try:
            self.results[self.tool['Name']] = self.tool['Result']
        except Exception as e:
            self.logger.log(f"Error in parsing tool result: {e}", 'error')

    def save_action_results(self):
        """
        Saves the results of the action processing into the specified collection.

        Raises:
            Exception: If an error occurs while saving action results.
        """

        try:
            # Maybe we can just send the results directly?
            for key, result in self.results.items():
                self.storage.save_memory(collection_name='Results', data=[result])
        except Exception as e:
            self.logger.log(f"Error in saving action results: {e}", 'error')

    def load_tool(self, tool):
        """
        Loads configuration and data for a specified tool from the storage.

        Parameters:
            tool (str): The name of the tool to load.

        Returns:
            dict or None: The loaded tool data, or None if an error occurs.

        Raises:
            Exception: If an error occurs while loading the tool.
        """
        try:
            results = self.storage.query_memory(collection_name='Tools', query=tool, include=["documents", "metadatas"])
            filtered = results['metadatas'][0][0]
            filtered.pop('timestamp', None)

            return filtered
        except Exception as e:
            self.logger.log(f"Error in loading tool: {e}", 'error')
            return None

