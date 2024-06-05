#coding=utf-8

from matrix.base.BaseJob import BaseJob

class CalcProbability(BaseJob):
    def __init__(self, options):
        BaseJob.__init__(self, options)
        pass

    def run(self):
        self.logger.info('calc probability')