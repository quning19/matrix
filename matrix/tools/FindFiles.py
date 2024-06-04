#coding=utf-8

import os
import click
import shutil
import subprocess
from matrix import utils
from matrix.utils import common_utils

@click.command()
@click.option('-i', '--input', required = True, help=u'原始路径')
@click.option('-o', '--output', required = True, help=u'导出路径')
@click.option('--ext', required = True, help=u'扩展名')
def findFiles(**options):
    all_file_list = []
    input_path = options['input']
    output_path = options['output']
    print(options)
    url_list = utils.get_all_file_list(input_path, all_file_list, options['ext'])
    for i in range(len(url_list)):
        url = url_list[i]
        file_name = os.path.split(url)[-1]
        print(file_name)
        rel_path = os.path.relpath(url, input_path).split('/')[0]
        print(rel_path)
        target_path = os.path.join(output_path, rel_path)
        if not os.path.exists(target_path):
            os.mkdir(target_path)
        shutil.copy(url, target_path)
    print('total ' + str(len(url_list)) + ' files found.')