#coding=utf-8

import os
import sh
import sys
import click
import zipfile
import datetime
import time

from matrix.utils import *
from matrix.utils import common_utils

modTime = time.time()

@click.command()
@click.option('-i', '--input-path', required=True, help=u'输入路径')
@click.option('-o', '--output-path', default='', help=u'压缩导出路径')
def zip_all_files(**options):
    input_path = options['input_path']
    output_path = options['output_path']

    if os.path.exists(output_path):
        common_utils.remove_dir(output_path)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    all_file_list = []
    get_all_file_list(input_path, all_file_list)

    for file_name in all_file_list:
        rel_path = os.path.relpath(file_name, input_path)
        print(rel_path)
        zip_path = os.path.join(output_path, rel_path)
        dir_path = os.path.dirname(zip_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        os.utime(file_name, (modTime, modTime))

        zfile = zipfile.ZipFile(zip_path+'.zip', "w", zipfile.ZIP_DEFLATED)
        zfile.write(file_name)
        zfile.close()


