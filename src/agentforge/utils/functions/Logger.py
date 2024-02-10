import os
import logging
from ...config import Config
from agentforge.utils.functions.UserInterface import UserInterface

from termcolor import cprint
from colorama import init
init(autoreset=True)


def encode_msg(msg):
    return msg.encode('utf-8', 'replace').decode('utf-8')


class BaseLogger:
    # Class-level dictionaries to track existing handlers
    file_handlers = {}
    console_handlers = {}

    def __init__(self, name='BaseLogger', log_file='default.log'):
        self.logger = logging.getLogger(name)
        self.log_file = log_file
        self._setup_file_handler()
        self._setup_console_handler()

    def _setup_file_handler(self):
        if self.log_file in BaseLogger.file_handlers:
            # Use the existing file handler
            fh = BaseLogger.file_handlers[self.log_file]
            self.logger.addHandler(fh)
            return

        self.logger.setLevel(logging.DEBUG)  # Default level, can be customized

        # Define the relative path for the log directory
        log_folder = "Logs"
        # Create the Logs folder if it doesn't exist
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)

        # File handler for logs
        log_file_path = f'{log_folder}/{self.log_file}'
        fh = logging.FileHandler(log_file_path)
        fh.setLevel(logging.ERROR)  # Set the level for file handler
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %('
                                      'message)s\n-------------------------------------------------------------',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        # Store the file handler in the class-level dictionary
        BaseLogger.file_handlers[self.log_file] = fh

    def _setup_console_handler(self):
        if self.logger.name in BaseLogger.console_handlers:
            # Use the existing console handler
            ch = BaseLogger.console_handlers[self.logger.name]
            self.logger.addHandler(ch)
            return

        # Console handler for logs
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)  # Set the level for console handler
        formatter = logging.Formatter('%(levelname)s: %(message)s\n')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

        # Store the console handler in the class-level dictionary
        BaseLogger.console_handlers[self.logger.name] = ch

    def log_msg(self, msg, level='info'):
        level_code = self._get_level_code(level)

        if level_code == logging.DEBUG:
            self.logger.debug(msg)
        elif level_code == logging.INFO:
            self.logger.info(msg)
        elif level_code == logging.WARNING:
            self.logger.warning(msg)
        elif level_code == logging.ERROR:
            self.logger.error(msg)
        elif level_code == logging.CRITICAL:
            self.logger.critical(msg)
        else:
            raise ValueError(f'Invalid log level: {level}')

    def set_level(self, level):
        level_code = self._get_level_code(level)
        self.logger.setLevel(level_code)
        for handler in self.logger.handlers:
            handler.setLevel(level_code)

    @staticmethod
    def _get_level_code(level):
        level_dict = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL,
        }
        return level_dict.get(level.lower(), logging.INFO)


class Logger:
    def __init__(self, name, general_log_name='agentforge', model_log_name='model_io', results_log_name='results'):
        self.caller_name = name  # This will store the __name__ of the script that instantiated the Logger
        # Initialize loggers and store them in a list
        self.loggers = {
            'general': BaseLogger(name=general_log_name, log_file=f'{general_log_name}.log'),
            'model': BaseLogger(name=model_log_name, log_file=f'{model_log_name}.log'),
            'results': BaseLogger(name=results_log_name, log_file=f'{results_log_name}.log'),
        }

    @staticmethod
    def initialize_logging():
        # Save the result to a log.txt file in the /Logs/ folder
        log_folder = "Logs"

        # Create the Logs folder if it doesn't exist
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)

    def log(self, msg, level='info', logger_type='general'):
        # Allow logging to a specific logger or all loggers
        # Prepend the caller's module name to the log message
        msg_with_caller = f'[{self.caller_name}] {msg}'
        if logger_type == 'all':
            for logger in self.loggers.values():
                logger.log_msg(msg_with_caller, level)
        else:
            self.loggers[logger_type].log_msg(msg_with_caller, level)

    def log_prompt(self, prompt):
        self.log(f'Prompt:\n{prompt}', 'debug', 'model')

    def log_response(self, response):
        self.log(f'Model Response:\n{response}', 'debug', 'model')

    def set_level(self, level, logger_type='all'):
        # Apply log level to selected logger(s)
        if logger_type == 'all':
            for logger in self.loggers.values():
                logger.set_level(level)
        else:
            self.loggers[logger_type].set_level(level)

    def parsing_error(self, model_response, error):
        self.log(f"Parsing Error - It is very likely the model did not respond in the required "
                 f"format\n\nModel Response:\n{model_response}\n\nError: {error}", 'error')

    def log_result(self, result, desc):
        try:
            # Print the task result
            cprint(f"***** {desc} *****", 'green', attrs=['bold'])
            cprint(encode_msg(result), 'white')
            cprint("*****", 'green', attrs=['bold'])

            # Create the Logs folder if it doesn't exist
            self.initialize_logging()

            # Save the result to the log file
            self.log(f'\n{result}', 'info', 'results')
            # Printing.write_file(log_folder, log_file, result)
        except OSError as e:
            self.log(f"File operation error: {e}", 'error')
        except Exception as e:
            self.log(f"Error logging result: {e}", 'error')

    def log_info(self, msg):
        try:
            # Create the Logs folder if it doesn't exist
            self.initialize_logging()

            encoded_msg = encode_msg(msg)  # Utilize the existing encode_msg function
            cprint(encoded_msg, 'red', attrs=['bold'])
            self.log(f'\n{encoded_msg}', 'info', 'results')
        except Exception as e:
            self.log(f"Error logging message: {e}", 'error')


