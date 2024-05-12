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

    def dynamic_tool(self, tool_module, payload):
        """
        Dynamically loads a tool module and executes a specified command within it, using arguments provided in the
        payload.

        Parameters:
            tool_module (str): The module path of the tool to be dynamically imported.
            payload (dict): A dictionary containing the 'command' to be executed and 'args' for the command.

        Returns:
            Any: The result of executing the command within the tool, or None if an error occurs.

        Raises:
            ModuleNotFoundError: If the specified tool module cannot be found.
            AttributeError: If the specified class or command does not exist within the module.
            TypeError: If there is a mismatch in the expected arguments for the command.
            Exception: For general errors encountered during command execution.
        """
        # Extract the actual class name from the tool_class path
        tool_class = tool_module.split('.')[-1]
        command = payload['command']
        args = payload['args']

        self.logger.log_info(f"\nRunning {tool_class} ...")

        try:
            tool = importlib.import_module(tool_module)
        except ModuleNotFoundError as e:
            self.logger.log(f"No tool module named '{tool_module}' found. Ensure the Module name matches the Script "
                            f"name exactly.\nError: {e}", 'critical')
            return None

        try:
            # Check if the tool has a class name
            # If it does, instantiate it, and then use the command method
            # Else, use the standalone function
            if hasattr(tool, tool_class):
                tool_instance = getattr(tool, tool_class)()
                command_func = getattr(tool_instance, command)
            else:
                command_func = getattr(tool, command)

            result = command_func(**args)
            self.logger.log_result(result, f"{tool_class} Result")
            return result
        except AttributeError as e:
            self.logger.log(f"Tool '{tool_module}' does not have a class named '{tool_class}' "
                            f"or command named '{command}'.\nError: {e}", 'error')
            return None
        except TypeError as e:
            self.logger.log(f"Error passing arguments: {e}", 'error')
            return None
        except Exception as e:
            self.logger.log(f"Error executing command: {e}", 'error')
            return None

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
