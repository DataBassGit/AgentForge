import os
from termcolor import cprint
from colorama import init
init(autoreset=True)


def encode_msg(msg):
    return msg.encode('utf-8', 'replace').decode('utf-8')


class Printing:

    @staticmethod
    def print_message(msg):
        try:
            encoded_msg = encode_msg(msg)  # Utilize the existing encode_msg function
            cprint(encoded_msg, 'red', attrs=['bold'])
        except Exception as e:
            print(f"Error in print_message: {e}")

    @staticmethod
    def print_result(result, desc):
        try:
            # Print the task result
            cprint(f"***** {desc} *****", 'green', attrs=['bold'])
            cprint(encode_msg(result), 'white')
            cprint("*****", 'green', attrs=['bold'])

            # Save the result to a log.txt file in the /Logs/ folder
            log_folder = "Logs"
            log_file = "log.txt"

            # Create the Logs folder if it doesn't exist
            if not os.path.exists(log_folder):
                os.makedirs(log_folder)

            # Save the result to the log file
            Printing.write_file(log_folder, log_file, result)
        except OSError as e:
            print(f"File operation error in print_result: {e}")
        except Exception as e:
            print(f"Error in print_result: {e}")

    @staticmethod
    def write_file(folder, filename, content):
        try:
            with open(os.path.join(folder, filename), "a") as file:  # 'a' mode for appending
                file.write(f"{content}\n")
        except OSError as e:
            print(f"Error writing to file {filename}: {e}")
        except Exception as e:
            print(f"Unexpected error in write_file: {e}")
