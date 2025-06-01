# =================== DEPRECATION WARNING ===================
# This module is part of the Tools/Actions system, which is DEPRECATED.
# Do NOT use in production or with untrusted input.
# See: https://github.com/DataBassGit/AgentForge/issues/116 for details.
# This functionality will be replaced in a future version with a secure implementation.
import warnings
warnings.warn(
    "agentforge.utils.tool_utils is part of the deprecated and insecure tools/actions system. Do NOT use in production. See https://github.com/DataBassGit/AgentForge/issues/116",
    DeprecationWarning
)
# ==========================================================
# utils/functions/tool_utils.py
import traceback
import importlib
from typing import List, Optional, Union
from agentforge.utils.logger import Logger
from typing import Any, Dict

from agentforge.storage.chroma_storage import ChromaStorage


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
        self.storage = ChromaStorage.get_or_create(storage_id="tool_library")

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
        tool_class = tool.get('Class')
        command = tool.get('Command')
        args = payload['args']
        self.logger.info(f"\nRunning {tool_class} ...")

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
            if tool_module.startswith('.agentforge'):
                # Remove '.agentforge' from the beginning of the path
                relative_path = tool_module.replace('.agentforge', '', 1)
                tool = importlib.import_module(relative_path, package='agentforge')
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

        self.logger.error(error_message)
        return {'status': 'failure', 'message': error_message, 'traceback': traceback.format_exc()}

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
            self.logger.error(f"Error Formatting Item List:\n{items}\n\nError: {e}")
            return None
        