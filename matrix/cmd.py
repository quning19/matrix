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
    job.run()

main.add_command(run_calc_probability, name='cp')


@click.option('-i', '--input-path', required=True, help='csv文件读取路径')
@click.command()
def run_dsp(**options):
    """DSP SEED CALC"""
    from matrix.games.DSPSeedFind import DSPSeedFind
    job = DSPSeedFind(options)
    job.run()

@click.option('-p', '--work-path', required=True, help='json文件读取路径')
@click.command()
def run_d2r_language_modify(**options):
    """Language Modify"""
    from matrix.games.d2rReimagined.LanguageModify import LanguageModify
    job = LanguageModify(options)
    job.run()

@click.option('-w', '--work-path', required=True, help='工作路径')
@click.command()
def run_d2r_item_finder(**options):
    """item finder"""
    from matrix.games.d2rReimagined.ItemFinder import ItemFinder
    job = ItemFinder(options)
    job.run()

@click.option('-o', '--original-path', required=True, help='原始excel输出路径')
@click.option('-w', '--work-path', required=True, help='工作路径')
@click.command()
def run_d2r_item_details(**options):
    """item finder"""
    from matrix.games.d2rReimagined.ItemDetailsGenerator import ItemDetailsGenerator
    job = ItemDetailsGenerator(options)
    job.run()

main.add_command(run_dsp, name='dsp')
main.add_command(run_d2r_language_modify, name='d2rl')
main.add_command(run_d2r_item_finder, name='d2rf')
main.add_command(run_d2r_item_details, name='d2rd')


if __name__ == '__main__':
    main()
