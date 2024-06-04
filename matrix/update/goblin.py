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

logger = common_utils.getLogger()

@click.command()
@click.option('-c/-nc', '--cocos', default=False, help=u'cocos-engine-topjoy')
@click.option('-C/-nC', '--creator', default=False, help=u'goblin-creator')
@click.option('-l/-nl', '--lua', default=False, help=u'lua 代码')
@click.option('-r/-nr', '--res', default=False, help=u'美术资源')
@click.option('-f/-nf', '--config', default=False, help=u'配置文件')
def update_goblin_res(**options):
    '''goblin 代码、资源、配置更新'''
    show_all = not (options['cocos'] or options['creator'] or options['lua'] or options['res'] or options['config'])
    project_setting = common_utils.getMainConfig('goblin_config')
    mtl_cmd = project_setting['mtool_path']


    if options['cocos'] or show_all:
        gitutil.git_update(project_setting['project_cocos'])

    if options['creator'] or show_all:
        gitutil.git_update(project_setting['project_creator'])

    if options['lua'] or show_all:
        has_update = gitutil.git_update(project_setting['project_lua'])
        print('Lua Updated = %s'%has_update)
        # if has_update:
        #     mtool = sh.Command(mtl_cmd)
        #     mtool('luaalt', _out=sys.stdout, _err=sys.stdout)

    if options['res'] or show_all:
        res_path = os.path.realpath(project_setting['project_res'])
        has_update = svnutil.update(res_path)
        if has_update:
            mtool = sh.Command(mtl_cmd)
            # mtool('ui', '-np', _out=sys.stdout, _err=sys.stdout)
            mtool('res', _out=sys.stdout, _err=sys.stdout)
            mtool('fgui', _out=sys.stdout, _err=sys.stdout)

    if options['config'] or show_all:
        cfg_path = os.path.realpath(project_setting['project_cfg'])
        has_update = svnutil.update(cfg_path)
        print('Lua Updated = %s'%has_update)
        if has_update:
            mtool = sh.Command(mtl_cmd)
            mtool('cfg', _out=sys.stdout, _err=sys.stdout)



@click.command()
@click.option('-g/-ng', '--goblin', default = True, help=u'切换goblin/menu项目')

def switch_resources(**options):
    '''goblin 更改Resources引用'''

    project_setting = common_utils.getMainConfig('vega_config')

    src_path = project_setting['res_path']
    dst_path = os.path.join(project_setting['project_c'], 'Resources')

    if options['patch'] != '':
        src_path = src_path + '_' + options['patch']

    if os.path.exists(dst_path):
        sh.rm(dst_path)
    ln = sh.Command('ln')
    logger.debug('ln -s %s %s'%(src_path, dst_path))
    ln('-s',src_path, dst_path, _out=sys.stdout, _err=sys.stdout)

    logger.info('switch to ' + os.path.split(src_path)[-1])
