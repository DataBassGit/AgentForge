from termcolor import cprint
from colorama import init
init(autoreset=True)


class Printing:

    @staticmethod
    def print_message(msg):
        cprint(f"{msg}", 'red', attrs=['bold'])

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