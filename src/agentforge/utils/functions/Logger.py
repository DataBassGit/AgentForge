import os
import logging
from pathlib import Path
from agentforge.utils.functions.UserInterface import UserInterface

from termcolor import cprint
from colorama import init
init(autoreset=True)


class BaseLogger:
    def __init__(self, name='BaseLogger', log_file='default.log'):
        self.logger = logging.getLogger(name)
        self.log_file = log_file
        self._setup_logger()

    def _setup_logger(self):
        if not self.logger.handlers:
            self.logger.setLevel(logging.DEBUG)  # Default level, can be customized

            # Define the relative path for the log directory
            log_folder = "Logs"
            # Create the Logs folder if it doesn't exist
            if not os.path.exists(log_folder):
                os.makedirs(log_folder)

            # File handler for logs
            log_file_path = f'{log_folder}/{self.log_file}'
            fh = logging.FileHandler(log_file_path)
            fh.setLevel(logging.DEBUG)  # File handler level

            # Console handler for logs
            ch = logging.StreamHandler()
            ch.setLevel(logging.ERROR)  # Console handler level

            # Formatter for handlers
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)

            # Add handlers to logger
            self.logger.addHandler(fh)
            self.logger.addHandler(ch)

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
    def __init__(self, name, general_log_name='AgentForge', model_log_name='ModelIO'):
        # Initialize loggers and store them in a list
        self.loggers = {
            'general': BaseLogger(name=general_log_name, log_file=f'{general_log_name}.log'),
            'model': BaseLogger(name=model_log_name, log_file=f'{model_log_name}.log'),
        }

    def log(self, msg, level='info', logger_type='general'):
        # Allow logging to a specific logger or all loggers
        if logger_type == 'all':
            for logger in self.loggers.values():
                logger.log_msg(msg, level)
        else:
            self.loggers[logger_type].log_msg(msg, level)

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

    # class Logger:
#     def __init__(self, general_log_name='AgentForge', model_log_name='ModelIO'):
#         self.general_logger = BaseLogger(name=general_log_name, log_file=f'{general_log_name}.log')
#         self.model_logger = BaseLogger(name=model_log_name, log_file=f'{model_log_name}.log')
#
#     def log(self, msg, level='info'):
#         level_code = self.get_level_code(level)
#         self.general_logger.log(msg, level_code)
#
#     def log_prompt(self, prompt):
#         self.model_logger.log(f'Prompt:\n{prompt}', logging.DEBUG)
#
#     def log_response(self, response):
#         self.model_logger.log(f'Model Response:\n{response}', logging.DEBUG)
#
#     # Other methods like `parsing_error` can be adapted similarly,
#     # depending on whether they belong to general or model logging.
#
#     def get_level_code(self, level):
#         level_dict = {
#             'debug': logging.DEBUG,
#             'info': logging.INFO,
#             'warning': logging.WARNING,
#             'error': logging.ERROR,
#             'critical': logging.CRITICAL,
#         }
#
#         if level.lower() not in level_dict:
#             self.log("Invalid log level: '{}'. Setting log level to 'info'.".format(level), 'warning')
#             level = 'info'
#
#         return level_dict.get(level.lower(), logging.INFO)
#
#     def set_level(self, level):
#         level_code = self.get_level_code(level)
#         self._logger.setLevel(level_code)
#
#         for handler in self._logger.handlers:
#             handler.setLevel(level_code)

    # def log(self, msg, level='info'):
    #     msg = str(msg) + '\n'  # Add a new line at the end of each message
    #
    #     if level == 'debug':
    #         self._logger.debug(msg)
    #     elif level == 'info':
    #         self._logger.info(msg)
    #     elif level == 'warning':
    #         self._logger.warning(msg)
    #     elif level == 'error':
    #         self._logger.error(msg)
    #         self.UI.user_input_on_error()
    #     elif level == 'critical':
    #         self._logger.critical(msg)
    #         raise
    #     else:
    #         raise ValueError('Invalid log level: {}'.format(level))

    # def log_prompt(self, prompt):
    #     self.log(f'Prompt:\n{prompt}', 'debug')
    #
    # def log_response(self, response):
    #     self.log(f'Model Response:\n{response}', "debug")

    def parsing_error(self, model_response, error):
        self.log(f"Parsing Error - It is very likely the model did not respond in the required "
                 f"format\n\nModel Response:\n{model_response}\n\nError: {error}", 'error')

