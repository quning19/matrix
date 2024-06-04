#coding=utf-8

import click
import sys
import os
if os.name != 'nt':
    import sh
import shutil
from matrix.utils import common_utils
from matrix.utils import svnutil
from matrix.utils import gitutil

mtl_cmd = 'mtl'

logger = common_utils.getLogger()



@click.command()
@click.option('-c/-nc', '--cpp', default=False, help=u'C 代码库')
@click.option('-l/-nl', '--lua', default=False, help=u'lua 代码')
@click.option('-r/-nr', '--res', default=False, help=u'美术资源')
@click.option('-f/-nf', '--config', default=False, help=u'配置文件')
def update_pandora_res(**options):
    '''pandora 代码、资源、配置更新'''
    show_all = not (options['cpp'] or options['lua'] or options['res'] or options['config'])
    project_setting = common_utils.getMainConfig('pandora_config')
    mtl_cmd = project_setting['mtool_path']


    if options['cpp'] or show_all:
        gitutil.git_update(project_setting['project_c'])

    if options['lua'] or show_all:
        has_update = gitutil.git_update(project_setting['project_lua'])
        print('Lua Updated = %s'%has_update)
        if has_update:
            mtool = sh.Command(mtl_cmd)
            mtool('luaalt', _out=sys.stdout, _err=sys.stdout)
            gitutil.git_update(project_setting['project_lua'])
            mtool = sh.Command(mtl_cmd)
            mtool('pb', _out=sys.stdout, _err=sys.stdout)

    if options['res'] or show_all:
        res_path = os.path.realpath(project_setting['project_res'])
        has_update = svnutil.update(res_path)
        if has_update:
            mtool = sh.Command(mtl_cmd)
            mtool('res', _out=sys.stdout, _err=sys.stdout)
            mtool('skill', _out=sys.stdout, _err=sys.stdout)
            mtool('map', _out=sys.stdout, _err=sys.stdout)
            mtool('fgui', _out=sys.stdout, _err=sys.stdout)

    if options['config'] or show_all:
        has_update = gitutil.git_update(project_setting['project_cfg'])
        print('Lua Updated = %s'%has_update)
        if has_update:
            mtool = sh.Command(mtl_cmd)
            mtool('cfg', _out=sys.stdout, _err=sys.stdout)
