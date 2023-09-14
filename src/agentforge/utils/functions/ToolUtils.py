from .Printing import Printing


class ToolUtils:

    def __init__(self):
        self.printing = Printing()

    def dynamic_tool(self, tool_class, payload):
        import importlib
        self.printing.print_message(f"\nRunning {tool_class} ...")

        command = payload['command']['name']
        args = payload['command']['args']
        tool_module = f"agentforge.tools.{tool_class}"

        try:
            tool = importlib.import_module(tool_module)
        except ModuleNotFoundError:
            raise ValueError(
                f"No tool module named '{tool_class}' found. Ensure the module name matches the Script name exactly.")

        # Check if the tool has a class named FileWriter (or any other tool name)
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
        speak = payload['thoughts']['speak']
        reasoning = payload['thoughts']['reasoning']

        # Format command arguments
        command_args = ", ".join(
            [f"{k}='{v}'" if isinstance(v, str) else f"{k}={v}" for k, v in payload['command']['args'].items()]
        )

        command = f"{payload['command']['name']}({command_args})"

        # Create the final output string
        formatted_string = f"{speak}\n\n" \
                           f"Tool: {tool_name}\n" \
                           f"Command: {command}\n" \
                           f"Reasoning: {reasoning}"

        self.printing.print_result(formatted_string, 'Primed Tool')

