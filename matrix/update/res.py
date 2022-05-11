#coding=utf8

import os
import sh
import sys
import click
import json
import logging
from ..utils import common_utils


@click.command()
@click.option('-n/-nc', '--normal', default = False, help=u'png资源')
@click.option('-p/-np', '--pvr', default = False, help=u'pvr tp 资源')
@click.option('-t/-nt', '--tp', default = False, help=u'png tp 资源')
@click.option('-e/-ne', '--etc', default = False, help=u'etc tp 资源')
@click.option('-s/-ns', '--silence', default = True, help=u'是否导出资源')
def switch_upgrade_path(**options):

    switched = False

    if options['pvr']:
        switched = create_ln('res_assets/asset_pvr')
    elif options['tp']:
        switched = create_ln('res_assets/asset_png')
    elif options['etc']:
        switched = create_ln('res_assets/asset_etc')
    else:
        switched = create_ln('res_assets/asset_notp')

    if switched and not options['silence'] :
        # export assets
        # pylint: disable=no-member
        sh.cd('/data/work/src/dzm2/mtool') 
        mtool = sh.Command('env/bin/mtl')
        if options['pvr']:
            mtool('res', '-P', _out=sys.stdout, _err=sys.stdout)
        else:
            mtool('res', _out=sys.stdout, _err=sys.stdout)
        mtool('ccs', '-n', '-c', '-m', '-p', _out=sys.stdout, _err=sys.stdout)


def create_ln(source):
    origin_source = common_utils.getSetting('ln_source')

    project_setting = common_utils.getMainConfig('master_config')
    src_path = os.path.join(project_setting['root_path'], source)
    dst_path = os.path.join(project_setting['res_path'], 'asset')
    print(src_path)
    print(dst_path)
    if os.path.exists(dst_path):
        # pylint: disable=no-member
        sh.rm(dst_path)
    ln = sh.Command('ln')
    ln('-s',src_path, dst_path, _out=sys.stdout, _err=sys.stdout)
    common_utils.setSetting('ln_source', source)
    if origin_source == None:
        return True
    return origin_source != source

if __name__ == '__main__':
    # run()
    pass
