from agentforge.utils.function_utils import Functions
from agentforge.utils.functions.Logger import Logger
from agentforge.utils.chroma_utils import ChromaUtils
from agentforge.agents.ActionSelectionAgent import ActionSelectionAgent
from agentforge.agents.ActionCreationAgent import ActionCreationAgent


def id_generator(data):
    return [str(i + 1) for i in range(len(data))]


def format_tool_list(tool_list, keys_to_include):
    formatted_string = "---\n"
    for tool in tool_list:
        for key in keys_to_include:
            if key in tool:
                formatted_string += f"{key}: {tool[key]}\n"
        formatted_string += "---\n"
    return formatted_string


class Action:
    """
    Manages the execution of actions by processing files, running tools in sequence based on the action's configuration,
    and saving the results into a database.

    This class orchestrates the flow from loading action-specific tools, executing these tools, to injecting the
    processed data into the knowledge graph.
    """
    tool_info_to_include = ["Name",  "Description", "Command", "Args", "Instruction", "Example"]

    def __init__(self):
        """
        Initializes the Action class, setting up logger, storage utilities, and loading necessary components for
        action processing.
        """
        self.logger = Logger(name=self.__class__.__name__)
        self.storage = ChromaUtils('default')
        self.functions = Functions()

        self.action_list = self.initialize_collection('Actions')
        self.tool_list: dict = self.initialize_collection('Tools')

    def initialize_collection(self, collection_name) -> {}:
        """
        Initializes a specified collection with preloaded data.

        Parameters:
            collection_name (str): The name of the collection to initialize.
        """
        data = self.functions.agent_utils.config.data[collection_name.lower()]
        ids = id_generator(data)
        description = [value['Description'] for key, value in data.items()]
        metadata = [value for key, value in data.items()]
        metadata = self.functions.parsing_utils.format_metadata(metadata)

        # print(f'\nData:\n{description}')
        # print(f'\nMeta:\n{metadata}\n')

        # Save the item into the selected collection
        self.storage.save_memory(collection_name=collection_name, data=description, ids=ids, metadata=metadata)
        print(f'{collection_name} collection initialized')
        return metadata

    def run(self, objective: str, context: str = None):

        try:
            available_actions = ActionSelectionAgent(threshold=0.5).run(objective=objective, context=context)
            if not available_actions:
                print(f'\nSelecting Action for Objective:\n{objective}')

                print(f'\nTool List:\n{self.tool_list}')

                formatted_tool_list = format_tool_list(self.tool_list, self.tool_info_to_include)

                potential_action = ActionCreationAgent().run(objective=objective,
                                                             context=context,
                                                             tool_list=formatted_tool_list)

                print(f'\nPotential Action:\n{potential_action}')

        except Exception as e:
            self.logger.log(f"Error in running action: {e}", 'error')
            return None

        print('Ran')
