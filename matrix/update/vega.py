#coding=utf-8

import click
import sh
import sys
import os
import shutil
from matrix.utils import common_utils
from matrix.utils import svnutil
from matrix.utils import gitutil

mtl_cmd = 'mtl'

logger = common_utils.getLogger()

@click.command()
@click.option('-c/-nc', '--cpp', default = False, help=u'C 代码库')
@click.option('-l/-nl', '--lua', default = False, help=u'lua 代码')
@click.option('-r/-nr', '--res', default = False, help=u'美术资源')
@click.option('-f/-nf', '--config', default = False, help=u'配置文件')
@click.option('-r/-nr', '--release', default = False, help=u'release目录')
def update_vega_res(**options):
    '''vega 代码、资源、配置更新'''
    show_all = not (options['cpp'] or options['lua'] or options['res'] or options['config'])
    project_setting = common_utils.getMainConfig('vega_config')
    if options['cpp'] or show_all:
        gitutil.git_update(project_setting['project_c'])
    if options['lua'] or show_all:
        gitutil.git_update(project_setting['project_lua'])
        sh.cd(project_setting['mtool_path'] or '/data/work/src/dzm2/mtool')
        mtool = sh.Command(mtl_cmd)
        mtool('luaalt', _out=sys.stdout, _err=sys.stdout)

    release_fix = ''
    if options['release'] :
        release_fix = '_release'
        
    if options['res'] or show_all:
        res_path = os.path.realpath(project_setting['project_res'] + release_fix)
        has_update = svnutil.update(res_path)
        if has_update:
            sh.cd(project_setting['mtool_path'] or '/data/work/src/dzm2/mtool')
            mtool = sh.Command(mtl_cmd)
            mtool('ui', '-np', _out=sys.stdout, _err=sys.stdout)
            mtool('res', _out=sys.stdout, _err=sys.stdout)

    if options['config'] or show_all:
        cfg_path = os.path.realpath(project_setting['project_cfg'] + release_fix)
        has_update = svnutil.update(cfg_path)
        if has_update:
            sh.cd(project_setting['mtool_path'] or '/data/work/src/dzm2/mtool')
            mtool = sh.Command(mtl_cmd)
            mtool('cfg', _out=sys.stdout, _err=sys.stdout)

@click.command()
@click.option('-n/-nc', '--normal', default = False, help=u'png资源')
@click.option('-i/-ni', '--ios', default = False, help=u'pvr tp 资源')
@click.option('-a/-na', '--android', default = False, help=u'png tp 资源')
@click.option('-s/-ns', '--silence', default = True, help=u'是否导出资源')

def switch_upgrade_path(**options):

    switched = False

    if options['ios']:
        switched = create_ln('assets_platform/asset_ios')
    elif options['android']:
        switched = create_ln('assets_platform/asset_android')
    else:
        switched = create_ln('assets_platform/asset')

    if not switched or options['silence'] :
        return
        # export assets

@click.command()
@click.option('-p', '--patch', default = '', help='配置文件读取路径')

def switch_resources(**options):
    '''vega 更改Resources引用'''

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


@click.command()
def rebuild_platform_asset(**options):
    origin_source = common_utils.getSetting('ln_source')
    if origin_source == None or 'android' in origin_source:
        logger.error('skip')
        return

    project_setting = common_utils.getMainConfig('vega_config')
    sh.cd(project_setting['mtool_path'] or '/data/work/src/dzm2/mtool')
    mtool = sh.Command(mtl_cmd)

    project_setting = common_utils.getMainConfig('vega_config')

    work_path = os.path.join(project_setting['root_path'], origin_source)

    for root, dirs, files in os.walk(work_path, topdown=False):
        for name in dirs:
            shutil.rmtree(os.path.join(root, name))

    # mtool('ui', _out=sys.stdout, _err=sys.stdout)

    if 'ios' in origin_source:
        mtool('res_online', '-i','/data/work/src/VegaGame/svn/frontend/Assets', '-o', '/data/work/src/VegaGame/Resources', _out=sys.stdout, _err=sys.stdout)
        mtool('task', '-g', 'vega', '-p', '/data/work/src/VegaGame/svn/frontend/Assets', '-i', '/data/work/src/VegaGame/svn/frontend/Assets/', '-t', 'iOS', '-o', '/data/work/src/VegaGame/Resources', '-cd', '/data/work/src/VegaGame/cachedir', '-an', 'X2Mc_walle,PackupAnim_walle', _out=logger.debug, _err=logger.error)
    else:
        mtool('res', _out=sys.stdout, _err=sys.stdout)


def create_ln(source):
    origin_source = common_utils.getSetting('ln_source')
    if origin_source == source:
        logger.info('same source, skip switch')
        return False

    project_setting = common_utils.getMainConfig('vega_config')

    src_path = os.path.join(project_setting['root_path'], source)
    dst_path = os.path.join(project_setting['res_path'], 'asset')
    logger.debug(src_path)
    logger.debug(dst_path)
    if os.path.exists(dst_path):
        sh.rm(dst_path)
    ln = sh.Command('ln')
    ln('-s',src_path, dst_path, _out=sys.stdout, _err=sys.stdout)
    common_utils.setSetting('ln_source', source)
    logger.info('switch to ' + source)
    return True
