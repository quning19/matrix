#coding=utf-8

import os
import sys
import click
import subprocess
from matrix.utils import common_utils

aria2_path = '/data/work/src/tools/aria2-1.35.0/bin/aria2c'

@click.command()
@click.option('-i', '--input', required = True, help=u'csv文件路径')
@click.option('-o', '--output', required = True, help=u'下载路径')
def download(**options):
    url_list = _read_input_file(options['input'])
    for i in range(len(url_list)):
        info = url_list[i]
        print('index = %d'%i)
        print(info)
        _download_file(info['url'], options['output'], info['file_name'] + '.mp3')
    _rename_downloaded(options['output'])

def _read_input_file(input_csv):
    if not os.path.exists(input_csv):
        return
    url_list = []
    csvFile = open(input_csv)
    while True:
        line = csvFile.readline()
        if len(line) == 0:
            break
        lines = line.split(",")
        url = lines[1]
        file_name = lines[2]
        if 'http' in url:
            url_list.append({'url':url.strip(), 'file_name':file_name.strip()})

    return url_list


def _rename_downloaded(dir_path):
    mp3_file_list = []
    collect_files(dir_path, mp3_file_list, 'mp3')
    for i in range(len(mp3_file_list)):
        file_name = mp3_file_list[i]
        if '.1.mp3' in file_name:
            file_name2 = file_name.replace('.1.mp3', '.mp3')
            size1 = os.path.getsize(file_name)
            size2 = os.path.getsize(file_name2)
            if size1 > size2 :
                big_file = file_name
                small_file = file_name2
            else:
                big_file = file_name2
                small_file = file_name
            os.rename(big_file, file_name2.replace('.mp3', '-故事.mp3'))
            os.rename(small_file, file_name2.replace('.mp3', '-律动.mp3'))
            

def _download_file(url, output_path, file_name):
    cmd = '%s -d %s -o "%s" %s'%(aria2_path, output_path, file_name, url)
    subprocess.check_call(cmd, shell=True)

def collect_files(find_dir, all_file_name, ext=None):
    file_list = os.listdir(find_dir)
    for file_name in file_list:
        file_path = os.path.join(find_dir, file_name)
        if os.path.isdir(file_path):
            collect_files(file_path, all_file_name, ext)
        elif os.path.isfile(file_path):
            if ext is None or ext in os.path.splitext(file_path)[1]:
                all_file_name.append(file_path)