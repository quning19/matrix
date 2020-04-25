#coding=utf-8

import os
import sh
import sys
import click
from matrix.utils import common_utils

ffmpegPath = '/data/work/src/tools/ffmpeg'

@click.command()
@click.option('-i', '--input', required = True, help=u'video文件路径')
@click.option('-t', '--time', default = '', help=u'截取时间')
@click.option('-s', '--slow', default = '1', help=u'慢动作')
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

