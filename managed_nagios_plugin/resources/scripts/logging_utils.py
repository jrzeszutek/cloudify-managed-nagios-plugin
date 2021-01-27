import json
import logging
import logging.config


LOGGING_CONFIG_LOCATION = '/etc/nagios/cloudify_components_logging.cfg'


class Logger(object):
    def __init__(self, name, config_location=LOGGING_CONFIG_LOCATION):
        self._logger = logging.getLogger(name)

        if config_location:
            with open(config_location) as config_handle:
                logging.config.dictConfig(json.load(config_handle))

    def debug(self, message):
        self._logger.debug(message)

    def info(self, message):
        self._logger.info(message)

    def warn(self, message):
        self._logger.warn(message)

    def error(self, message):
        self._logger.error(message)

    def exception(self, message):
        self._logger.exception(message)
