# import os
from termcolor import colored, cprint
from colorama import init
init(autoreset=True)


class Printing:

    @staticmethod
    def print_message(msg):
        cprint(f"{msg}", 'red', attrs=['bold'])

    def print_primed_tool(self, tool_name, payload):
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

        self.print_result(formatted_string, 'Primed Tool')

    @staticmethod
    def print_result(result, desc):
        # Print the task result
        cprint(f"***** {desc} *****", 'green', attrs=['bold'])
        print(result)
        cprint(f"*****", 'green', attrs=['bold'])

        # # Save the result to a log.txt file in the /Logs/ folder
        # log_folder = "Logs"
        # log_file = "log.txt"

        # Create the Logs folder if it doesn't exist
        # if not os.path.exists(log_folder):
        #     os.makedirs(log_folder)

        # Save the result to the log file
        # self.write_file(log_folder, log_file, result)