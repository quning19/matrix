#coding=utf-8

import click
import sh
import sys
from matrix.utils import common_utils
from matrix.utils import svnutil
from matrix.utils import gitutil

CONTEXT_SETTINGS = dict(auto_envvar_prefix='RESLIB',help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
# @click.group()
def main(**options):
    """We All In Matrix"""
    pass

from .update import update_all_res
main.add_command(update_all_res.run,name='update')

from .update import res
main.add_command(res.switch_upgrade_path,name='sw')

@click.command()
def update_vega_res():
    project_setting = common_utils.getMainConfig('vega_config')
    gitutil.git_update(project_setting['project_c'])
    gitutil.git_update(project_setting['project_lua'])
    sh.cd(project_setting['mtool_path'] or '/data/work/src/dzm2/mtool')
    mtool = sh.Command('env/bin/mtl')
    mtool('luaalt', _out=sys.stdout, _err=sys.stdout)
    has_update = svnutil.update(project_setting['project_res'])
    if has_update:
        # mtool('task_dev', '-g', 'vega', _out=sys.stdout, _err=sys.stdout)
        mtool('ui', _out=sys.stdout, _err=sys.stdout)
        mtool('res', _out=sys.stdout, _err=sys.stdout)

    has_update = svnutil.update(project_setting['project_cfg'])
    if has_update:
        mtool('cfg', _out=sys.stdout, _err=sys.stdout)



main.add_command(update_vega_res,name='v')


from matrix.vega_pvp import server_log_analyse
main.add_command(server_log_analyse.run,name='server_log')
if __name__ == '__main__':
    main()
