from termcolor import cprint
from colorama import init
init(autoreset=True)


def encode_msg(msg):
    return msg.encode('utf-8', 'replace').decode('utf-8')


class Printing:

    @staticmethod
    def print_message(msg):
        encoded_msg = msg.encode('utf-8', 'replace').decode('utf-8')
        cprint(f"{encode_msg(msg)}", 'red', attrs=['bold'])

    @staticmethod
    def print_result(result, desc):
        # Print the task result
        cprint(f"***** {desc} *****", 'green', attrs=['bold'])
        cprint(f"{encode_msg(result)}", 'white')
        cprint(f"*****", 'green', attrs=['bold'])

        # # Save the result to a log.txt file in the /Logs/ folder
        # log_folder = "Logs"
        # log_file = "log.txt"

        # Create the Logs folder if it doesn't exist
        # if not os.path.exists(log_folder):
        #     os.makedirs(log_folder)

        # Save the result to the log file
        # self.write_file(log_folder, log_file, result)