#coding=utf8

import os
import sh
import sys
import click
import json
import logging
from ..utils import svnutil
from ..utils import gitutil
from ..utils import common_utils

@click.command()
@click.option('-c/-nc', '--cpp', default = False, help=u'C 代码库')
@click.option('-l/-nl', '--lua', default = False, help=u'lua 代码')
@click.option('-r/-nr', '--res', default = False, help=u'美术资源')
@click.option('-f/-nf', '--config', default = False, help=u'配置文件')
def run(**options):
    show_all = not (options['cpp'] or options['lua'] or options['res'] or options['config'])
    '''导出配置资源, 需要配置路径'''
    if options['cpp'] or show_all:
        update_c()
    if options['lua'] or show_all:
        update_lua()
    if options['res'] or show_all:
        update_svn()
    if options['config'] or show_all:
        update_config()

def update_config():
    project_setting = common_utils.getMainConfig('master_config')
    has_update = svnutil.update(project_setting['project_cfg'])
    if has_update:
        sh.cd('/data/work/src/dzm2/mtool')
        mtool = sh.Command('env/bin/mtl')
        mtool('cfg', _out=sys.stdout, _err=sys.stdout)

def update_c():
    project_setting = common_utils.getMainConfig('master_config')
    gitutil.git_update(project_setting['project_c'])


def update_lua():
    project_setting = common_utils.getMainConfig('master_config')
    gitutil.git_update(project_setting['project_lua'])



def update_svn():
    project_setting = common_utils.getMainConfig('master_config')
    has_update = svnutil.update(project_setting['project_res'])
    if has_update:
        sh.cd('/data/work/src/dzm2/mtool')
        mtool = sh.Command('env/bin/mtl')
        origin_source = common_utils.getSetting('ln_source')
        if origin_source == 'asset_pvr':
            mtool('res', '-P', _out=sys.stdout, _err=sys.stdout)
        else:
            mtool('res', _out=sys.stdout, _err=sys.stdout)

        mtool('ccs', '-n', '-c', '-m', '-p', _out=sys.stdout, _err=sys.stdout)

if __name__ == '__main__':
    run()
