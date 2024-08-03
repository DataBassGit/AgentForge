import traceback
from typing import List, Dict, Optional, Union
from agentforge.utils.function_utils import Functions
from agentforge.utils.functions.Logger import Logger
from agentforge.utils.chroma_utils import ChromaUtils
from agentforge.agents.ActionSelectionAgent import ActionSelectionAgent
from agentforge.agents.ActionCreationAgent import ActionCreationAgent
from agentforge.agents.ToolPrimingAgent import ToolPrimingAgent


def id_generator(data: List[Dict]) -> List[str]:
    """
    Generates a list of string IDs for the given data.

    Parameters:
        data (List[Dict]): The data for which to generate IDs.

    Returns:
        List[str]: A list of generated string IDs.
    """
    return [str(i + 1) for i in range(len(data))]


def format_tool_list(tool_list: List[Dict], keys_to_include: List[str]) -> str:
    """
    Formats a list of tools into a human-readable string.

    Parameters:
        tool_list (List[Dict]): The list of tools to format.
        keys_to_include (List[str]): The keys to include in the formatted string.

    Returns:
        str: The formatted string representing the tool list.
    """
    formatted_string = "---\n"
    for tool in tool_list:
        for key in keys_to_include:
            if key in tool:
                formatted_string += f"{key}: {tool[key]}\n"
        formatted_string += "---\n"
    return formatted_string


def format_action(action: Dict[str, Union[str, List[str]]], order: List[str]) -> str:
    """
    Formats an action into a human-readable string.

    Parameters:
        action (Dict[str, Union[str, List[str]]]): The action to format.
        order (List[str]): The order in which to format the action's keys.

    Returns:
        str: The formatted action string.
    """
    formatted_string = ""
    for key in order:
        if key == 'Name':
            formatted_string += f"Action: {action[key].strip()}\n\n"
        elif key == 'Tools':
            formatted_string += f"{key}: \n- " + "\n- ".join(action[key]) + "\n\n"
        elif key in action:
            formatted_string += f"{key}:\n{action[key].strip()}\n\n"
    return formatted_string.strip()


