import subprocess
import os


class CommandExecutor:
    """
    A class for executing shell commands safely.

    This class provides a method to execute shell commands and return their output.
    It includes error handling and environment variable support.

    Attributes:
        None

    Raises:
        Exception: If any method in this class fails to execute properly.
    """

    def __init__(self):
        """
        Initialize the CommandExecutor.

        This method currently doesn't set up any attributes but is included for future extensibility.
        """
        pass

    def execute(self, cmd: str, env_vars: dict = None) -> str:
        """
        Execute a command and return its output.

        This method executes the given command in a shell environment and returns the output.
        It supports command chaining and custom environment variables.

        Args:
            cmd (str): Command to be executed.
            env_vars (dict, optional): Dictionary containing environment variables to be set for the command.

        Returns:
            str: Command output as a string.

        Raises:
            ValueError: If the input command is not a string or is empty.
            subprocess.CalledProcessError: If the command execution fails.
            Exception: For any other unexpected errors during execution.
        """
        if not isinstance(cmd, str) or not cmd.strip():
            raise ValueError("Command must be a non-empty string")

        if env_vars is not None and not isinstance(env_vars, dict):
            raise ValueError("env_vars must be a dictionary or None")

        # Setting the shell=True allows for command chaining (&, &&, ||, ;)
        # But also be cautious about its usage with untrusted input due to security reasons.
        environment = dict(os.environ, **(env_vars or {}))

        try:
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, env=environment)
            return output.decode('utf-8')
        except subprocess.CalledProcessError as e:
            # In case of an error, return the error output.
            raise Exception(f"Command execution failed: {e.output.decode('utf-8')}") from e
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {str(e)}") from e


# Usage example (commented out)
# if __name__ == "__main__":
#     executor = CommandExecutor()
#
#     try:
#         # Single command
#         print(executor.execute("echo Hello, World!"))
#
#         # Command chaining
#         print(executor.execute("echo Hello, World! && echo Goodbye, World!"))
#
#         # With environment variables
#         print(executor.execute("echo $MY_VAR", env_vars={"MY_VAR": "Hello from env vars!"}))
#     except Exception as e:
#         print(f"Error: {str(e)}")
