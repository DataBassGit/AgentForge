import subprocess


class CommandExecutor:
    def __init__(self):
        pass

    def execute(self, cmd: str, env_vars: dict = None) -> str:
        """
        Execute a command and return its output.
        If there's an error during execution, it will return the error message.

        Parameters:
        - cmd: Command to be executed.
        - env_vars: Optional dictionary containing environment variables to be set for the command.

        Returns:
        - Command output as a string.
        """
        # Setting the shell=True allows for command chaining (&, &&, ||, ;)
        # But also be cautious about its usage with untrusted input due to security reasons.
        environment = dict(os.environ, **(env_vars or {}))

        try:
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, env=environment)
            return output.decode('utf-8')
        except subprocess.CalledProcessError as e:
            # In case of an error, return the error output.
            return e.output.decode('utf-8')
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"


# Usage
# if __name__ == "__main__":
#     executor = CommandExecutor()
#
#     # Single command
#     print(executor.execute("echo Hello, World!"))
#
#     # Command chaining
#     print(executor.execute("echo Hello, World! && echo Goodbye, World!"))
#
#     # With environment variables
#     print(executor.execute("echo $MY_VAR", env_vars={"MY_VAR": "Hello from env vars!"}))