class Actions:
    """
    Manages the execution of actions by processing files, running tools in sequence based on the action's configuration,
    and saving the results into a database.

    This class orchestrates the flow from loading action-specific tools, executing these tools, to injecting the
    processed data into the knowledge graph.
    """

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

    def parse_actions(self, action_list: Dict) -> Optional[Dict[str, Dict]]:
        """
        Parses and structures the actions fetched from storage for easier handling and processing.

        Parameters:
            action_list (Dict): The list of actions to parse.

        Returns:
            Optional[Dict[str, Dict]]: A dictionary of parsed actions, or None if an error occurs.
        """
        parsed_actions = {}
        try:
            for metadata in action_list.get("metadatas", []):
                action_name = metadata.get("Name")
                if action_name:
                    metadata.pop('timestamp', None)  # Remove any non-relevant metadata, such as timestamps
                    parsed_actions[action_name] = metadata
            return parsed_actions
        except Exception as e:
            self.logger.log(f"Error Parsing Actions:\n{action_list}\n\nError: {e}", 'error', 'Actions')
            return None

    def format_actions(self, action_list: Dict) -> Optional[str]:
        """
        Formats the actions into a human-readable string and stores it in the agent's data for later use.

        Parameters:
            action_list (Dict): The list of actions to format.

        Returns:
            Optional[str]: The formatted string of actions, or None if an error occurs.
        """
        try:
            formatted_actions = []
            parsed_actions = self.parse_actions(action_list)
            for action_name, metadata in parsed_actions.items():
                action_desc = metadata.get("Description", "No Description")
                formatted_action = f"Action: {action_name}\nDescription: {action_desc}\n"
                formatted_actions.append(formatted_action)
            return "\n".join(formatted_actions)
        except Exception as e:
            self.logger.log(f"Error Formatting Actions:\n{action_list}\n\nError: {e}", 'error', 'Actions')
            return None

    def initialize_collection(self, collection_name: str) -> None:
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

        # Save the item into the selected collection
        self.storage.save_memory(collection_name=collection_name, data=description, ids=ids, metadata=metadata)
        self.logger.log(f"\n{collection_name} collection initialized", 'info', 'Actions')

    def get_relevant_actions_for_objective(self, objective: str, threshold: Optional[float] = None, num_results: int = 1) -> Union[str, Dict]:
        """
        Loads actions based on the current object and specified criteria.

        Parameters:
            objective (str): The objective to find relevant actions for.
            threshold (Optional[float]): The threshold for relevance.
            num_results (int): The number of results to return.

        Returns:
            Union[str, Dict]: The formatted actions or an empty dictionary if no actions are found.
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

        action_list = self.format_actions(action_list)

        return action_list

    def get_tool_list(self, num_results: int = 20) -> Optional[Dict[str, Union[List[str], None, List[Dict]]]]:
        """
        Retrieves the list of tools from storage.

        Parameters:
            num_results (int): The number of tools to return.

        Returns:
            Optional[Dict[str, Union[List[str], None, List[Dict]]]]: A dictionary containing all tool information,
            or None if there are no tools.
        """
        if self.storage.count_collection('Tools') <= num_results:
            tool_list = self.storage.load_collection('Tools')
            return tool_list

        # Need a way to query for relevant tools

    def select_action_for_objective(self, objective: str, action_list: str, context: Optional[str] = None,
                                    format_result: bool = False) -> Union[str, Dict]:
        """
        Selects an action for the given objective from the provided action list.

        Parameters:
            objective (str): The objective to select an action for.
            action_list (str): The list of actions to select from.
            context (Optional[str]): The context for action selection.
            format_result (bool): Whether to format the result. Default is False.

        Returns:
            Union[str, Dict]: The selected action or formatted result.
        """
        selected_action = self.action_selection.run(objective=objective, action_list=action_list, context=context)

        if format_result:
            selected_action = self.functions.parsing_utils.parse_yaml_content(selected_action)

        return selected_action

    def craft_action_for_objective(self, objective: str, context: Optional[str] = None,
                                   format_result: bool = False) -> Union[str, Dict]:
        """
        Crafts a new action for the given objective.

        Parameters:
            objective (str): The objective to craft an action for.
            context (Optional[str]): The context for action crafting.
            format_result (bool): Whether to format the result. Default is False.

        Returns:
            Union[str, Dict]: The crafted action or formatted result.
        """
        tool_info_to_include = ["Name", "Description", "Args"]
        tool_list = self.get_tool_list()

        self.logger.log(f"\nTool List:\n{tool_list}", 'info', 'Actions')
        formatted_tool_list = format_tool_list(tool_list['metadatas'], tool_info_to_include)

        new_action = self.action_creation.run(objective=objective,
                                              context=context,
                                              tool_list=formatted_tool_list)

        if format_result:
            new_action = self.functions.parsing_utils.parse_yaml_content(new_action)

        return new_action

    def load_tool_from_storage(self, tool: str) -> Optional[Dict]:
        """
        Loads configuration and data for a specified tool from the storage.

        Parameters:
            tool (str): The name of the tool to load.

        Returns:
            Optional[Dict]: The loaded tool data, or None if an error occurs.
        """
        try:
            result = self.storage.query_memory(collection_name='Tools', query=tool, include=["documents", "metadatas"])
            filtered = result['metadatas'][0]
            return filtered
        except Exception as e:
            self.logger.log(f"Error in loading tool: {e}", 'error')
            return None

    def parse_action_tools(self, action: Dict) -> List[Dict] | None:
        """
        Loads the tools specified in the action's configuration.

        Parameters:
            action (Dict): The action containing the tools to load.

        Returns:
            List[Dict]: A list with the loaded tools or None.

        Raises:
            Exception: If an error occurs while loading action tools.
        """
        try:
            tools = [self.load_tool_from_storage(tool) for tool in action['Tools']]
        except Exception as e:
            self.logger.log(f"Error in loading action tools: {e}", 'error', 'Actions')
            tools = None

        return tools

    def prime_tool(self, objective: str, action: str, tool: Dict, previous_results: Optional[str],
                   tool_context: Optional[str]) -> Dict:
        """
        Prepares the tool for execution by running the ToolPrimingAgent.

        Parameters:
            objective (str): The objective for tool priming.
            action (str): The action to prime the tool for.
            tool (Dict): The tool to be primed.
            previous_results (Optional[str]): The results from previous tool executions.
            tool_context (Optional[str]): The context for the tool.

        Returns:
            Dict: The formatted payload for the tool.

        Raises:
            Exception: If an error occurs during tool priming.
        """
        tool_info_to_include = ["Name", "Description", "Command", "Args", "Instruction", "Example"]
        formatted_tool = format_tool_list([tool], tool_info_to_include)

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
                raise Exception('Parsing Error - Model did not respond in specified format')

            self.logger.log(f"Tool Payload: {formatted_payload}", 'info', 'Actions')
            return formatted_payload
        except Exception as e:
            self.logger.log(f"Error in priming tool: {e}", 'error', "Actions")
            message = f"Error in priming tool '{tool['Name']}': {e}"
            self.logger.log(message, 'error', "Actions")
            return {'error': message, 'traceback': traceback.format_exc()}

    def execute_tool(self, tool: Dict, payload: Dict) -> Union[Dict, None]:
        """
        Executes the tool using the dynamic tool utility with the prepared payload.

        Parameters:
            tool (Dict): The tool to be executed.
            payload (Dict): The payload to execute the tool with.

        Returns:
            Union[Dict, None]: The result of the tool execution or an error dictionary.

        Raises:
            Exception: If an error occurs during tool execution.
        """
        try:
            result = self.functions.tool_utils.dynamic_tool(tool, payload)
            # Check if result contains an error
            if isinstance(result, Dict) and 'error' in result:
                return result
        except Exception as e:
            message = f"Error in executing tool '{tool['Name']}': {e}"
            self.logger.log(message, 'error')
            return {'error': message, 'traceback': traceback.format_exc()}

    def run_tools_in_sequence(self, objective: str, action: Dict, tools: List[Dict]) -> Union[Dict, None]:
        """
        Runs the specified tools in sequence for the given objective and action.

        Parameters:
            objective (str): The objective for running the tools.
            action (Dict): The action containing the tools to run.
            tools (List[Dict]): The list of tools to run.

        Returns:
            Union[Dict, None]: The final result of the tool execution or an error dictionary.

        Raises:
            Exception: If an error occurs while running the tools in sequence.
        """
        results = None
        tool_context = None
        order = ["Name", "Description", "Tools", "Instruction", "Example"]
        formatted_action = format_action(action, order)
        try:
            for tool in tools:
                payload = self.prime_tool(objective=objective,
                                          action=formatted_action,
                                          tool=tool,
                                          previous_results=results,
                                          tool_context=tool_context)

                if isinstance(payload, Dict) and 'error' in payload:
                    return payload  # Stop execution and return the error message

                tool_context = payload.get('next_tool_context')
                results = self.execute_tool(tool, payload)

                # Check if an error occurred
                if isinstance(results, Dict) and 'error' in results:
                    return results  # Stop execution and return the error message

            return results

        except Exception as e:
            error_message = f"Error in running tools in sequence: {e}"
            self.logger.log(error_message, 'error')
            return {'error': error_message, 'traceback': traceback.format_exc()}

    def auto_execute(self, objective: str, context: Optional[str] = None) -> Union[Dict, None]:
        """
        Automatically executes the actions for the given objective and context.

        Parameters:
            objective (str): The objective for the execution.
            context (Optional[str]): The context for the execution.

        Returns:
            Union[Dict, None]: The result of the execution or an error dictionary.

        Raises:
            Exception: If an error occurs during execution.
        """
        try:
            available_actions = self.get_relevant_actions_for_objective(objective=objective, threshold=0.5)

            if available_actions:
                self.logger.log(f"\nSelecting Action for Objective:\n{objective}", 'info', 'Actions')
                selected_action = self.select_action_for_objective(objective=objective,
                                                                   action_list=available_actions,
                                                                   context=context,
                                                                   format_result=True)
                self.logger.log(f"\nSelected Action:\n{selected_action}", 'info', 'Actions')
            else:
                self.logger.log(f"\nCrafting Action for Objective:\n{objective}", 'info', 'Actions')
                selected_action = self.craft_action_for_objective(objective=objective,
                                                                  context=context,
                                                                  format_result=True)
                self.logger.log(f"\nCrafted Action:\n{selected_action}", 'info', 'Actions')

            tools = self.parse_action_tools(selected_action)

            if tools:
                result = self.run_tools_in_sequence(objective=objective,
                                                    action=selected_action,
                                                    tools=tools)
                # Check if an error occurred
                if isinstance(result, Dict) and 'error' in result:
                    self.logger.log(f"\nAction Result:\n{result['error']}", 'error', 'Actions')
                    return result  # Stop execution and return the error message

                self.logger.log(f"\nAction Result:\n{result}", 'info', 'Actions')
                return result

            error_message = f"No Tools in Selected Action:\n{selected_action}"
            self.logger.log(error_message, 'error', 'Actions')
            return {'error': error_message, 'traceback': None}
        except Exception as e:
            error_message = f"Error in running action: {e}"
            self.logger.log(error_message, 'error', 'Actions')
            return {'error': error_message, 'traceback': traceback.format_exc()}
