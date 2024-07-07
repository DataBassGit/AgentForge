from agentforge.utils.function_utils import Functions
from agentforge.utils.functions.Logger import Logger
from agentforge.utils.chroma_utils import ChromaUtils
from agentforge.agents.ActionSelectionAgent import ActionSelectionAgent


def id_generator(data):
    return [str(i + 1) for i in range(len(data))]


class Action:
    """
    Manages the execution of actions by processing files, running tools in sequence based on the action's configuration,
    and saving the results into a database.

    This class orchestrates the flow from loading action-specific tools, executing these tools, to injecting the
    processed data into the knowledge graph.
    """
    def __init__(self):
        """
        Initializes the Action class, setting up logger, storage utilities, and loading necessary components for
        action processing.
        """
        self.logger = Logger(name=self.__class__.__name__)
        self.storage = ChromaUtils('default')
        self.functions = Functions()

        self.initialize_collection('Actions')
        self.initialize_collection('Tools')

    def initialize_collection(self, collection_name):
        """
        Initializes a specified collection with preloaded data.

        Parameters:
            collection_name (str): The name of the collection to initialize.
        """
        data = self.functions.agent_utils.config.data[collection_name.lower()]

        ids = id_generator(data)

        description = [value['Description'] for key, value in data.items()]
        metadata = [value for key, value in data.items()]

        # Save the item into the selected collection
        self.storage.save_memory(collection_name=collection_name, data=description, ids=ids, metadata=metadata)
        print(f'{collection_name} collection initialized')

    def run(self):
        print('Ran')
