from agentforge.utils.functions.ToolUtils import ToolUtils

class PythonFunction:

    def __init__(self):
        pass

    @staticmethod
    def execute_function(function_name, payload):
        tool = ToolUtils.dynamic_tool()
        result = tool(function_name, payload)
        return result
