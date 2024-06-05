import os

walle_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..'))


def humansize(nbytes):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    if nbytes == 0: return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes) - 1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])


def make_parent_folder(path):
    dest_dir = os.path.dirname(path)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)


def md5_for_file(filename):
    md5 = sh.Command('/sbin/md5')
    r = md5('-q', filename)
    md5sum = r.stdout.strip()
    if type(md5sum) == bytes:
        md5sum = md5sum.decode("utf-8")
    return md5sum


def get_all_file_list(find_dir, all_file_name, ext=None):
    file_list = os.listdir(find_dir)
    for file_name in file_list:
        file_path = os.path.join(find_dir, file_name)
        if os.path.isdir(file_path):
            get_all_file_list(file_path, all_file_name, ext)
        elif os.path.isfile(file_path):
            if ext == None or ext in os.path.splitext(file_path)[1]:
                all_file_name.append(file_path)

    return all_file_name

import logging
from matrix.utils.MLogger import MLogger
logger_list = []

def getLogger(name):

    logger = MLogger(name)
    logger_list.append(logger)
    return logger


def setLoggerLevel(logger_level):
    for i in range(len(logger_list)):
        logger = logger_list[i]
        logger.setLevel(logger_level or logging.INFO)