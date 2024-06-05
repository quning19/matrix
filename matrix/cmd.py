#coding=utf-8

import click

from matrix.utils import common_utils
from matrix.utils import svnutil
from matrix.utils import gitutil

CONTEXT_SETTINGS = dict(auto_envvar_prefix='RESLIB',help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
# @click.group()
def main(**options):
    """We All In Matrix"""
    pass

# from .update import update_all_res
# main.add_command(update_all_res.run,name='update')
#
# from .update import res
# main.add_command(res.switch_upgrade_path,name='sw')

# from matrix.update import vega
# main.add_command(vega.update_vega_res,name='up')
# main.add_command(vega.update_gouki_res, name='gouki')
# main.add_command(vega.switch_upgrade_path,name='sw')
# main.add_command(vega.switch_resources,name='sr')
# main.add_command(vega.rebuild_platform_asset,name='rb')

# from matrix.update import pandora
# main.add_command(pandora.update_pandora_res, name='pdr')

# from matrix.update import goblin
# main.add_command(goblin.update_goblin_res, name='goblin')


# from matrix.vega_pvp import server_log_analyse
# main.add_command(server_log_analyse.run,name='server_log')

from matrix.utils import VideoTool
main.add_command(VideoTool.cutVideo,name='video')
main.add_command(VideoTool.ExportVideo, name='ev')

from matrix.tools import DownloadFiles
main.add_command(DownloadFiles.download,name='download')

from matrix.tools import RenameAssetsForApk
main.add_command(RenameAssetsForApk.zip_all_files, name='zipall')

from matrix.tools import FindFiles
main.add_command(FindFiles.findFiles, name='findFiles')



@click.command()
def run_calc_probability(**options):
    """Calc Probability """
    from matrix.games.CalcProbability import CalcProbability
    job = CalcProbability(options)
    # from matrix.tests.test_click_times import ClickSimulator
    # job = ClickSimulator(options)
    job.run()


main.add_command(run_calc_probability, name='cp')



if __name__ == '__main__':
    main()
