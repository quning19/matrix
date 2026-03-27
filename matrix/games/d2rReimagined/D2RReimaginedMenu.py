#coding=utf-8

import os
from matrix.games.d2rReimagined.D2rJob import D2rJob

class D2RReimaginedMenu(D2rJob):

    def __init__(self, options):
        D2rJob.__init__(self, options)
  
    def run(self):
        commands = [
            {'name': 'Mod Optimizer', 'cmd': 'd2ro', 'desc': 'Mod优化工具'},
            {'name': 'Item Finder', 'cmd': 'd2rf', 'desc': '物品查找器'},
            {'name': 'Item Details', 'cmd': 'd2rd', 'desc': '物品详情生成'},
            {'name': 'Casc Extractor', 'cmd': 'd2rc', 'desc': 'Casc数据提取工具'},
            {'name': 'Mod Exporter', 'cmd': 'd2re', 'desc': 'Mod文件导出工具'},
        ]

        print('\nD2R Reimagined 工具集')
        print('=' * 50)
        for i, cmd in enumerate(commands, 1):
            print(f'{i}. {cmd["name"]} ({cmd["cmd"]}) - {cmd["desc"]}')
        print('=' * 50)

        choice = input('\n请输入序号选择要执行的命令 (x退出): ')
        
        try:
            if choice.strip().lower() == 'x':
                self.logger.info('用户选择退出')
                return

            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(commands):
                selected_cmd = commands[choice_idx]
                print(f'\n执行: {selected_cmd["name"]}\n')
                
                if selected_cmd['cmd'] == 'd2rf':
                    self._run_item_finder()
                elif selected_cmd['cmd'] == 'd2rd':
                    self._run_item_details()
                elif selected_cmd['cmd'] == 'd2ro':
                    self._run_mod_optimizer()
                elif selected_cmd['cmd'] == 'd2rc':
                    self._run_casc_extractor()
                elif selected_cmd['cmd'] == 'd2re':
                    self._run_mod_exporter()
            else:
                print('无效的选择')
        except ValueError:
            print('请输入有效的数字')
        except Exception as e:
            self.logger.error(f'执行出错: {e}')

    def _run_item_finder(self):
        from matrix.games.d2rReimagined.ItemFinder import ItemFinder
        work_path = self.get_d2r_config('work_path', os.path.join(os.path.dirname(__file__), 'output'))
        options = {'work_path': work_path}
        job = ItemFinder(options)
        job.run()

    def _run_item_details(self):
        from matrix.games.d2rReimagined.ItemDetailsGenerator import ItemDetailsGenerator
        original_path = self.get_d2r_config('original_path', os.path.join(os.path.dirname(__file__), 'original_excel'))
        work_path = self.get_d2r_config('work_path', os.path.join(os.path.dirname(__file__), 'output'))
        options = {'original_path': original_path, 'work_path': work_path}
        job = ItemDetailsGenerator(options)
        job.run()

    def _run_mod_optimizer(self):
        from matrix.games.d2rReimagined.ModOptimizer import ModOptimizer
        d2rmm_format_input = input('请输入格式选择(0:D2R, 1:D2RMM): ')
        try:
            d2rmm_format = int(d2rmm_format_input) == 1
        except ValueError:
            print('输入无效，默认使用D2R格式')
            d2rmm_format = False
            
        options = {'d2rmm_format': d2rmm_format, 'debug': self.get_options('debug', False)}
        job = ModOptimizer(options)
        job.run()

    def _run_casc_extractor(self):
        from matrix.games.d2rReimagined.CascExtractor import CascExtractor
        options = {}
        job = CascExtractor(options)
        job.run()

    def _run_mod_exporter(self):
        from matrix.games.d2rReimagined.ModExporter import ModExporter
        options = {}
        job = ModExporter(options)
        job.run()
