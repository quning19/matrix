#coding=utf-8

import logging
import os

import sys, time, random

from matrix import utils
from matrix.utils import common_utils

class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance

class ProgressLogger(Singleton):
    _logger = utils.getLogger('job')
    _width = 50
    _error_list = []
    _warning_list = []
    _log_file = None
    DisableProgress = False

    def setLogName(self, name):
        self._logger = utils.getLogger(name)

    def setTotal(self, cnt):
        self._total = cnt
        self._count = 0

    def __next__(self):
        # return
        self._count += 1

    def debug(self, s):
        self.log(s, 'debug')

    def info(self, s):
        self.log(s, 'info')

    def warning(self, s):
        self.log(s, 'warning')

    def error(self, s):
        self.log(s, 'error')


    def log(self, s, level):

        if level == 'error':
            self._error_list.append(s)
        if level == 'warning':
            self._warning_list.append(s)

        if hasattr(self, '_total') and self._total > 0:
            sys.stdout.write(' ' * (self._width + 9) + '\r')
            sys.stdout.flush()
        getattr(self._logger, level)(s)
        if self._log_file != None and level in ['info', 'warning', 'error'] :
            self._log_file.write(s)
            self._log_file.write('\n')

        if not (hasattr(self, '_total') and self._total > 0) or ProgressLogger.DisableProgress:
            return

        progress = self._width * min(1, self._count / self._total)
        sys.stdout.write('{0:3}/{1:3}: '.format(self._count, self._total))
        sys.stdout.write('#' * int(progress) + '-' * int(self._width - progress) + '\r')
        # if self._count == self._total:
        #     sys.stdout.write('\n')
        sys.stdout.flush()

    def export_error_logs(self):
        for i in range(len(self._warning_list)):
            self._logger.warning(self._warning_list[i])
        for i in range(len(self._error_list)):
            self._logger.error(self._error_list[i])

    def get_error_log_count(self):
        return len(self._error_list)
        
    def get_warning_log_count(self):
        return len(self._warning_list)

    def set_log_file(self, file_path):
        dir_path = os.path.dirname(file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        if self._log_file != None:
            self._log_file.close()
            self._log_file = None
        if file_path != None:
            self._log_file = open(file_path, "w")

