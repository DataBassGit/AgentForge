import logging
import os


class Logger:
    _logger = None
    name = None

    def __init__(self, name='AgentForge', log_file='./Logs/AgentForge.log'):
        self._logger = logging.getLogger(name)

        if not self._logger.handlers:
            self._logger.setLevel(logging.DEBUG)  # or whatever level you want

            # create file handler which logs messages
            fh = logging.FileHandler(os.path.join(log_file))
            fh.setLevel(logging.DEBUG)  # or whatever level you want

            # create console handler with a higher log level
            ch = logging.StreamHandler()
            ch.setLevel(logging.ERROR)  # or whatever level you want

            # create formatter and add it to the handlers
            formatter = logging.Formatter('%(name)s - %(message)s')
            ch.setFormatter(formatter)
            fh.setFormatter(formatter)

            # add the handlers to logger
            self._logger.addHandler(ch)
            self._logger.addHandler(fh)

    def log(self, msg, level='default'):
        msg = str(msg) + '\n'  # Add a new line at the end of each message

        if level == 'default':
            level = self.get_current_level().lower()

        if level == 'debug':
            self._logger.debug(msg)
        elif level == 'info':
            self._logger.info(msg)
        elif level == 'warning':
            self._logger.warning(msg)
        elif level == 'error':
            self._logger.error(msg)
        elif level == 'critical':
            self._logger.critical(msg)
        else:
            raise ValueError('Invalid log level: {}'.format(level))

    def set_level(self, level):
        level_dict = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL,
        }

        if level not in level_dict:
            raise ValueError('Invalid log level: {}'.format(level))

        level_code = level_dict[level]

        self._logger.setLevel(level_code)
        for handler in self._logger.handlers:
            handler.setLevel(level_code)

    def get_current_level(self):
        level = logging.getLevelName(self._logger.getEffectiveLevel())
        return level

# EXAMPLES:
# logger = Logger(name="ethos_tester.py")
# logger.set_level('debug')

# current_level = logger.get_current_level()

# logger.log('debug message') -> default, meaning it will always print
# logger.log('debug', 'debug message')
# logger.log('info', 'info message')
# logger.log('warning', 'warning message')
# logger.log('error', 'error message')
# logger.log('critical', 'critical message')
