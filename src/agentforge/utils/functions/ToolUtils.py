# utils/functions/ToolUtils.py
import traceback
import importlib
from .Logger import Logger
from typing import Any, Dict


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

# import traceback
# import importlib
# from .Logger import Logger
#
#
# class ToolUtils:
#     """
#     A utility class for dynamically interacting with tools. It supports dynamically importing tool modules,
#     executing specified commands within those modules, and handling tool priming for display purposes.
#
#     Attributes:
#         logger (Logger): Logger instance for logging messages.
#     """
#
#     def __init__(self):
#         """
#         Initializes the ToolUtils class with a Logger instance.
#         """
#         self.logger = Logger(name=self.__class__.__name__)
#
#     def dynamic_tool(self, tool, payload):
#         """
#         Dynamically loads a tool module and executes a specified command within it, using arguments provided in the
#         payload.
#
#         Parameters:
#             tool (dict): The tool to be dynamically imported.
#             payload (dict): A dictionary containing the 'command' to be executed and 'args' for the command.
#
#         Returns:
#             Any: The result of executing the command within the tool, or an error dictionary if an error occurs.
#
#         Raises:
#             ModuleNotFoundError: If the specified tool module cannot be found.
#             AttributeError: If the specified class or command does not exist within the module.
#             TypeError: If there is a mismatch in the expected arguments for the command.
#             Exception: For general errors encountered during command execution.
#         """
#         tool_module = tool.get('Script')
#         tool_class = tool_module.split('.')[-1]
#         command = tool.get('Command')
#         args = payload['args']
#         error_message: str
#         self.logger.log_info(f"\nRunning {tool_class} ...")
#
#         try:
#             if tool_module in ['print', 'len', 'sum', 'max', 'min']:  # Add more built-in functions if needed
#                 command_func = eval(tool_module)
#                 result = command_func(**args)
#             else:
#                 tool = importlib.import_module(tool_module)
#                 if hasattr(tool, tool_class):
#                     tool_instance = getattr(tool, tool_class)()
#                     command_func = getattr(tool_instance, command)
#                 else:
#                     command_func = getattr(tool, command)
#
#                 result = command_func(**args)
#
#             self.logger.log(f'\n{tool_class} Result:\n{result}', 'info', 'Actions')
#             return {'status': 'success', 'data': result}
#         except AttributeError as e:
#             error_message = f"Tool '{tool_module}' does not have a class named '{tool_class}' " \
#                             f"or command named '{command}'.\nError: {e}"
#             self.logger.log(error_message, 'error')
#             return {'status': 'failure', 'message': error_message, 'traceback': traceback.format_exc()}
#         except TypeError as e:
#             error_message = f"Error passing arguments: {e}"
#             self.logger.log(error_message, 'error')
#             return {'status': 'failure', 'message': error_message, 'traceback': traceback.format_exc()}
#         except Exception as e:
#             error_message = f"Error executing command: {e}"
#             self.logger.log(error_message, 'error')
#             return {'status': 'failure', 'message': error_message, 'traceback': traceback.format_exc()}
