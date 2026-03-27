#coding=utf-8

import os
import shutil
import pandas as pd
from matrix.games.d2rReimagined.D2rJob import D2rJob

class ModExporter(D2rJob):

    def __init__(self, options):
        D2rJob.__init__(self, options)

    def run(self):
        self.logger.info('start')

        print('\n请选择Mod格式:')
        print('1. D2R格式')
        print('2. D2RMM格式')
        print('=' * 50)

        format_choice = input('\n请选择格式 (1-2): ')

        if format_choice == '1':
            mod_root = self.get_d2r_config('d2r_reimagined_mod_root')
        elif format_choice == '2':
            mod_root = self.get_d2r_config('d2rmm_reimagined_mod_path')
        else:
            print('无效的选择')
            return

        if not os.path.exists(mod_root):
            self.logger.error(f'Mod目录不存在: {mod_root}')
            return

        excels_path = self.get_d2r_config('excels_path')
        os.makedirs(excels_path, exist_ok=True)

        self.logger.info(f'从Mod目录导出: {mod_root}')

        self._copy_excel_files(mod_root, excels_path)
        self._copy_string_files(mod_root, excels_path)

        print('\n是否将txt文件转换为xlsx? (y/n): ')
        convert_choice = input('').strip().lower()
        if convert_choice == 'y':
            self._convert_txt_to_xlsx(excels_path)

        self.logger.info('Mod目录导出完成')

    def _copy_excel_files(self, source_root, target_path):
        try:
            excel_source = os.path.join(source_root, 'data', 'global', 'excel')
            excel_target = os.path.join(target_path, 'excel')

            if not os.path.exists(excel_source):
                self.logger.warning(f'Excel源目录不存在: {excel_source}')
                return

            os.makedirs(excel_target, exist_ok=True)

            txt_files = [f for f in os.listdir(excel_source) if f.endswith('.txt')]
            self.logger.info(f'复制{len(txt_files)}个Excel文件...')

            for txt_file in txt_files:
                source_file = os.path.join(excel_source, txt_file)
                target_file = os.path.join(excel_target, txt_file)
                shutil.copy2(source_file, target_file)
                self.logger.info(f'复制: {txt_file}')

            self.logger.info(f'Excel文件已复制到: {excel_target}')

        except Exception as e:
            self.logger.error(f'复制Excel文件出错: {e}')

    def _copy_string_files(self, source_root, target_path):
        try:
            string_source = os.path.join(source_root, 'data', 'local', 'lng', 'strings')
            string_target = os.path.join(target_path, 'strings')

            if not os.path.exists(string_source):
                self.logger.warning(f'String源目录不存在: {string_source}')
                return

            os.makedirs(string_target, exist_ok=True)

            json_files = [f for f in os.listdir(string_source) if f.endswith('.json')]
            self.logger.info(f'复制{len(json_files)}个String文件...')

            for json_file in json_files:
                source_file = os.path.join(string_source, json_file)
                target_file = os.path.join(string_target, json_file)
                shutil.copy2(source_file, target_file)
                self.logger.info(f'复制: {json_file}')

            self.logger.info(f'String文件已复制到: {string_target}')

        except Exception as e:
            self.logger.error(f'复制String文件出错: {e}')

    def _convert_txt_to_xlsx(self, excels_path):
        try:
            excel_target = os.path.join(excels_path, 'excel')
            xlsx_path = excel_target + '-xlsx'

            if not os.path.exists(excel_target):
                self.logger.warning(f'Excel源目录不存在: {excel_target}')
                return

            os.makedirs(xlsx_path, exist_ok=True)

            txt_files = [f for f in os.listdir(excel_target) if f.endswith('.txt')]
            if not txt_files:
                self.logger.info(f'没有找到txt文件在: {excel_target}')
                return

            self.logger.info(f'开始转换{len(txt_files)}个txt文件...')

            for txt_file in txt_files:
                txt_file_path = os.path.join(excel_target, txt_file)
                xlsx_file = txt_file.replace('.txt', '.xlsx')
                xlsx_file_path = os.path.join(xlsx_path, xlsx_file)

                try:
                    df = pd.read_csv(txt_file_path, sep='\t', encoding='utf-8', low_memory=False)
                    df.to_excel(xlsx_file_path, index=False, engine='openpyxl')
                    self.logger.info(f'转换完成: {txt_file} -> {xlsx_file}')
                except Exception as e:
                    self.logger.error(f'转换失败 {txt_file}: {e}')

            self.logger.info(f'所有txt文件已转换到: {xlsx_path}')

        except Exception as e:
            self.logger.error(f'转换过程出错: {e}')
