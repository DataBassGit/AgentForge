# utils/functions/ToolUtils.py
import traceback
import importlib
from typing import List, Dict, Optional, Union
from .Logger import Logger
from typing import Any, Dict

from agentforge.utils.chroma_utils import ChromaUtils


class ToolUtils:
    """
    A utility class for dynamically interacting with tools. It supports dynamically importing tool modules,
    executing specified commands within those modules, and handling tool priming for display purposes.

    Attributes:
        logger (Logger): Logger instance for logging messages.
    """

    BUILTIN_FUNCTIONS = {
        'print': print,
        'len': len,
        'sum': sum,
        'max': max,
        'min': min
        # Add more built-in functions if needed
    }

    def __init__(self):
        """
        Initializes the ToolUtils class with a Logger instance.
        """
        self.logger = Logger(name=self.__class__.__name__)
        self.storage = ChromaUtils('default')

    # --------------------------------------------------------------------------------------------------------
    # ----------------------------------------- Dynamic Tool Methods -----------------------------------------
    # --------------------------------------------------------------------------------------------------------

    def dynamic_tool(self, tool: Dict[str, str], payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dynamically loads a tool module and executes a specified command within it, using arguments provided in the
        payload.

        Parameters:
            tool (dict): The tool to be dynamically imported.
            payload (dict): A dictionary containing the 'command' to be executed and 'args' for the command.

        Returns:
            dict: The result of executing the command within the tool, or an error dictionary if an error occurs.
        """
        tool_module = tool.get('Script')
        tool_class = tool_module.split('.')[-1]
        command = tool.get('Command')
        args = payload['args']
        self.logger.log_info(f"\nRunning {tool_class} ...")

        try:
            result = self._execute_tool(tool_module, tool_class, command, args)
            self.logger.log(f'\n{tool_class} Result:\n{result}', 'info', 'Actions')
            return {'status': 'success', 'data': result}
        except (AttributeError, TypeError, Exception) as e:
            return self._handle_error(e, tool_module, tool_class, command)

    def _execute_tool(self, tool_module: str, tool_class: str, command: str, args: Dict[str, Any]) -> Any:
        """
        Executes the specified command within the tool module.

        Parameters:
            tool_module (str): The tool module to be imported.
            tool_class (str): The class within the tool module.
            command (str): The command to be executed.
            args (dict): The arguments for the command.

        Returns:
            Any: The result of executing the command.
        """
        if tool_module in self.BUILTIN_FUNCTIONS:
            command_func = self.BUILTIN_FUNCTIONS[tool_module]  # type: ignore
            result = command_func(**args)
        else:
            tool = importlib.import_module(tool_module)
            if hasattr(tool, tool_class):
                tool_instance = getattr(tool, tool_class)()
                command_func = getattr(tool_instance, command)
            else:
                command_func = getattr(tool, command)

            result = command_func(**args)

        return result

    def _handle_error(self, e: Exception, tool_module: str, tool_class: str, command: str) -> Dict[str, Any]:
        """
        Handles errors encountered during command execution.

        Parameters:
            e (Exception): The exception raised.
            tool_module (str): The tool module where the error occurred.
            tool_class (str): The class within the tool module where the error occurred.
            command (str): The command that caused the error.

        Returns:
            dict: An error dictionary with the error message and traceback.
        """
        if isinstance(e, AttributeError):
            error_message = f"Tool '{tool_module}' does not have a class named '{tool_class}' or command named '{command}'.\nError: {e}"
        elif isinstance(e, TypeError):
            error_message = f"Error passing arguments: {e}"
        else:
            error_message = f"Error executing command: {e}"

        self.logger.log(error_message, 'error')
        return {'status': 'failure', 'message': error_message, 'traceback': traceback.format_exc()}

    # --------------------------------------------------------------------------------------------------------
    # ----------------------------------------- Tool Helper Methods ------------------------------------------
    # --------------------------------------------------------------------------------------------------------

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

    def get_tool_list(self, parse_result: bool = True) -> Optional[Dict[str, Union[List[str], None, List[Dict]]]]:
        """
        Retrieves the list of tools from storage.

        Parameters:
            parse_result (bool): Whether to parse the tool list for easier handling. Default is True.

        Returns:
            Optional[Dict[str, Union[List[str], None, List[Dict]]]]: A dictionary containing all tool information,
            or None if there are no tools.
        """
        tool_list = self.storage.load_collection('Tools')

        if parse_result:
            tool_list = self.parse_item_list(tool_list)

        return tool_list

    def query_tool_list(self, num_results: int = 20, query: str = None,
                        filter_condition: Dict = None, parse_result: bool = True) -> Optional[Dict[str, Dict]]:
        """
        Retrieves the list of tools from storage using query_memory.

        Parameters:
            num_results (int): The maximum number of tools to return.
            query (str, optional): A query string to search for specific tools.
            filter_condition (Dict, optional): A dictionary specifying filter conditions for the query.
            parse_result (bool): Whether to parse the tool list for easier handling. Default is True.

        Returns:
            Optional[Dict[str, Dict]]: A dictionary containing tool information,
            or None if there are no tools or an error occurs.
        """
        try:
            collection_name = 'Tools'
            
            # Use query_memory instead of load_collection
            tool_list = self.storage.query_memory(
                collection_name=collection_name,
                query=query,
                filter_condition=filter_condition,
                include=["documents", "metadatas"],
                num_results=num_results
            )

            if not tool_list or 'documents' not in tool_list:
                self.logger.log(f"No tools found in the {collection_name} collection.", 'warning')
                return None

            # Parse the results
            if parse_result:
                tool_list = self.parse_item_list(tool_list)

            return tool_list

        except Exception as e:
            self.logger.log(f"Error in get_tool_list: {e}", 'error')
            return None

    # --------------------------------------------------------------------------------------------------------
    # ------------------------------------ Parsing and Formatting Methods ------------------------------------
    # --------------------------------------------------------------------------------------------------------

    @staticmethod
    def format_item(item: Dict[str, Union[str, List[str]]],
                    order: Optional[List[str]] = None) -> str:
        """
        Formats an item (action or tool) into a human-readable string.

        Parameters:
            item (Dict[str, Union[str, List[str]]]): The item to format.
            order (Optional[List[str]]): The order in which to format the item's keys.

        Returns:
            str: The formatted item string.
        """
        if order is None:
            order = list(item.keys())

        formatted_string = ""
        for key in order:
            if key in item:
                value = item[key]
                if isinstance(value, list):
                    formatted_list = "\n- ".join([str(items).strip() for items in value])
                    formatted_string += f"{key}:\n- {formatted_list}\n\n"
                elif isinstance(value, str):
                    if len(value.splitlines()) > 1:
                        formatted_string += f"{key}:\n{value.strip()}\n\n"
                    else:
                        formatted_string += f"{key}: {value.strip()}\n"
        return formatted_string.strip()

    def format_item_list(self, items: Dict, order: Optional[List[str]] = None) -> Optional[str]:
        """
        Formats the actions into a human-readable string based on a given order and stores it in the agent's data for
        later use.

        Parameters:
            items (Dict): The list of actions or tools to format.
            order (Optional[List[str]]): The order in which to format the action's keys.

        Returns:
            Optional[str]: The formatted string of actions, or None if an error occurs.
        """
        try:
            formatted_actions = []
            for item_name, metadata in items.items():
                formatted_action = self.format_item(metadata, order)
                formatted_actions.append(formatted_action)
            return "---\n" + "\n---\n".join(formatted_actions) + "\n---"
        except Exception as e:
            self.logger.log(f"Error Formatting Item List:\n{items}\n\nError: {e}", 'error', 'Actions')
            return None

    def parse_item_list(self, item_list: Dict) -> Optional[Dict[str, Dict]]:
        """
        Parses and structures the actions fetched from storage for easier handling and processing.

        Parameters:
            item_list (Dict): The list of actions or tools to parse.

        Returns:
            Optional[Dict[str, Dict]]: A dictionary of parsed actions, or None if an error occurs.
        """
        parsed_list = {}
        try:
            for metadata in item_list.get("metadatas", []):
                metadata_name = metadata.get("Name")
                if metadata_name:
                    parsed_list[metadata_name] = metadata
            return parsed_list
        except Exception as e:
            self.logger.log(f"Error Parsing Item:\n{item_list}\n\nError: {e}", 'error', 'Actions')
            return None

    def parse_tools_in_action(self, action: Dict) -> List[Dict] | None:
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
            error_message = f"Error in loading tools from action '{action['Name']}': {e}"
            self.logger.log(error_message, 'error', 'Actions')
            tools = {'error': error_message, 'traceback': traceback.format_exc()}

        return tools
