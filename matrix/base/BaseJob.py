#coding=utf-8

import logging
from matrix import utils

class BaseJob:

    def __init__(self, options):
        self._options = options
        utils.setLoggerLevel(self.logger_level)

    @property
    def options(self):
        return self._options

    @property
    def logger(self):
        from matrix.base.ProgressLogger import ProgressLogger
        return ProgressLogger()
        # return utils.getLogger(self.__class__.__name__)

    @property
    def project_name(self):
        return self.get_config('project_name')

    @property
    def logger_level(self):
        return self.get_options('debug') and logging.DEBUG or logging.INFO

    def get_config(self, key):
        return self.get_options(key) or utils.getProjectConfig(key) or utils.getMainConfig(key)

    def get_options(self, key):
        if key in self._options:
            return self._options[key]
        return None
