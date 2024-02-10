import os
import logging
import pathlib
from ..utils.functions.UserInterface import UserInterface

from termcolor import cprint
from colorama import init
init(autoreset=True)


def encode_msg(msg):
    return msg.encode('utf-8', 'replace').decode('utf-8')

class Logger:
    _logger = None
    name = None

    def __init__(self, name='AgentForge', log_file=pathlib.Path(__file__).parent / 'AgentForge.log'):

        self.UI = UserInterface()
        self._logger = logging.getLogger(name)

        if not self._logger.handlers:
            self._logger.setLevel(logging.DEBUG)  # or whatever level you want

            # create file handler which logs messages
            fh = logging.FileHandler(log_file)
            fh.setLevel(logging.DEBUG)  # or whatever level you want

            # create console handler with a higher log level
            ch = logging.StreamHandler()
            ch.setLevel(logging.ERROR)  # or whatever level you want

            # create formatter and add it to the handlers
            formatter = logging.Formatter('LOGGER - %(name)s - %(message)s')
            ch.setFormatter(formatter)
            fh.setFormatter(formatter)

            # add the handlers to logger
            self._logger.addHandler(ch)
            self._logger.addHandler(fh)

    def get_level_code(self, level):
        """
        Translates a log level string into the logging module's log level code.

        Args:
            level (str): Logging level as a string, e.g., 'debug', 'info', etc.

        Returns:
            int: The logging module's corresponding log level code.
        """
        level_dict = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL,
        }

        if level.lower() not in level_dict:
            self.log("Invalid log level: '{}'. Setting log level to 'info'.".format(level), 'warning')
            level = 'info'

        return level_dict.get(level.lower(), logging.INFO)

    def set_level(self, level):
        """
        Sets the logging level for the logger and its handlers.

        Args:
            level (str): Logging level as a string, e.g., 'debug', 'info', etc.
        """
        level_code = self.get_level_code(level)
        self._logger.setLevel(level_code)

        for handler in self._logger.handlers:
            handler.setLevel(level_code)

    def log(self, msg, level='info'):
        msg = str(msg) + '\n'  # Add a new line at the end of each message

        if level == 'debug':
            self._logger.debug(msg)
        elif level == 'info':
            self._logger.info(msg)
        elif level == 'warning':
            self._logger.warning(msg)
        elif level == 'error':
            self._logger.error(msg)
            self.UI.user_input_on_error()
        elif level == 'critical':
            self._logger.critical(msg)
            raise
        else:
            raise ValueError('Invalid log level: {}'.format(level))

    def log_prompt(self, prompt):
        self.log(f'Prompt:\n{prompt}', 'debug')

    def log_response(self, response):
        self.log(f'Model Response:\n{response}', "debug")

    def parsing_error(self, model_response, error):
        self.log(f"Parsing Error - It is very likely the model did not respond in the required "
                 f"format\n\nModel Response:\n{model_response}\n\nError: {error}", 'error')

    def print_result(self, result, desc):
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
            self.log(f'Model Response:\n{response}', "debug")
            self.write_file(log_folder, log_file, result)
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

# ----------------------------------------------------------------------------------------------------
# Example usage:
# logger = Logger(name="ethos_tester.py")
# logger.set_level('debug')

# current_level = logger.get_current_level()

# logger.log('debug message') -> default, meaning it will always print
# logger.log('debug', 'debug message')
# logger.log('info', 'info message')
# logger.log('warning', 'warning message')
# logger.log('error', 'error message')
# logger.log('critical', 'critical message')
