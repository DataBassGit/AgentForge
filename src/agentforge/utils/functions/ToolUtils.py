import importlib
from .Printing import Printing


class ToolUtils:

    def __init__(self):
        self.printing = Printing()

    def dynamic_tool(self, tool_module, payload):
        # Extract the actual class name from the tool_class path
        tool_class = tool_module.split('.')[-1]
        command = payload['command']
        args = payload['args']

        self.printing.print_message(f"\nRunning {tool_class} ...")

        try:
            tool = importlib.import_module(tool_module)
        except ModuleNotFoundError:
            raise ValueError(
                f"No tool module named '{tool_module}' found. Ensure the Module name matches the Script name exactly.")

        # Check if the tool has a class named
        # If it does, instantiate it, and then use the command method
        # Else, use the standalone function
        if hasattr(tool, tool_class):
            tool_instance = getattr(tool, tool_class)()
            command_func = getattr(tool_instance, command)
        else:
            command_func = getattr(tool, command)

        result = command_func(**args)

        self.printing.print_result(result, f"{tool_class} Result")
        return result

    def show_primed_tool(self, tool_name, payload):
        tool_name = tool_name.replace('_', ' ')
        say = payload['thoughts']['say']
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

        self.printing.print_result(formatted_string, 'Primed Tool')

