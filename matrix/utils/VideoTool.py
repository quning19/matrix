#coding=utf-8

import os
import sh
import sys
import click
from matrix.utils import *
from matrix.utils import common_utils

ffmpegPath = 'ffmpeg'

@click.command()
@click.option('-i', '--input', required = True, help=u'video文件路径')
@click.option('-t', '--time', default = '', help=u'截取时间')
@click.option('-s', '--slow', default = '1', help=u'慢动作')
@click.option('-q', '--quality', help=u'慢动作')
def cutVideo(**options):
    inputPath = options['input']
    pathes = os.path.splitext(inputPath)
    outputPath = pathes[0] + '_new' + pathes[1]
    optionStr = ""
    ffmpeg = sh.Command(ffmpegPath)
    logger = common_utils.getLogger()
    args = []
    if ':' in options['time']:
        times = options['time'].split(':')
        startT = int(times[0])
        endT = int(times[1])
        args = args + ['-ss', startT, '-t', endT - startT]
        logger.info(u'截取第[%d]秒到第[%d]秒.'%(startT, endT))

    args = args + ['-y', '-i', inputPath]
    if options['slow'] != None:
        args = args + ['-c:v', 'libx264', '-crf', options['slow']]
        # /data/work/src/tools/ffmpeg -ss 10 -t 3 -i /data/work/src/VegaGame/workspace/temp/oppo截图/Record_2019-12-30-14-20-52_67e27fddcffeff615c8f2a3c728537d0.mp4  -vf "setpts=(PTS-STARTPTS)/0.2" /data/work/src/VegaGame/workspace/temp/oppo截图/tes111t.mp4
    if options['slow'] != '1':
        slowRate = float(options['slow'])
        args = args + ['-vf', 'setpts=(PTS-STARTPTS)/%f'%(1/slowRate)]
        logger.info(u'视频速度放慢[%.2f]倍'%slowRate)

    args.append(outputPath)
    logger.info(args)
    logger.info('开始处理')
    ffmpeg(*args)
    logger.info('输出文件: ' + outputPath)


@click.command()
@click.option('-i', '--input-path', required=True, help=u'video文件路径')
@click.option('-q', '--quality', default='16', help=u'视频品质，越低越好，默认16高清。抽卡，loading建议18，战斗建议21')
@click.option('-h', '--height', default='720', help=u'视频高度，默认720')
@click.option('-o', '--output-path', help=u'导出路径')
def ExportVideo(**options):
    inputPath = options['input_path']
    outputPath = options['output_path']
    if outputPath == None:
        outputPath = os.path.abspath(inputPath) + '_export'

    all_file_list = []

    get_all_file_list(inputPath, all_file_list)

    for i in range(len(all_file_list)):
        filePath = all_file_list[i]
        relpath = os.path.relpath(filePath, inputPath)
        outputFilePath = os.path.join(outputPath, relpath)
        outputFilePath = os.path.splitext(outputFilePath)[0] + '.mp4'

        outputDir = os.path.dirname(outputFilePath)
        if not os.path.isdir(outputDir):
            os.mkdir(outputDir)

        ffmpeg = sh.Command(ffmpegPath)
        logger = common_utils.getLogger()
         
        # args = ['-y', '-i', filePath, '-s', '1280x720', '-c:v', 'libx264', '-r', '30', '-tune', 'fastdecode', '-crf', '16', outputFilePath]
        args = ['-y', '-i', filePath, '-vf', 'scale=-1:'+options['height'], '-c:v', 'libx264', '-r', '30', '-tune', 'fastdecode', '-crf', options['quality'], outputFilePath]
        logger.info(args)
        logger.info(' '.join(args))
        logger.info('开始处理: ' + relpath)
        ffmpeg(*args)
    logger.info('输出文件: ' + outputPath)
