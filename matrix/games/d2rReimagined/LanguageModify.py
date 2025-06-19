#coding=utf-8

from enum import Flag, auto
import json
import os
import re
import shutil
from matrix.base.BaseJob import BaseJob
from matrix.utils import get_all_file_list

class ModifyType(Flag):
    Default = auto()
    Replace = auto()
    NewLine = auto()


class LanguageModify(BaseJob):

    language_setting = {
        'item-names':[
            {
                'filter': r'\[[XE]\]',
                'form': 'enUS',
                'to': 'zhTW',
                'type': ModifyType.Default,
            },
            {
                'filter': r'Stack:',
                'form': 'enUS',
                'to': 'zhTW',
                'type': ModifyType.Replace,
            },
            {
                'filter': r'Orb of',
                'form': 'enUS',
                'to': 'zhTW',
                'type': ModifyType.Replace,
            },
        ],
        'item-runes':[
            {
                'name': 'item-runes.json',
                'form': 'enUS',
                'to': 'zhTW',
                'type': ModifyType.Default,
            },
        ],
    }

    def __init__(self, options):
        BaseJob.__init__(self, options)

    def run(self):
        self.logger.info('start')
        work_path = self.get_options('work_path')
        input_path = os.path.join(work_path, 'original')
        output_path = os.path.join(work_path)
    
        if not os.path.exists(input_path):

            all_files = os.listdir(work_path)

            os.mkdir(input_path)

            for file_name in all_files:
                source_file = os.path.join(work_path, file_name)
                target_file = os.path.join(input_path, file_name)
                shutil.copy(source_file, target_file)

            self.logger.info(f'首次启动，创建original目录: {input_path}')

        for key, settings in self.language_setting.items():
            file_name = key + '.json'

            input_file_path = os.path.join(input_path, file_name)
            output_file_path = os.path.join(output_path, file_name)

            if not os.path.exists(input_file_path):
                self.logger.error(f'File not found: {input_file_path}')
                continue

            self._modify_language_file(input_file_path, output_file_path, settings)

    def _modify_language_file(self, input_file_path, output_file_path, setting):
        self.logger.info(f'Modifying {input_file_path} to {output_file_path}')

        try:
            # 读取JSON文件
            with open(input_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 应用修改函数
            for setting in setting:
                modified_data = self._modify_lang_content(data, setting)
            
            # 保存为新的JSON文件
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(modified_data, f, ensure_ascii=False, indent=4)

            return True
        except json.JSONDecodeError:
            self.logger.error(f"错误: JSON解析失败 - {input_file_path}")
        except Exception as e:
            self.logger.error(f"发生未知错误: {e}")

    def _modify_lang_content(self, content, setting):
        for single_content in content:
            if 'filter' in setting:
                if not re.search(setting['filter'], single_content[setting['form']]):
                    continue

            modify_type = setting.get('type', ModifyType.Default)
            if ModifyType.Replace in modify_type:
                single_content[setting['to']] = single_content[setting['form']]
            else:
                if ModifyType.NewLine in modify_type:
                    single_content[setting['to']] = single_content[setting['to']] + "\n"+ single_content[setting['form']]
                else:
                    single_content[setting['to']] = single_content[setting['to']] + " " + single_content[setting['form']]

        return content

