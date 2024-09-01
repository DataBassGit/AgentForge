import traceback
from typing import List, Dict, Optional, Union
from agentforge.utils.function_utils import Functions
from agentforge.utils.functions.Logger import Logger
from agentforge.utils.chroma_utils import ChromaUtils
from agentforge.agents.ActionSelectionAgent import ActionSelectionAgent
from agentforge.agents.ActionCreationAgent import ActionCreationAgent
from agentforge.agents.ToolPrimingAgent import ToolPrimingAgent
import yaml


def id_generator(data: List[Dict]) -> List[str]:
    """
    Generates a list of string IDs for the given data.

    Parameters:
        data (List[Dict]): The data for which to generate IDs.

    Returns:
        List[str]: A list of generated string IDs.
    """
    return [str(i + 1) for i in range(len(data))]


class Actions:
    """
    Provides a series of methods for developers to create custom solutions for managing and executing actions and tools
    within the framework. This class offers the necessary flexibility and modularity to support both in-depth custom
    implementations and generic examples.

    The `auto_execute` method serves as a comprehensive example of how to use the provided methods to orchestrate the
    flow from loading action-specific tools, executing these tools, to injecting the processed data into the knowledge
    graph. Developers can use this method directly or reference it to build their own tailored workflows.
    """

    # --------------------------------------------------------------------------------------------------------
    # -------------------------------- Constructor and Initialization Methods --------------------------------
    # --------------------------------------------------------------------------------------------------------

    def __init__(self):
        """
        Initializes the Actions class, setting up logger, storage utilities, and loading necessary components for
        action processing.
        """
        self.logger = Logger(name=self.__class__.__name__)
        self.storage = ChromaUtils('default')
        self.functions = Functions()
        self.action_creation = ActionCreationAgent()
        self.action_selection = ActionSelectionAgent()
        self.priming_agent = ToolPrimingAgent()

        self.initialize_collection('Actions')
        self.initialize_collection('Tools')

    def initialize_collection(self, collection_name: str) -> None:
        """
        Initializes a specified collection in the vector database with preloaded data. Mainly used to load the
        actions and tools data into the database, allowing for semantic search.

        Parameters:
            collection_name (str): The name of the collection to initialize.
        """
        data = self.functions.agent_utils.config.data[collection_name.lower()]
        ids = id_generator(data)
        description = [value['Description'] for key, value in data.items()]
        metadata = [value for key, value in data.items()]
        metadata = self.functions.parsing_utils.format_metadata(metadata)

        # Save the item into the selected collection
        self.storage.save_memory(collection_name=collection_name, data=description, ids=ids, metadata=metadata)
        self.logger.log(f"\n{collection_name} collection initialized", 'info', 'Actions')

    # --------------------------------------------------------------------------------------------------------
    # ------------------------------------ Primary Functionality Methods -------------------------------------
    # --------------------------------------------------------------------------------------------------------

    def auto_execute(self, objective: str, context: Optional[str] = None,
                     threshold: Optional[float] = 0.8) -> Union[Dict, str, None]:
        """
        Automatically executes the actions for the given objective and context.

        Parameters:
            objective (str): The objective for the execution.
            context (Optional[str]): The context for the execution.
            threshold (Optional[float]): The threshold for action relevance (Lower is stricter). Default is 0.8.

        Returns:
            Union[Dict, str, None]: The result of the execution or an error dictionary.

        Raises:
            Exception: If an error occurs during execution.
        """
        try:
            action_list = self.get_relevant_actions_for_objective(objective=objective, threshold=threshold,
                                                                  num_results=10)
            if action_list:
                self.logger.log(f"\nSelecting Action for Objective:\n{objective}", 'info', 'Actions')
                order = ["Name", "Description"]
                available_actions = self.functions.tool_utils.format_item_list(action_list, order)
                selected_action = self.select_action_for_objective(objective=objective,
                                                                   action_list=available_actions,
                                                                   context=context)
                self.logger.log(f"\nSelected Action:\n{selected_action}", 'info', 'Actions')
            else:
                self.logger.log(f"\nCrafting Action for Objective:\n{objective}", 'info', 'Actions')
                order = ["Name", "Description", "Args"]
                tool_list = self.functions.tool_utils.get_tool_list()
                selected_action = self.craft_action_for_objective(objective=objective,
                                                                  tool_list=tool_list,
                                                                  context=context,
                                                                  info_order=order)
                self.logger.log(f"\nCrafted Action:\n{selected_action}", 'info', 'Actions')

                if 'error' in selected_action:
                    return selected_action

            action_info_order = ["Name", "Description"]
            tool_info_order = ["Name", "Description", "Args", "Instruction", "Example"]
            result: Dict = self.run_tools_in_sequence(objective=objective,
                                                      action=selected_action,
                                                      action_info_order=action_info_order,
                                                      tool_info_order=tool_info_order)
            # Check if an error occurred
            if isinstance(result, Dict) and result['status'] != 'success':
                self.logger.log(f"\nAction Failed:\n{result['message']}", 'error', 'Actions')
                return result  # Stop execution and return the error message

            self.logger.log(f"\nAction Result:\n{result['data']}", 'info', 'Actions')
            return result
        except Exception as e:
            error_message = f"Error in running action: {e}"
            self.logger.log(error_message, 'error', 'Actions')
            return {'error': error_message, 'traceback': traceback.format_exc()}

    def get_relevant_actions_for_objective(self, objective: str, threshold: Optional[float] = None,
                                           num_results: int = 1, parse_result: bool = True) -> Dict:
        """
        Loads actions based on the current object and specified criteria.

        Parameters:
            objective (str): The objective to find relevant actions for.
            threshold (Optional[float]): The threshold for action relevance (Lower is stricter).
            num_results (int): The number of results to return. Default is 1.
            parse_result (bool): Whether to parse the result. Default is True.
            Not used if format_result is False.

        Returns:
            Dict: The action list or an empty dictionary if no actions are found.
        """
        action_list = {}
        try:
            action_list = self.storage.search_storage_by_threshold(collection_name='Actions',
                                                                   query=objective,
                                                                   threshold=threshold,
                                                                   num_results=num_results)
        except Exception as e:
            self.logger.log(f"Error loading actions: {e}", 'error', 'Actions')

        if not action_list:
            self.logger.log(f"No Actions Found", 'info', 'Actions')
            return {}

        if parse_result:
            action_list = self.functions.tool_utils.parse_item_list(action_list)

        return action_list

    def select_action_for_objective(self, objective: str, action_list: str | Dict, context: Optional[str] = None,
                                    parse_result: bool = True) -> Union[str, Dict]:
        """
        Selects an action for the given objective from the provided action list.

        Parameters:
            objective (str): The objective to select an action for.
            action_list (str | Dict): The list of actions to select from.
            If given a Dict the method will attempt to convert to a string.
            context (Optional[str]): The context for action selection.
            parse_result (bool): Whether to parse the result. Default is True.

        Returns:
            Union[str, Dict]: The selected action or formatted result.
        """
        if isinstance(action_list, Dict):
            action_list = self.functions.tool_utils.format_item_list(action_list)

        selected_action = self.action_selection.run(objective=objective, action_list=action_list, context=context)

        if parse_result:
            selected_action = self.functions.parsing_utils.parse_yaml_content(selected_action)

        return selected_action

    def craft_action_for_objective(self, objective: str, tool_list: Dict | str, context: Optional[str] = None,
                                   info_order: Optional[List[str]] = None,
                                   parse_result: bool = True) -> Union[str, Dict]:
        """
        Crafts a new action for the given objective.

        Parameters:
            objective (str): The objective to craft an action for.
            tool_list (Dict | str): The list of tools to be used. Will attempt to convert to a string if given a Dict.
            context (Optional[str]): The context for action crafting.
            parse_result (bool): Whether to parse the result. Default is True.
            info_order (Optional[List[str]]): Tool information to include in the formatted tool list. Default is None.

        Returns:
            Union[str, Dict]: The crafted action or formatted result.
        """
        if isinstance(tool_list, Dict):
            tool_list = self.functions.tool_utils.format_item_list(tool_list, info_order)

        self.logger.log(f"\nTool List:\n{tool_list}", 'info', 'Actions')

        new_action = self.action_creation.run(objective=objective,
                                              context=context,
                                              tool_list=tool_list)

        if parse_result:
            new_action = self.functions.parsing_utils.parse_yaml_content(new_action)

            if new_action is None:
                msg = {'error': "Error Creating Action"}
                self.logger.log(msg['error'], 'error', 'Actions')
                return msg
            else:
                path = f".agentforge/actions/unverified/{new_action['Name'].replace(' ', '_')}.yaml"
                with open(path, "w") as file:
                    yaml.dump(new_action, file)
                # self.functions.agent_utils.config.add_item(new_action, 'Actions')
                count = self.storage.count_documents(collection_name='actions')+1
                metadata = [{'Name': new_action['Name'], 'Description': new_action['Description'], 'Path': path}]
                self.storage.save_memory(collection_name='actions', data=new_action['Description'], ids=count, metadata=metadata)

        return new_action

    def prime_tool_for_action(self, objective: str, action: Union[str, Dict], tool: Dict, previous_results: Optional[str] = None,
                              tool_context: Optional[str] = None, action_info_order: Optional[List[str]] = None,
                              tool_info_order: Optional[List[str]] = None) -> Dict:
        """
        Prepares the tool for execution by running the ToolPrimingAgent.

        Parameters:
            objective (str): The objective for tool priming.
            action (Union[str, Dict]): The action to prime the tool for.
                If a dictionary, it will be formatted using the tool_info_order methods.
            tool (Dict): The tool to be primed.
            previous_results (Optional[str]): The results from previous tool executions.
            tool_context (Optional[str]): The context for the tool.
            action_info_order (Optional[List[str]]): The order of action information to include in the Agent prompt.
            tool_info_order (Optional[List[str]]): The order of tool information to include in the Agent prompt.

        Returns:
            Dict: The formatted payload for the tool.

        Raises:
            Exception: If an error occurs during tool priming.
        """
        formatted_tool = self.functions.tool_utils.format_item(tool, tool_info_order)

        if isinstance(action, Dict):
            action = self.functions.tool_utils.format_item(action, action_info_order)

        try:
            # Load the paths into a dictionary
            paths_dict = self.storage.config.data['settings']['system']['Paths']

            # Construct the work_paths string by iterating over the dictionary
            work_paths = None
            if paths_dict:
                work_paths = "\n".join(f"{key}: {value}" for key, value in paths_dict.items())

            payload = self.priming_agent.run(objective=objective,
                                             action=action,
                                             tool_name=tool.get('Name'),
                                             tool_info=formatted_tool,
                                             path=work_paths,
                                             previous_results=previous_results,
                                             tool_context=tool_context)

            formatted_payload = self.functions.parsing_utils.parse_yaml_content(payload)

            if formatted_payload is None:
                return {'error': 'Parsing Error - Model did not respond in specified format'}

            self.logger.log(f"Tool Payload: {formatted_payload}", 'info', 'Actions')
            return formatted_payload
        except Exception as e:
            message = f"Error in priming tool '{tool['Name']}': {e}"
            self.logger.log(message, 'error', "Actions")
            return {'error': message, 'traceback': traceback.format_exc()}

    def run_tools_in_sequence(self, objective: str, action: Dict,
                              action_info_order: Optional[List[str]] = None,
                              tool_info_order: Optional[List[str]] = None) -> Union[Dict, None]:
        """
        Runs the specified tools in sequence for the given objective and action.

        Parameters:
            objective (str): The objective for running the tools.
            action (Dict): The action containing the tools to run.
            action_info_order (Optional[List[str]]): The order of action information to include in the Agent prompt.
            tool_info_order (Optional[List[str]]): The order of tool information to include in the Agent prompt.

        Returns:
            Union[Dict, None]: The final result of the tool execution or an error dictionary.

        Raises:
            Exception: If an error occurs while running the tools in sequence.
        """
        results: Dict = {}
        tool_context: str = ''

        try:
            tools = self.functions.tool_utils.parse_tools_in_action(action)

            # Check if an error occurred
            if isinstance(tools, Dict) and 'error' in tools:
                return tools

            for tool in tools:
                payload = self.prime_tool_for_action(objective=objective,
                                                     action=action,
                                                     tool=tool,
                                                     previous_results=results.get('data', None),
                                                     tool_context=tool_context,
                                                     action_info_order=action_info_order,
                                                     tool_info_order=tool_info_order)

                if isinstance(payload, Dict) and 'error' in payload:
                    return payload  # Stop execution and return the error message

                tool_context = payload.get('next_tool_context')
                results = self.functions.tool_utils.dynamic_tool(tool, payload)

                # Check if an error occurred
                if isinstance(results, Dict) and results['status'] != 'success':
                    return results  # Stop loop and return the error message

            return results

        except Exception as e:
            error_message = f"Error running tools in sequence: {e}"
            self.logger.log(error_message, 'error')
            return {'error': error_message, 'traceback': traceback.format_exc()}

