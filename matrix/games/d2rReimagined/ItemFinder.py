#coding=utf-8

import os

import yaml
from matrix.base.BaseJob import BaseJob


class ItemFinder(BaseJob):

    excel_relative_path = 'data/global/excel/'

    item_files = [
        'uniqueitems.txt',
        'setitems.txt',
        'runes.txt',
    ]

    def __init__(self, options):
        BaseJob.__init__(self, options)

        yaml_path = os.path.join(os.path.dirname(__file__), 'D2rrConfig.yaml')

        if os.path.isfile(yaml_path):
            self.d2r_config = yaml.load(open(yaml_path))
        print(self.d2r_config)


    def run(self):
        self.logger.info('start')
        work_path = self.get_options('work_path')
