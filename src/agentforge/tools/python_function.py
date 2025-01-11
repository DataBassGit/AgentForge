# tools/python_function.py

from agentforge.utils.tool_utils import ToolUtils


class PythonFunction:
    """
    A class for executing Python functions dynamically.

    This class provides a method to execute Python functions specified by name,
    using the ToolUtils class for dynamic execution.

    Attributes:
        None

    Raises:
        Exception: If any method in this class fails to execute properly.
    """

    def __init__(self):
        """
        Initialize the PythonFunction object.

        This method currently doesn't set up any attributes but is included for future extensibility.
        """
        pass

    @staticmethod
    def execute_function(function_name, payload):
        """
        Execute a Python function specified by name.

        This method uses the ToolUtils class to dynamically execute a Python function
        specified by its name. The function should be available in the current Python environment.

        Args:
            function_name (str): The name of the Python function to execute.
            payload (dict): A dictionary containing the arguments to pass to the function.

        Returns:
            Any: The result of the executed function.

        Raises:
            ValueError: If the function_name is not a string or is empty.
            TypeError: If the payload is not a dictionary.
            AttributeError: If the specified function is not found.
            Exception: For any other unexpected errors during execution.
        """
        if not isinstance(function_name, str) or not function_name.strip():
            raise ValueError("function_name must be a non-empty string")

        if not isinstance(payload, dict):
            raise TypeError("payload must be a dictionary")

        try:
            tool = {'Script': function_name, 'Command': 'execute'}
            result = ToolUtils().dynamic_tool(tool, payload)
            return result
        except AttributeError as e:
            raise AttributeError(f"Function '{function_name}' not found: {str(e)}")
        except Exception as e:
            raise Exception(f"An error occurred while executing the function: {str(e)}")

# Usage example (commented out)
# if __name__ == "__main__":
#     def example_function(x, y):
#         return x + y
#
#     try:
#         python_function = PythonFunction()
#         result = python_function.execute_function('example_function', {'x': 5, 'y': 3})
#         print(f"Result: {result}")
#     except Exception as e:
#         print(f"Error: {str(e)}")

