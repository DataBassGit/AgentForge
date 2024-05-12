import os
import logging
from ...config import Config
from ...utils.functions.UserInterface import UserInterface

from termcolor import cprint
from colorama import init
init(autoreset=True)


def encode_msg(msg):
    return msg.encode('utf-8', 'replace').decode('utf-8')


class BaseLogger:
    """
    A base logger class for setting up file and console logging with support for multiple handlers and log levels.

    This class provides mechanisms for initializing file and console log handlers, logging messages at various
    levels, and dynamically adjusting log levels.

    Attributes:
        file_handlers (dict): A class-level dictionary tracking file handlers by log file name.
        console_handlers (dict): A class-level dictionary tracking console handlers by logger name.
    """

    # Class-level dictionaries to track existing handlers
    file_handlers = {}
    console_handlers = {}

    def __init__(self, name='BaseLogger', log_file='default.log', log_level='error'):
        """
        Initializes the BaseLogger with optional name, log file, and log level.

        Parameters:
            name (str): The name of the logger.
            log_file (str): The name of the file to log messages to.
            log_level (str): The initial log level for the logger.
        """
        self.config = Config()
        self.UI = UserInterface()

        # Retrieve the logging enabled flag from configuration
        logging_enabled = self.config.data['settings']['system']['Logging']['Enabled']

        level = self._get_level_code(log_level)
        self.logger = logging.getLogger(name)
        self.log_folder = None
        self.log_file = log_file

        # Conditional setup based on logging enabled flag
        if logging_enabled:
            self._setup_file_handler(level)
            self._setup_console_handler(level)
            self.logger.setLevel(level)
            return

        # If logging is disabled, set the logger level to NOTSET or higher than CRITICAL to effectively disable it
        self.logger.setLevel(logging.CRITICAL + 1)  # Effectively disables logging

    @staticmethod
    def _get_level_code(level):
        """
        Converts a log level as a string to the corresponding logging module level code.

        Parameters:
            level (str): The log level as a string (e.g., 'debug', 'info', 'warning', 'error', 'critical').

        Returns:
            int: The logging module level code corresponding to the provided string.
        """
        level_dict = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL,
        }
        return level_dict.get(level.lower(), logging.INFO)

    def _setup_console_handler(self, level):
        """
        Sets up a console handler for logging messages to the console. Configures logging format and level.

        Parameters:
            level (int): The logging level to set for the console handler.
        """

        formatter = logging.Formatter(f'%(asctime)s - %(levelname)s - {self.log_file} - %(message)s\n',
                                      datefmt='%Y-%m-%d %H:%M:%S')

        if self.logger.name in BaseLogger.console_handlers:
            # Use the existing console handler if it's not already added to this logger
            ch = BaseLogger.console_handlers[self.logger.name]
            if ch not in self.logger.handlers:
                ch.setLevel(level)
                ch.setFormatter(formatter)
                self.logger.addHandler(ch)
            return

        # Console handler for logs
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)

        if not any(type(handler) is logging.StreamHandler for handler in self.logger.handlers):
            self.logger.addHandler(ch)

        BaseLogger.console_handlers[self.logger.name] = ch

    def _setup_file_handler(self, level):
        """
        Sets up a file handler for logging messages to a file. Initializes the log folder and file if they do not exist,
        and configures logging format and level.

        Parameters:
            level (int): The logging level to set for the file handler.
        """
        # Create the Logs folder if it doesn't exist
        self.initialize_logging()

        formatter = logging.Formatter(f'%(asctime)s - %(levelname)s - %(message)s\n'
                                      '-------------------------------------------------------------',
                                      datefmt='%Y-%m-%d %H:%M:%S')

        if self.log_file in BaseLogger.file_handlers:
            # Use the existing file handler if it's not already added to this logger
            fh = BaseLogger.file_handlers[self.log_file]
            if fh not in self.logger.handlers:
                fh.setLevel(level)
                fh.setFormatter(formatter)
                self.logger.addHandler(fh)
            return

        # File handler for logs
        log_file_path = f'{self.log_folder}/{self.log_file}'
        fh = logging.FileHandler(log_file_path, encoding='utf-8')
        fh.setLevel(level)
        fh.setFormatter(formatter)

        # Check if a similar handler is already attached
        if not any(isinstance(handler, logging.FileHandler) and handler.baseFilename == fh.baseFilename for handler in
                   self.logger.handlers):
            self.logger.addHandler(fh)

        # Store the file handler in the class-level dictionary
        BaseLogger.file_handlers[self.log_file] = fh

    def initialize_logging(self):
        """
        Initializes logging by ensuring the log folder exists and setting up the log folder path.
        """
        # Save the result to a log.txt file in the /Logs/ folder
        self.log_folder = self.config.data['settings']['system']['Logging']['Folder']
        self.logger.handlers = [h for h in self.logger.handlers if not isinstance(h, logging.StreamHandler)]

        # Create the Logs folder if it doesn't exist
        if not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder)
            return

    def log_msg(self, msg, level='info'):
        """
        Logs a message at the specified log level.

        Parameters:
            msg (str): The message to log.
            level (str): The level at which to log the message (e.g., 'info', 'debug', 'error').
        """
        level_code = self._get_level_code(level)

        if level_code == logging.DEBUG:
            self.logger.debug(msg)
        elif level_code == logging.INFO:
            self.logger.info(msg)
        elif level_code == logging.WARNING:
            self.logger.warning(msg)
        elif level_code == logging.ERROR:
            self.logger.error(msg)
            self.logger.exception("Exception Error Occurred!")
        elif level_code == logging.CRITICAL:
            self.logger.critical(msg)
            self.logger.exception("Critical Exception Occurred!")
            raise
        else:
            raise ValueError(f'Invalid log level: {level}')

    def set_level(self, level):
        """
        Sets the log level for the logger and its handlers.

        Parameters:
            level (str): The new log level to set (e.g., 'info', 'debug', 'error').
        """
        level_code = self._get_level_code(level)
        self.logger.setLevel(level_code)
        for handler in self.logger.handlers:
            handler.setLevel(level_code)


