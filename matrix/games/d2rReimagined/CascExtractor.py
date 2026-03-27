#coding=utf-8

import os
import subprocess
import shutil
import pandas as pd
from matrix.games.d2rReimagined.D2rJob import D2rJob

class CascExtractor(D2rJob):

    def __init__(self, options):
        D2rJob.__init__(self, options)

    def run(self):
        self.logger.info('start')

        casc_console = self.get_d2r_config('casc_console_path')
        d2r_root = self.get_d2r_config('d2r_root')
        vanilla_path = self.get_d2r_config('vanilla_path')

        if not os.path.exists(casc_console):
            self.logger.error(f'Casc工具不存在: {casc_console}')
            return

        if not os.path.exists(d2r_root):
            self.logger.error(f'D2R根目录不存在: {d2r_root}')
            return

        os.makedirs(vanilla_path, exist_ok=True)

        self.logger.info('\nCasc数据提取工具')
        self.logger.info('=' * 50)
        self.logger.info(f'Casc工具: {casc_console}')
        self.logger.info(f'D2R根目录: {d2r_root}')
        self.logger.info(f'输出目录: {vanilla_path}')
        self.logger.info('=' * 50)

        print('\n常用数据目录:')
        print('1. Excel文件 (data/global/excel/)')
        print('2. 语言文件 (data/local/lng/strings/)')
        print('3. 全部Excel和语言文件')
        print('4. 自定义路径')
        print('=' * 50)

        choice = input('\n请选择要提取的数据类型 (1-4): ')

        if choice == '1':
            self._extract_excel_directory(casc_console, d2r_root, vanilla_path)
        elif choice == '2':
            self._extract_language_directory(casc_console, d2r_root, vanilla_path)
        elif choice == '3':
            self._extract_all_directories(casc_console, d2r_root, vanilla_path)
        elif choice == '4':
            self._extract_custom_path(casc_console, d2r_root, vanilla_path)
        else:
            print('无效的选择')

    def _extract_excel_directory(self, casc_console, d2r_root, output_path):
        directory_path = 'data/global/excel/'
        self.logger.info(f'\n开始提取Excel目录: {directory_path}')
        self._extract_directory(casc_console, d2r_root, output_path, directory_path)
        
        convert_choice = input('\n是否将txt文件转换为xlsx? (y/n): ').strip().lower()
        if convert_choice == 'y':
            self._convert_txt_to_xlsx(output_path, 'excel')
        
        self.logger.info('Excel目录提取完成')

    def _extract_language_directory(self, casc_console, d2r_root, output_path):
        directory_path = 'data/local/lng/strings/'
        self.logger.info(f'\n开始提取语言目录: {directory_path}')
        self._extract_directory(casc_console, d2r_root, output_path, directory_path)
        self.logger.info('语言目录提取完成')

    def _extract_all_directories(self, casc_console, d2r_root, output_path):
        self.logger.info('\n开始提取所有目录...')
        self._extract_excel_directory(casc_console, d2r_root, output_path)
        self._extract_language_directory(casc_console, d2r_root, output_path)
        self.logger.info('所有目录提取完成')

    def _extract_custom_path(self, casc_console, d2r_root, output_path):
        path = input('\n请输入要提取的路径 (如: data/global/excel/): ').strip()
        if path:
            self.logger.info(f'\n开始提取: {path}')
            self._extract_directory(casc_console, d2r_root, output_path, path)
            self.logger.info('提取完成')

    def _extract_directory(self, casc_console, d2r_root, output_path, directory_path):
        try:
            target_dir = directory_path.rstrip('/').split('/')[-1]
            pattern_path = 'data/' + directory_path.rstrip('/') + '/*.*'
            
            cmd = [
                casc_console,
                '-l', 'None',
                '-d', output_path,
                '-s', d2r_root,
                '-m', 'Pattern',
                '-e', pattern_path,
                '-p', 'osi'
            ]

            self.logger.info(f'提取模式: {pattern_path}')
            self.logger.info(f'目标目录: {target_dir}')
            self.logger.info(f'执行命令: {" ".join(cmd)}')
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                self.logger.info(f'成功提取: {pattern_path}')
                self._move_extracted_files(output_path, directory_path, target_dir)
            else:
                self.logger.error(f'提取失败: {pattern_path}, 错误: {result.stderr}')

        except Exception as e:
            self.logger.error(f'提取目录出错 {pattern_path}: {e}')

    def _move_extracted_files(self, output_path, directory_path, target_dir):
        try:
            source_dir = os.path.join(output_path, 'data', directory_path.rstrip('/'))
            target_path = os.path.join(output_path, target_dir)

            if os.path.exists(source_dir):
                if os.path.exists(target_path):
                    shutil.rmtree(target_path)
                shutil.move(source_dir, target_path)
                self.logger.info(f'文件已移动到: {target_path}')

                data_dir = os.path.join(output_path, 'data')
                if os.path.exists(data_dir):
                    shutil.rmtree(data_dir)
                    self.logger.info(f'删除目录: {data_dir}')
            else:
                self.logger.warning(f'源目录不存在: {source_dir}')

        except Exception as e:
            self.logger.error(f'移动文件出错: {e}')

    def _convert_txt_to_xlsx(self, output_path, target_dir):
        try:
            source_dir = os.path.join(output_path, target_dir)
            xlsx_dir = os.path.join(output_path, target_dir + '-xlsx')

            if not os.path.exists(source_dir):
                self.logger.warning(f'源目录不存在: {source_dir}')
                return

            os.makedirs(xlsx_dir, exist_ok=True)

            txt_files = [f for f in os.listdir(source_dir) if f.endswith('.txt')]
            if not txt_files:
                self.logger.info(f'没有找到txt文件在: {source_dir}')
                return

            self.logger.info(f'开始转换 {len(txt_files)} 个txt文件...')

            for txt_file in txt_files:
                txt_path = os.path.join(source_dir, txt_file)
                xlsx_file = txt_file.replace('.txt', '.xlsx')
                xlsx_path = os.path.join(xlsx_dir, xlsx_file)

                try:
                    df = pd.read_csv(txt_path, sep='\t', encoding='utf-8', low_memory=False)
                    df.to_excel(xlsx_path, index=False, engine='openpyxl')
                    self.logger.info(f'转换完成: {txt_file} -> {xlsx_file}')
                except Exception as e:
                    self.logger.error(f'转换失败 {txt_file}: {e}')

            self.logger.info(f'所有txt文件已转换到: {xlsx_dir}')

        except Exception as e:
            self.logger.error(f'转换过程出错: {e}')
