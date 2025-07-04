#coding=utf-8

import os
import shutil

import yaml
import pandas as pd
from matrix.games.d2rReimagined import * 
from matrix.base.BaseJob import BaseJob

class ItemDetailsGenerator(BaseJob):
    excel_relative_path = 'data/global/excel/'

    excel_path = None
    work_path = None
    debug_path = None
    original_path = None
    language_path = None

    hero_level = 90

    base_item_info = {
        'file_names' : [
            'armor.txt',
            'weapons.txt',
            'misc.txt',
        ],
        'fields': {
            'BaseItem' : 'name',
            'Type': 'type',
        }
    }

    property_modify_list = [
        {
            'output_column': 'swing',
            'columns': ["swing1.max", "swing2.max", "swing3.max"],
        },
        {
            'output_column': 'crush',
            'columns':  ['crush.max', 'crush/lvl.parm'],
            'weights': [1, hero_level/8],
        },
        {
            'output_column': 'openwounds',
            'columns':  ['openwounds.max', 'wounds/lvl.parm'],
            'weights': [1, hero_level/8],
        },
    ]

    file_and_field_list = [
        {
            'file_name': 'uniqueitems.txt',
            'max_original_index': 404,
            'fields': {
                'Name' : 'index',
                'code' : 'code',
                'Lvl.Req': 'lvl req',
                'Index': '*ID'
            },
            'prop_fields': {
                'prop_name' : 'prop',
                'param_name' : 'par',
                'min_value' : 'min',
                'max_value' : 'max',
            },
        },
        {
            'file_name': 'setitems.txt',
            'max_original_index': 126,
            'fields': {
                'Name' : 'index',
                'code': 'item',
                'Lvl.Req': 'lvl req',
                'Index': '*ID'
            },
            'prop_fields': {
                'prop_name' : 'prop',
                'param_name' : 'par',
                'min_value' : 'min',
                'max_value' : 'max',
            },
        },
        {
            'file_name': 'runes.txt',
            'fields': {
                'Name' : '*Rune Name',
                'itype1': 'itype1',
                'itype2': 'itype2',
                'itype3': 'itype3',
                'itype4': 'itype4',
                'itype5': 'itype5',
                'itype6': 'itype6',
                'Rune1': 'Rune1',
                'Rune2': 'Rune2',
                'Rune3': 'Rune3',
                'Rune4': 'Rune4',
                'Rune5': 'Rune5',
                'Rune6': 'Rune6',
            },
            'prop_fields': {
                'prop_name' : 'T1Code',
                'param_name' : 'T1Param',
                'min_value' : 'T1Min',
                'max_value' : 'T1Max',
            },
        }
    ]

    def __init__(self, options):
        BaseJob.__init__(self, options)

        yaml_path = os.path.join(os.path.dirname(__file__), 'D2rrConfig.yaml')

        with open(yaml_path, 'r', encoding='utf-8') as f:
            self.d2r_config = yaml.load(f, yaml.FullLoader)

        self.excel_path = os.path.join(self.d2r_config['mod_d2rr_root'], self.excel_relative_path)
        self.work_path = self.get_options('work_path')
        self.debug_path = os.path.join(self.work_path, 'debug_generate')
        self.original_path = os.path.join(self.work_path, 'original_excel')
        self.language_path = os.path.join(self.d2r_config['mod_d2rr_root'], 'data/local/lng/strings/original/')

        if os.path.exists(self.debug_path):
            shutil.rmtree(self.debug_path)
        os.makedirs(self.debug_path)

    def run(self):
        self.logger.info('start')

        if not os.path.exists(self.excel_path):
            self.logger.error(f'Excel directory not found: {self.excel_path}')
            return
        
        self.load_item_type()

        # 初始化空DataFrame
        combined_items_df = pd.DataFrame()

        for file_and_field in self.file_and_field_list:
            # print(file_and_field)
            file_name = file_and_field['file_name']
            file_path = os.path.join(self.excel_path, file_name)
            if not os.path.exists(file_path):
                self.logger.error(f'File not found: {file_path}')
                continue

            # 读取CSV文件并转换
            items_df = self.read_csv_file(file_path, file_and_field['fields'], file_and_field['prop_fields'])
            items_df = items_df.copy()
            items_df['source'] = os.path.splitext(file_name)[0]  # 添加文件名列

            items_df.to_excel(os.path.join(self.debug_path, f'{file_name}.xlsx'), index=False)
            if file_name == 'runes.txt':
                items_df = self.modify_rune_item_df(items_df, file_and_field)

            if 'max_original_index' in file_and_field:
                items_df = items_df.dropna(subset=['Index'])
                items_df['isOriginal'] = items_df['Index'].apply(lambda x: 'True' if x < file_and_field['max_original_index'] else '')

            # 追加到总DataFrame
            combined_items_df = pd.concat([combined_items_df, items_df], ignore_index=True)

        # combined_items_df.to_excel(os.path.join(self.debug_path, 'combined_items_df.xlsx'), index=False)

        combined_items_df = remove_all_empty_columns(combined_items_df)

        self.logger.info('合并基础物品信息')
        items_df = self.merge_base_item_info(combined_items_df)

        self.logger.info('修改合并物品属性')
        items_df = self.merge_and_modify_property(items_df)
    
        # items_df.to_excel(os.path.join(self.debug_path, 'items_df.xlsx'), index=False)

        skill_path = os.path.join(self.excel_path, 'skills.txt')
        self.logger.info(f'读取技能信息')
        items_df = self.match_and_replace(items_df, ['aura.parm', 'hit-skill.parm'],
                                        skill_path, '*Id', 'skill')
        
        output_file = os.path.join(self.work_path, 'ItemDetails.xlsx')
        self.logger.info(f"数据导出到 {output_file}")
        items_df.to_excel(output_file, index=False)
        self.logger.info("导出完成")

    def modify_rune_item_df(self, items_df, file_and_field):
        items_df = self.map_typeshort_to_type(        
            input_df = items_df,
            mapping_df = self.item_type_mappings,
            code_columns=['itype1', 'itype2', 'itype3', 'itype4', 'itype5', 'itype6']
        )
        items_df['code'] = 'None'

        completed_file_path = os.path.join(self.original_path, 'runes_completed.txt')
        if not os.path.exists(completed_file_path):
            self.logger.error(f'File not found: {completed_file_path}')
            return items_df

        # 读取CSV文件并转换
        completed_items_df = self.read_csv_file(completed_file_path, file_and_field['fields'])

        items_df['isOriginal'] = items_df['Name'].isin(completed_items_df['Name']).map({True: 'True', False: ''})

        # 根据rune处理等级需求
        rune_columns = [col for col in items_df.columns if col.startswith('Rune')]
        
        for col in rune_columns:
            # 先将空值（包括 NaN、空字符串、非数字字符）替换为 'r0'，再提取数字
            items_df[col] = items_df[col].fillna('r0').str.extract(r'(\d+)', expand=False).astype(int)
        items_df['Lvl.Req'] = items_df[rune_columns].max(axis=1) * 2 + 3

        return items_df
    
    def match_and_replace(self, source_df, source_column_list, findin_path, find_column, replace_column):
        findin_df = read_file_to_dataframe(findin_path)

        findin_mapping = {
            str(find).lower(): replace
            for find, replace in zip(findin_df[find_column], findin_df[replace_column])
        }

        result_df = source_df.copy()

        for column in source_column_list:
            result_df[column] = result_df[column].map(
                lambda x: findin_mapping.get(str(x).lower(), x) if pd.notna(x) else x
            )

        return result_df
        
    def map_typeshort_to_type(self, input_df, mapping_df, code_columns, output_column='itype'):
        """
        将DataFrame中的代码列映射为对应的物品类型
        
        参数:
        input_df (pd.DataFrame): 包含代码列的输入DataFrame
        mapping_df (pd.DataFrame): 包含代码到物品类型映射的DataFrame
        code_columns (list): 需要映射的代码列名列表
        
        返回:
        pd.DataFrame: 包含映射结果的DataFrame
        """
        # 创建代码到物品类型的映射字典（忽略大小写）
        code_to_itemtype = {
            TypeShort: item_type 
            for TypeShort, item_type in zip(mapping_df['TypeShort'], mapping_df['Type'])
        }
        
        # 复制原始DataFrame，避免修改原数据
        result_df = input_df.copy()
        
        # 对每行中的每个代码列进行映射，并合并结果
        result_df[output_column] = result_df[code_columns].apply(
            lambda row: ','.join(
                code_to_itemtype.get(str(code).lower(), code)  # 找不到映射时保留原代码
                for code in row 
                if pd.notna(code)
            ),
            axis=1
        )
        
        result_df.to_excel(os.path.join(self.debug_path, f'result_df.xlsx'), index=False)

        return result_df
    
    def merge_and_modify_property(self, items_df):

        for modify_config in self.property_modify_list:
            output_column = modify_config['output_column']
            columns = modify_config['columns']
            weights = modify_config.get('weights', [1] * len(columns))

            # 计算加权和，将空值视为0
            items_df[output_column] = sum(pd.to_numeric(items_df[col]).fillna(0) * weight for col, weight in zip(columns, weights))
            # items_df[output_column] = items_df[output_column].replace(0, pd.NA)
            items_df = items_df.drop(columns=columns)

        return items_df
    
    def merge_base_item_info(self, items_df):

        # print(items_df)
        # print(self.base_item_mappings)

        # 合并到主DataFrame
        merged_df = items_df.merge(
            self.base_item_mappings,
            on='code',
            how='left',
            suffixes=('', '_1')
        )


        # 将itype列的值合并到Type列中，按指定规则处理

        def merge_values(row):
            type_val = row['Type']
            itype_val = row['itype']
            
            # 如果Type为空，用itype填充
            if pd.isna(type_val) or type_val == 'None':
                return itype_val
            # 如果itype为空，保持Type不变
            elif pd.isna(itype_val):
                return type_val
            # 如果两者都不为空，使用Type并记录警告
            else:
                self.logger.warning(f"行 {row.name}: Type='{type_val}' 和 itype='{itype_val}' 都不为空，使用Type")
                return type_val
        
        # 应用合并逻辑
        merged_df['Type'] = merged_df.apply(merge_values, axis=1)

        # print(merged_df)
        return merged_df

    def load_base_item_info(self, excel_path):
        config = self.base_item_info
        # 选择需要的列并添加到总映射
        name_col = config['fields']['BaseItem']
        type_col = config['fields']['Type']
        base_item_mapping = pd.DataFrame(columns=['code', name_col, type_col])
 
        # 读取并合并所有映射表
        for file_name in config['file_names']:
            file_path = os.path.join(excel_path, file_name)
            try:
                # 根据文件扩展名选择读取方法
                if file_path.endswith('.txt'):
                    mapping_df = pd.read_csv(file_path, sep='\t')
                elif file_path.endswith(('.xlsx', '.xls')):
                    mapping_df = pd.read_excel(file_path)
                else:
                    print(f"不支持的文件格式: {file_path}")
                    continue

                mapping_df['MainType'] = file_name.split('.')[0]
                    
                if name_col in mapping_df.columns and type_col in mapping_df.columns:
                    base_item_mapping = pd.concat([
                        base_item_mapping,
                        mapping_df[['code', name_col, type_col,'MainType']]
                    ], ignore_index=True)
                else:
                    print(f"映射表 {file_path} 缺少必要的列: {name_col} 或 {type_col}")
            except Exception as e:
                print(f"读取映射表 {file_path} 时出错: {e}")

        base_item_mapping.to_excel(os.path.join(self.debug_path, 'base_item_mapping00.xlsx'))
        
        # 去除空白项
        base_item_mapping = base_item_mapping[base_item_mapping['code'].notna()]

        base_item_mapping = base_item_mapping.rename(columns={
            config['fields']['BaseItem']: 'BaseItem',
            config['fields']['Type']: 'TypeShort'
        })

        return base_item_mapping

    def load_item_type(self):
        base_item_mapping = self.load_base_item_info(self.excel_path)

        #     code     BaseItem TypeShort
        # 0    cap          Cap      helm
        # 1    skp    Skull Cap      helm
        # 2    hlm         Helm      helm

        # print(base_item_mapping)
        base_item_mapping.to_excel(os.path.join(self.debug_path, 'base_item_mapping.xlsx'), index=False)

        file_path = os.path.join(self.excel_path, 'itemtypes.txt')

        itemtype_df = read_file_to_dataframe(file_path)

        itemtype_df = itemtype_df.rename(columns={
            'Code': 'TypeShort',
            'ItemType': 'Type'
        })
        itemtype_df = itemtype_df[['TypeShort', 'Type', 'BodyLoc1']]
        itemtype_df.loc[itemtype_df['TypeShort'] == 'helm', 'Type'] = 'Helm'

        #     TypeShort                 Type
        # 0         NaN                  Any
        # 1        none                  NaN
        # 2        shie               Shield
        # 3        tors                Armor

        # print(itemtype_df)
        # itemtype_df.to_excel(os.path.join(self.debug_path, 'itemtype_df.xlsx'), index=False)

        # 合并到主DataFrame
        merged_base_item_mapping = base_item_mapping.merge(
            itemtype_df,
            left_on='TypeShort',
            right_on='TypeShort',
            how='left',
            suffixes=('', '_1')
        )

        # merged_base_item_mapping.to_excel(os.path.join(self.debug_path, 'merged_base_item_mapping.xlsx'), index=False)

        # print(merged_df)
        self.item_type_mappings = itemtype_df
        self.base_item_mappings = merged_base_item_mapping
        # code	BaseItem	TypeShort	Type
        # cap	Cap	helm	Helm
        # skp	Skull Cap	helm	Helm
        # hlm	Helm	helm	Helm
        # fhl	Full Helm	helm	Helm

        merged_base_item_mapping.to_excel(os.path.join(self.debug_path, 'merged_base_item_mapping.xlsx'), index=False)


    def read_csv_file(self, item_file_path, fields, prop_fields = None):
        
        self.logger.info(f'Reading file: {item_file_path}')
            
        df = pd.read_csv(item_file_path, index_col=False, sep='\t')

        self.logger.info(f'读取属性信息')
        def transform_row(row):
            result = {}

            for key, value in fields.items():
                v = row[value]
                if pd.notna(v) and isinstance(v, float):
                    v = int(v)
                result[key] = v

            if prop_fields is None:
                return pd.Series(result)

            num_props = len([col for col in df.columns if col.startswith(prop_fields['prop_name'])])

            for i in range(1, num_props + 1):
                prop = row[prop_fields['prop_name'] + f'{i}']
                par = row[prop_fields['param_name'] + f'{i}']
                min_val = row[prop_fields['min_value'] + f'{i}']
                max_val = row[prop_fields['max_value'] + f'{i}']
                
                # 添加 .min 和 .max 键值对

                if prop == 'oskill':
                    if f"{prop}.parm" in result:
                        result[f"{prop}.parm"] = result[f"{prop}.parm"] + '\n' + par
                        result[f"{prop}.min"] = str(result[f"{prop}.min"]) + '\n' + str(int(min_val))
                        result[f"{prop}.max"] = str(result[f"{prop}.max"]) + '\n' + str(int(max_val))
                    else:
                        result[f"{prop}.parm"] = par
                        result[f"{prop}.min"] = int(min_val)
                        result[f"{prop}.max"] = int(max_val)
                else:
                    result[f"{prop}.parm"] = par
                    result[f"{prop}.min"] = min_val
                    result[f"{prop}.max"] = max_val

            return pd.Series(result)
        
        transformed_df = df.apply(transform_row, axis=1)
        return transformed_df

