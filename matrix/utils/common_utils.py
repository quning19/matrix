#coding=utf-8

import yaml
import os
import logging
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def getLogger(name = None):
    name = None or 'log'
    logger = logging.getLogger(name)
    if len(logger.handlers) > 0:
        return logger

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)
    return logger

main_config = None

logger = getLogger()

def dumpOptions(obj, logger):
    logger.info('Input Options:')
    for k in obj:
        v = obj[k]
        logger.info(k + " = " + str(v))

def is_true(v):
    return v=='1' or v=='yes' or v=='true' or v == True

def getMainConfig(key = None):
    global main_config
    if main_config == None:
        self_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(self_dir,'..', 'config.yaml')
        if not os.path.exists(config_path):
            logger.error("config.yaml 文件不存在，需要将 config.example.yaml 复制为 config.yaml 并进行配置")
            exit()
        stream = open(config_path, 'r')
        main_config = yaml.load(stream, Loader=yaml.FullLoader)
    if key != None:
        if main_config.has_key(key):
            return main_config[key]
        else:
            return None
    return main_config

project_config = None
personal_config = None

def getProjectConfig(key):
    global project_config
    global personal_config

    if personal_config == None:
        self_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(self_dir, 'config.personal.yaml')
        if os.path.exists(config_path):
            stream = open(config_path, 'r')
            personal_config = yaml.load(stream)
        if personal_config == None:
            personal_config = {}
    if project_config == None:
        config = getMainConfig()
        project_name = config['project_name']
        self_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(self_dir, 'config.' + project_name + '.yaml')
        if not os.path.exists(config_path):
            logger.error("config.yaml 文件不存在，需要将 config.example.yaml 复制为 config.yaml 并进行配置")
            exit()
        stream = open(config_path, 'r')
        project_config = yaml.load(stream)
        if project_config == None:
            project_config = {}
    if key != None:
        if personal_config.has_key(key):
            return personal_config[key]
        elif project_config.has_key(key):
            return project_config[key]
        else:
            return None
    return project_config

def remove_dir(dir_path):
    if not os.path.exists(dir_path):
        return
    dir_path = dir_path + os.sep
    list = os.listdir(dir_path)
    for li in list:
        filepath = os.path.join(dir_path,li)
        if os.path.isdir(filepath):
            remove_dir(filepath)
        elif os.path.isfile(filepath):
            os.remove(filepath)

        if os.path.exists(filepath):
            os.rmdir(filepath)

def getSetting(key):
    self_dir = os.path.dirname(os.path.abspath(__file__))
    setting_path = os.path.join(self_dir, 'setting.yaml')
    if not os.path.exists(setting_path):
        return None
    stream = open(setting_path, 'r')
    setting = yaml.load(stream)
    stream.close()
    if setting.has_key(key):
        return setting[key]
    return None

def setSetting(key, value):
    self_dir = os.path.dirname(os.path.abspath(__file__))
    setting_path = os.path.join(self_dir, 'setting.yaml')
    stream = open(setting_path, 'w+')
    setting = yaml.load(stream) or {}
    setting[key] = value
    yaml.dump(setting, stream)
    stream.close()


if __name__ == '__main__':
    getProjectConfig('')
