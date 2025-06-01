import os
import re
import logging
import threading
from agentforge.config import Config


def encode_msg(msg: str) -> str:
    """Encodes a message to UTF-8, replacing any invalid characters."""
    return msg.encode('utf-8', 'replace').decode('utf-8')


class ColoredFormatter(logging.Formatter):
    """
    A custom logging formatter to add colors to console logs based on the log level.
    Uses ANSI escape codes for coloring without external dependencies.
    """

    COLOR_CODES = {
        logging.DEBUG: '\033[36m',     # Cyan
        logging.INFO: '\033[32m',      # Green
        logging.WARNING: '\033[33m',   # Yellow
        logging.ERROR: '\033[31m',     # Red
        logging.CRITICAL: '\033[41m',  # Red background
    }
    RESET_CODE = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        color_code = self.COLOR_CODES.get(record.levelno, self.RESET_CODE)
        message = super().format(record)
        return f"{color_code}{message}{self.RESET_CODE}"


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

    def __init__(self, name: str = 'BaseLogger', log_file: str = 'default.log', log_level: str = 'error') -> None:
        """
        Initializes the BaseLogger with optional name, log file, and log level.

        Parameters:
            name (str): The name of the logger.
            log_file (str): The name of the file to log messages to.
            log_level (str): The initial log level for the file handler.
        """
        self.config = Config()
        self.logger = logging.getLogger(name)
        self.log_folder = self.config.settings.system.logging.folder
        self.log_file = log_file

        if not self.config.settings.system.logging.enabled:
            self.logger.setLevel(logging.CRITICAL + 1)  # Disable logging
            return

        file_level = self._get_level_code(log_level)
        console_level = self._get_level_code(
            self.config.settings.system.logging.console_level
        )
        self.logger.setLevel(min(file_level, console_level))

        self._setup_file_handler(file_level)
        self._setup_console_handler(console_level)

    @staticmethod
    def _get_level_code(level: str) -> int:
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

    def _setup_console_handler(self, level: int) -> None:
        """
        Sets up a console handler for logging messages to the console. Configures logging format and level.

        Parameters:
            level (int): The logging level to set for the console handler.
        """
        formatter = ColoredFormatter('%(levelname)s: %(message)s')

        if self.logger.name in BaseLogger.console_handlers:
            ch = BaseLogger.console_handlers[self.logger.name]
            if ch not in self.logger.handlers:
                ch.setLevel(level)
                ch.setFormatter(formatter)
                self.logger.addHandler(ch)
            return

        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        BaseLogger.console_handlers[self.logger.name] = ch

    def _setup_file_handler(self, level: int) -> None:
        """
        Sets up a file handler for logging messages to a file. Initializes the log folder and file if they do not exist,
        and configures logging format and level.

        Parameters:
            level (int): The logging level to set for the file handler.
        """
        self._initialize_logging()

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s\n-------------------------------------------------------------',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        if self.log_file in BaseLogger.file_handlers:
            fh = BaseLogger.file_handlers[self.log_file]
            if fh not in self.logger.handlers:
                fh.setLevel(level)
                fh.setFormatter(formatter)
                self.logger.addHandler(fh)
            return

        log_file_path = os.path.join(self.log_folder, self.log_file)
        fh = logging.FileHandler(log_file_path, encoding='utf-8')
        fh.setLevel(level)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        BaseLogger.file_handlers[self.log_file] = fh

    def _initialize_logging(self) -> None:
        """
        Initializes logging by ensuring the log folder exists.
        """
        if not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder)

    def log_msg(self, msg: str, level: str = 'info') -> None:
        """
        Logs a message at the specified log level.

        Parameters:
            msg (str): The message to log.
            level (str): The level at which to log the message (e.g., 'info', 'debug', 'error').
        """
        level_code = self._get_level_code(level)
        self.logger.log(level_code, msg)

    def set_level(self, level: str) -> None:
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
    """
    A wrapper class for managing multiple BaseLogger instances, supporting different log files and levels
    as configured in the system settings.

    This class facilitates logging across different modules and components of the application, allowing
    for specific logs for agent activities, model interactions, and results.

    Attributes:
        _instances (dict): A dictionary of Logger instances keyed by name.
        loggers (dict): A dictionary of BaseLogger instances keyed by log type.
    """

    _instances = {}
    _lock = threading.Lock()  # Class-level lock for thread safety
    VALID_LOGGER_NAME_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

    def __new__(cls, name: str, default_logger: str = 'agentforge'):
        """
        Create a new instance of Logger if one doesn't exist, or return the existing instance.

        Parameters:
            name (str): The name of the module or component using the logger.
            default_logger (str): The default logger file to use.
        """
        with cls._lock:
            if name not in cls._instances:
                instance = super(Logger, cls).__new__(cls)
                cls._instances[name] = instance
                instance._initialized = False
        return cls._instances[name]

    def __init__(self, name: str, default_logger: str = 'agentforge') -> None:
        """
        Initializes the Logger class with names for different types of logs.
        Initialization will only happen once.

        Parameters:
            name (str): The name of the module or component using the logger.
            default_logger (str): The default logger file to use.
        """

        if self._initialized:
            return

        with Logger._lock:
            self.config = Config()
            self.caller_name = name  # Stores the __name__ of the script that instantiated the Logger
            self.default_logger = default_logger
            self.logging_config = None
            self.loggers = {}

            self.load_logging_config()

        self.update_logger_config(default_logger)
        self.init_loggers()

        self._initialized = True

    def load_logging_config(self):
        self.logging_config = self.config.settings.system.logging.files

    def update_logger_config(self, logger_file: str):
        """
        Adds a new logger to the configuration if it doesn't exist.

        Parameters:
            logger_file (str): The name of the logger file to add.
        """
        if logger_file and not self.VALID_LOGGER_NAME_PATTERN.match(logger_file):
            raise ValueError(
                f"Invalid logger_file name: '{logger_file}'. Must match pattern: {self.VALID_LOGGER_NAME_PATTERN.pattern}")

        with Logger._lock:
            if logger_file not in self.logging_config:
                self.logging_config[logger_file] = 'warning'
                self.config.save()

    def init_loggers(self):
        # Initialize loggers dynamically based on configuration settings
        self.loggers = {}
        for logger_file, log_level in self.logging_config.items():
            self.create_logger(logger_file, log_level)

    def create_logger(self, logger_file: str, log_level: str = 'warning'):
        with Logger._lock:
            logger_name = f'{self.caller_name}.{logger_file}'
            log_file_name = f'{logger_file}.log'
            new_logger = BaseLogger(name=logger_name, log_file=log_file_name, log_level=log_level)
            self.loggers[logger_file] = new_logger

    def log(self, msg: str, level: str = 'info', logger_file: str = None) -> None:
        """
        Logs a message to a specified logger.

        Parameters:
            msg (str): The message to log.
            level (str): The log level (e.g., 'info', 'debug', 'error').
            logger_file (str): The specific logger to use. If None, uses the default logger.
        """
        # Prepend the caller's module name to the log message
        msg_with_caller = f'[{self.caller_name}] {msg}'

        if logger_file is None:
            logger_file = self.default_logger

        if logger_file not in self.loggers:
            self.update_logger_config(logger_file)
            self.create_logger(logger_file)

        logger = self.loggers.get(logger_file)
        if logger:
            logger.log_msg(msg_with_caller, level)
            return

        raise ValueError(f"Logger '{logger_file}' could not be created.")

    def debug(self, msg: str, logger_file: str = None) -> None:
        """Logs a debug level message."""
        self.log(msg, level='debug', logger_file=logger_file)

    def info(self, msg: str, logger_file: str = None) -> None:
        """Logs an info level message."""
        self.log(msg, level='info', logger_file=logger_file)

    def warning(self, msg: str, logger_file: str = None) -> None:
        """Logs a warning level message."""
        self.log(msg, level='warning', logger_file=logger_file)

    def error(self, msg: str, logger_file: str = None) -> None:
        """Logs an error level message."""
        self.log(msg, level='error', logger_file=logger_file)

    def critical(self, msg: str, logger_file: str = None) -> None:
        """Logs a critical level message."""
        self.log(msg, level='critical', logger_file=logger_file)

    def log_prompt(self, model_prompt: dict) -> None:
        """
        Logs a prompt to the model interaction logger.

        Parameters:
            model_prompt (dict): A dictionary containing the model prompts.
        """
        system_prompt = model_prompt.get('system', '')
        user_prompt = model_prompt.get('user', '')
        msg = (
            f'******\nSystem Prompt\n******\n{system_prompt}\n'
            f'******\nUser Prompt\n******\n{user_prompt}\n'
            f'******'
        )
        self.debug(msg, logger_file='model_io')

    def log_response(self, response: str) -> None:
        """
        Logs a model response to the model interaction logger.

        Parameters:
            response (str): The model response to log.
        """
        msg = f'******\nModel Response\n******\n{response}\n******'
        self.debug(msg, logger_file='model_io')

    def parsing_error(self, model_response: str, error: Exception) -> None:
        """
        Logs parsing errors along with the model response.

        Parameters:
            model_response (str): The model response associated with the parsing error.
            error (Exception): The exception object representing the parsing error.
        """
        msg = (
            f"Parsing Error - The model may not have responded in the required format.\n\n"
            f"Model Response:\n******\n{model_response}\n******\n\nError: {error}"
        )
        self.error(msg)