class Logger:
    _instances = {}
    """
    A wrapper class for managing multiple BaseLogger instances, supporting different log files and levels
    as configured in the system settings.

    This class facilitates logging across different modules and components of the application, allowing
    for specific logs for agent activities, model interactions, and results.

    Attributes:
        loggers (dict): A dictionary of BaseLogger instances keyed by log type (e.g., '.agentforge', 'modelio').
    """

    def __new__(cls, name: str):
        """
        Create a new instance of Logger if one doesn't exist, or return the existing instance.

        Parameters:
            name (str): The name of the module or component using the logger.
        """
        if name not in cls._instances:
            instance = super(Logger, cls).__new__(cls)
            cls._instances[name] = instance
            instance._initialized = False
        return cls._instances[name]

    def __init__(self, name: str):
        """
        Initializes the Logger class with names for different types of logs. Initialization will only happen once.

        Parameters:
            name (str): The name of the module or component using the logger.
        """
        if self._initialized:
            return

        self.config = Config()
        self.caller_name = name  # This will store the __name__ of the script that instantiated the Logger

        # Retrieve the logging configuration from the config data
        logging_config = self.config.data['settings']['system']['Logging']['Files']

        # Initialize loggers dynamically based on configuration settings
        self.loggers = {}
        for log_name, log_level in logging_config.items():
            log_file_name = f'{log_name}.log'
            new_logger = BaseLogger(name=f'{name}.{log_name}', log_file=log_file_name, log_level=log_level)
            self.loggers[log_name] = new_logger

        self._initialized = True

    def log(self, msg: str, level: str = 'info', logger_file: str = 'AgentForge'):
        """
        Logs a message to a specified logger or all loggers.

        Parameters:
            msg (str): The message to log.
            level (str): The log level (e.g., 'info', 'debug', 'error').
            logger_file (str): The specific logger to use, or 'all' to log to all loggers.
        """
        # Prepend the caller's module name to the log message
        msg_with_caller = f'[{self.caller_name}]\n{msg}'

        if logger_file not in self.loggers:
            raise ValueError(f"Unknown logger file '{logger_file}' - Make sure the file name is a Logging File in "
                             f"the configuration file (system.yaml).")

        self.loggers[logger_file].log_msg(msg_with_caller, level)

    def log_prompt(self, prompt: str):
        """
        Logs a prompt to the model interaction logger.

        Parameters:
            prompt (str): The prompt to log.
        """
        self.log(f'Prompt:\n{prompt}', 'debug', 'ModelIO')

    def log_response(self, response: str):
        """
        Logs a model response to the model interaction logger.

        Parameters:
            response (str): The model response to log.
        """
        self.log(f'Model Response:\n{response}', 'debug', 'ModelIO')

    def parsing_error(self, model_response: str, error: Exception):
        """
        Logs parsing errors along with the model response.

        Parameters:
            model_response (str): The model response associated with the parsing error.
            error (Exception): The exception object representing the parsing error.
        """
        self.log(f"Parsing Error - It is very likely the model did not respond in the required "
                 f"format\n\nModel Response:\n{model_response}\n\nError: {error}", 'error')

    def log_result(self, result: str, desc: str):
        """
        Logs and displays a result with a description.

        Parameters:
            result (str): The result to log and display.
            desc (str): A short description of the result.
        """
        try:
            # Print the task result
            cprint(f"***** {desc} *****", 'green', attrs=['bold'])
            cprint(encode_msg(result), 'white')
            cprint("*****", 'green', attrs=['bold'])

            # Save the result to the log file
            self.log(f'\n{result}', 'info', 'Results')
        except OSError as e:
            self.log(f"File operation error: {e}", 'error')
        except Exception as e:
            self.log(f"Error logging result: {e}", 'error')

    def log_info(self, msg: str):
        """
        Logs and displays an informational message.

        Parameters:
            msg (str): The message to log and display.
        """
        try:
            encoded_msg = encode_msg(msg)  # Utilize the existing encode_msg function
            cprint(encoded_msg, 'red', attrs=['bold'])
            self.log(f'\n{encoded_msg}', 'info', 'Results')
        except Exception as e:
            self.log(f"Error logging message: {e}", 'error')
