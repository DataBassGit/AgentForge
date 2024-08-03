# utils/functions/ToolUtils.py
import traceback
import importlib
from .Logger import Logger


class ToolUtils:
    """
    A utility class for dynamically interacting with tools. It supports dynamically importing tool modules,
    executing specified commands within those modules, and handling tool priming for display purposes.

    Attributes:
        logger (Logger): Logger instance for logging messages.
    """

    def __init__(self):
        """
        Initializes the ToolUtils class with a Logger instance.
        """
        self.logger = Logger(name=self.__class__.__name__)

    def dynamic_tool(self, tool, payload):
        """
        Dynamically loads a tool module and executes a specified command within it, using arguments provided in the
        payload.

        Parameters:
            tool (dict): The tool to be dynamically imported.
            payload (dict): A dictionary containing the 'command' to be executed and 'args' for the command.

        Returns:
            Any: The result of executing the command within the tool, or an error dictionary if an error occurs.

        Raises:
            ModuleNotFoundError: If the specified tool module cannot be found.
            AttributeError: If the specified class or command does not exist within the module.
            TypeError: If there is a mismatch in the expected arguments for the command.
            Exception: For general errors encountered during command execution.
        """
        tool_module = tool.get('Script')
        tool_class = tool_module.split('.')[-1]
        command = tool.get('Command')
        args = payload['args']

        self.logger.log_info(f"\nRunning {tool_class} ...")

        try:
            if tool_module in ['print', 'len', 'sum', 'max', 'min']:  # Add more built-in functions if needed
                command_func = eval(tool_module)
                result = command_func(**args)
                self.logger.log_result(result, f"{tool_class} Result")
                return result
            else:
                tool = importlib.import_module(tool_module)
                if hasattr(tool, tool_class):
                    tool_instance = getattr(tool, tool_class)()
                    command_func = getattr(tool_instance, command)
                else:
                    command_func = getattr(tool, command)

                result = command_func(**args)
                self.logger.log_result(result, f"{tool_class} Result")
                return result
        except AttributeError as e:
            error_message = f"Tool '{tool_module}' does not have a class named '{tool_class}' " \
                            f"or command named '{command}'.\nError: {e}"
            self.logger.log(error_message, 'error')
            return {'error': error_message, 'traceback': traceback.format_exc()}
        except TypeError as e:
            error_message = f"Error passing arguments: {e}"
            self.logger.log(error_message, 'error')
            return {'error': error_message, 'traceback': traceback.format_exc()}
        except Exception as e:
            error_message = f"Error executing command: {e}"
            self.logger.log(error_message, 'error')
            return {'error': error_message, 'traceback': traceback.format_exc()}

    def show_primed_tool(self, tool_name, payload):
        """
        Formats and logs the primed tool information for display, including the tool's name, command arguments,
        and reasoning behind the tool's use.

        Parameters:
            tool_name (str): The name of the tool being primed.
            payload (dict): A dictionary containing 'thoughts' about the tool usage and 'args' for the command.

        Raises:
            Exception: Logs an error message if an exception occurs during the formatting or logging process.
        """
        try:
            tool_name = tool_name.replace('_', ' ')
            say = payload['thoughts']['speak']
            reasoning = payload['thoughts']['reasoning']

            # Format command arguments
            command_args = ", ".join(
                [f"{k}='{v}'" if isinstance(v, str) else f"{k}={v}" for k, v in payload['args'].items()]
            )

            command = f"{command_args}"

            # Create the final output string
            formatted_string = f"{say}\n\n" \
                               f"Tool: {tool_name}\n" \
                               f"Command Args: {command}\n" \
                               f"Reasoning: {reasoning}"

            self.logger.log_result(formatted_string, 'Primed Tool')
        except Exception as e:
            self.logger.log(f"Error in showing primed tool: {e}", 'error')
            return None
