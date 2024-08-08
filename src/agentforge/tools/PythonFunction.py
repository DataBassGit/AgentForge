# tools/PythonFunction.py

from agentforge.utils.functions.ToolUtils import ToolUtils


class PythonFunction:

    def __init__(self):
        pass

    @staticmethod
    def execute_function(function_name, payload):
        tool = {'Script': function_name, 'Command': 'execute'}
        result = ToolUtils().dynamic_tool(tool, payload)
        return result

