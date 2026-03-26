#coding=utf-8

import json
import os
from matrix.games.d2rReimagined.D2rJob import D2rJob
from matrix.games.d2rReimagined.LanguageModify import LanguageModify

class ModOptimizer(D2rJob):

    def __init__(self, options):
        D2rJob.__init__(self, options)

    def run(self):
        self.logger.info('start')

        is_d2rmm_format = self.get_options('d2rmm_format', False)
        
        if is_d2rmm_format:
            work_path = self.d2r_config['d2rmm_reimagined_mod_path']
            self.logger.info(f'使用D2RMM格式，路径: {work_path}')
        else:
            work_path = self.d2r_config['d2r_reimagined_mod_root']
            self.logger.info(f'使用D2R格式，路径: {work_path}')

        self._optimize_text_content(work_path)
        self._optimize_json_files(work_path)
        
        self.logger.info('finished')

    def _optimize_text_content(self, work_path):
        self.logger.info('开始优化文本内容')

        language_path = os.path.join(work_path, 'data', 'local', 'lng', 'strings')

        if not os.path.exists(language_path):
            self.logger.warning(f'语言路径不存在: {language_path}')
            return

        options = {
            'work_path': language_path,
            'debug': self.get_options('debug', False)
        }

        language_modifier = LanguageModify(options)
        language_modifier.run()

        self.logger.info('文本内容优化完成')

    def _optimize_json_files(self, work_path):
        self.logger.info('开始优化JSON文件')

        json_files = [
            'data/hd/global/excel/desecratedzones.json',
        ]

        for json_file in json_files:
            json_path = os.path.join(work_path, json_file)

            if not os.path.exists(json_path):
                self.logger.warning(f'文件不存在: {json_path}')
                continue

            self._optimize_desecratedzones(json_path)

        self.logger.info('JSON文件优化完成')

    def _optimize_desecratedzones(self, json_path):
        self.logger.info(f'优化文件: {json_path}')

        try:
            force_terror_zones_path = os.path.join(
                self.d2r_config['d2r_beta_launcher_mods_path'],
                'Force Terror Zones',
                'mods',
                'Reimagined',
                'Reimagined.mpq',
                'data',
                'hd',
                'global',
                'excel',
                'desecratedzones.json'
            )

            if not os.path.exists(force_terror_zones_path):
                self.logger.warning(f'Force Terror Zones文件不存在: {force_terror_zones_path}')
                return

            with open(force_terror_zones_path, 'r', encoding='utf-8') as f:
                source_data = json.load(f)

            with open(json_path, 'r', encoding='utf-8') as f:
                target_data = json.load(f)

            if 'desecrated_zones' in source_data and 'desecrated_zones' in target_data:
                for i, source_zone in enumerate(source_data['desecrated_zones']):
                    if i < len(target_data['desecrated_zones']):
                        target_zone = target_data['desecrated_zones'][i]
                        
                        if 'manual_zones' in source_zone:
                            target_zone['manual_zones'] = source_zone['manual_zones']
                            self.logger.info(f'已更新第{i+1}个区域的manual_zones')
                        
                        if 'zones' in source_zone:
                            target_zone['zones'] = source_zone['zones']
                            self.logger.info(f'已更新第{i+1}个区域的zones')

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(target_data, f, ensure_ascii=False, indent=4)

            self.logger.info(f'文件优化完成: {json_path}')

        except json.JSONDecodeError as e:
            self.logger.error(f'JSON解析失败: {json_path}, 错误: {e}')
        except Exception as e:
            self.logger.error(f'优化文件时发生错误: {json_path}, 错误: {e}')
