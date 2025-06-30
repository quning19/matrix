#coding=utf-8

import os
import shutil

import yaml
import pandas as pd
from openpyxl.styles import Font, Alignment
from matrix.base.BaseJob import BaseJob

class ItemDetailsGenerator(BaseJob):
    excel_relative_path = 'data/global/excel/'

    excel_path = None
    work_path = None
    debug_path = None
    original_path = None
    language_path = None

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

        # 去除重复项（根据需求选择是否执行）
        self.logger.info('去除重复项')
        combined_items_df = combined_items_df.drop_duplicates()

        # combined_items_df.to_excel(os.path.join(self.debug_path, 'combined_items_df.xlsx'), index=False)

        self.logger.info('合并基础物品信息')
        items_df = self.merge_base_item_info(combined_items_df)

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
        
        # 去除重复项
        base_item_mapping = base_item_mapping.drop_duplicates(subset=['code'])

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


class ItemFinder(BaseJob):

    excel_relative_path = 'data/global/excel/'
    excel_path = None
    work_path = None
    debug_path = None

    config_list = [
        {
            'enable': True,
            'export_name': 'Bow & Crossbow Valueable',
            'check_conditions': {
                'logic': 'AND',
                'conditions': [
                    {"path": "Type", "operator": "in", "threshold": ['Bow', 'Amazon Bow', 'Crossbow', 'Magic Bow Quiv', 'Magic Xbow Quiv', 'Missile Weapon']},
                    {
                        'logic': 'OR',
                        'conditions': [
                            {"path": "hit-skill.max", "operator": ">", "threshold": 0},      # 触发技能
                            {"path": "aura.max", "operator": ">", "threshold": 0},      # 光环
                            {"path": "pierce.max", "operator": ">", "threshold": 0},    # 穿刺
                            {"path": "explosivearrow.max", "operator": ">", "threshold": 0},    # 爆炸箭
                        ]
                    },
                ]
            },

            'export_mapping': {
                'Name': 'Name',
                'isOriginal': 'isOriginal',
                'Source': 'source',
                'MainType': 'MainType',
                'Type': 'Type',
                'BaseItem': 'BaseItem',
                'Lvl.Req': 'Lvl.Req',
                'AllSkills': 'allskills.max',
                'Amazon Skill': 'ama.max',
                'Amazon Skill': 'skilltab.parm',
                'Bow or Passive Skill': 'skilltab.max',
                'Explosive Arrow': 'explosivearrow.max',
                'Piercing Attack': 'pierce.max',
                'Aura': 'aura.parm',
                'Aura Lvl': 'aura.max',
                'oskill': 'oskill.parm',
                'oskill Level': 'oskill.max',
                'hit-skill': 'hit-skill.parm',
                'hit-skill rate': 'hit-skill.max',
                'Faster Cast Rate1': 'cast1.max',
                'Faster Cast Rate2': 'cast2.max',
                'Faster Cast Rate3': 'cast3.max',
                'AR.min': 'res-all.min',
                'AR.max': 'res-all.max',
            }
        },
        {
            'enable': True,
            'export_name': 'OSkill Items',
            'check_conditions': {
                'logic': 'AND',
                'conditions': [
                    {"path": "oskill.parm", "operator": "notnull"},
                ]
            },

            'export_mapping': {
                'Name': 'Name',
                'isOriginal': 'isOriginal',
                'Source': 'source',
                'MainType': 'MainType',
                'Type': 'Type',
                'BaseItem': 'BaseItem',
                'Lvl.Req': 'Lvl.Req',
                'oskill': 'oskill.parm',
                'oskill Level': 'oskill.max',
                'AllSkills': 'allskills.max',
                'Amazon Skill': 'ama.max',
                'Amazon Skill': 'skilltab.parm',
                'Bow or Passive Skill': 'skilltab.max',
                'Explosive Arrow': 'explosivearrow.max',
                'Piercing Attack': 'pierce.max',
                'Aura': 'aura.parm',
                'Aura Lvl': 'aura.max',
                'hit-skill': 'hit-skill.parm',
                'hit-skill rate': 'hit-skill.max',
                'AR.min': 'res-all.min',
                'AR.max': 'res-all.max',
            }
        },
        {
            'enable': True,
            'export_name': 'Hit Skills Items',
            'check_conditions': {
                'logic': 'AND',
                'conditions': [
                    {"path": "hit-skill.max", "operator": ">", "threshold": 0},      # 光环  
                ]
            },

            'export_mapping': {
                'Name': 'Name',
                'isOriginal': 'isOriginal',
                'Source': 'source',
                'MainType': 'MainType',
                'Type': 'Type',
                'BaseItem': 'BaseItem',
                'Lvl.Req': 'Lvl.Req',
                'hit-skill': 'hit-skill.parm',
                'hit-skill rate': 'hit-skill.max',
                'AllSkills': 'allskills.max',
                'Amazon Skill': 'ama.max',
                'Amazon Skill': 'skilltab.parm',
                'Bow or Passive Skill': 'skilltab.max',
                'Explosive Arrow': 'explosivearrow.max',
                'Piercing Attack': 'pierce.max',
                'Aura': 'aura.parm',
                'Aura Lvl': 'aura.max',
                'oskill': 'oskill.parm',
                'oskill Level': 'oskill.max',
                'AR.min': 'res-all.min',
                'AR.max': 'res-all.max',
            }
        },
        {
            'enable': True,
            'export_name': 'Aura Items',
            'check_conditions': {
                'logic': 'AND',
                'conditions': [
                    {"path": "aura.max", "operator": ">", "threshold": 0},      # 光环  
                ]
            },

            'export_mapping': {
                'Name': 'Name',
                'isOriginal': 'isOriginal',
                'Source': 'source',
                'MainType': 'MainType',
                'Type': 'Type',
                'BaseItem': 'BaseItem',
                'Lvl.Req': 'Lvl.Req',
                'Aura': 'aura.parm',
                'Aura Lvl': 'aura.max',
                'AllSkills': 'allskills.max',
                'Amazon Skill': 'ama.max',
                'Amazon Skill': 'skilltab.parm',
                'Bow or Passive Skill': 'skilltab.max',
                'Explosive Arrow': 'explosivearrow.max',
                'Piercing Attack': 'pierce.max',
                'oskill': 'oskill.parm',
                'oskill Level': 'oskill.max',
                'hit-skill': 'hit-skill.parm',
                'hit-skill rate': 'hit-skill.max',
                'AR.min': 'res-all.min',
                'AR.max': 'res-all.max',
            }
        },
        {
            'enable': False,
            'export_name': 'Rings & Amulets with Skills',
            'check_conditions': {
                'logic': 'AND',
                'conditions': [
                    {"path": "Type", "operator": "in", "threshold": ['Ring', 'Amulet']},
                    {
                        'logic': 'OR',
                        'conditions': [
                            {"path": "allskills.max", "operator": ">=", "threshold": 1},
                            {"path": "coldskill.max", "operator": ">=", "threshold": 1},
                            {"path": "sor.max", "operator": ">=", "threshold": 1},
                        ]
                    },

                ]
            },

            'export_mapping': {
                'Name': 'Name',
                'isOriginal': 'isOriginal',
                'Source': 'source',
                'MainType': 'MainType',
                'Type': 'Type',
                'BaseItem': 'BaseItem',
                'Lvl.Req': 'Lvl.Req',
                'location': 'BodyLoc1',
                'hit-skill': 'hit-skill.parm',
                'Faster Cast Rate1': 'cast1.max',
                'Faster Cast Rate2': 'cast2.max',
                'Faster Cast Rate3': 'cast3.max',
                'AllSkills': 'allskills.max',
                'Cold Skill': 'coldskill.max',
                'Sorceress Skill': 'sor.max',
                'oskill': 'oskill.parm',
                'AR.min': 'res-all.min',
                'AR.max': 'res-all.max',
            }
        },
        {
            'enable': False,
            'export_name': 'Gloves IAS & skill',
            'check_conditions': {
                'logic': 'AND',
                'conditions': [
                    {"path": "Type", "operator": "==", "threshold": 'Gloves'},
                    # {"path": ["swing1.max","swing2.max","swing3.max"], "operator": ">", "threshold": 0},
                    {
                        'logic': 'OR',
                        'conditions': [
                            # {"path": "res-all.min", "operator": ">", "threshold": 10},
                            {"path": "oskill.parm", "operator": "notnull"},
                            {"path": "hit-skill.parm", "operator": "notnull"},
                        ]
                    },

                ]
            },

            'export_mapping': {
                'Name': 'Name',
                'isOriginal': 'isOriginal',
                'Source': 'source',
                'MainType': 'MainType',
                'Type': 'Type',
                'BaseItem': 'BaseItem',
                'Lvl.Req': 'Lvl.Req',
                'location': 'BodyLoc1',
                'hit-skill': 'hit-skill.parm',
                'IAS1': 'swing1.max',
                'IAS2': 'swing2.max',
                'IAS3': 'swing3.max',
                'oskill': 'oskill.parm',
                'AR.min': 'res-all.min',
                'AR.max': 'res-all.max',
            }
        },
        {
            'enable': False,
            'export_name': 'Pet Aura',
            'check_conditions': {
                'logic': 'OR',
                'conditions': [
                    {"path": "aura.max", "operator": ">", "threshold": 0},
                ]
            },

            'export_mapping': {
                'Name': 'Name',
                'isOriginal': 'isOriginal',
                'Source': 'source',
                'MainType': 'MainType',
                'Type': 'Type',
                'BaseItem': 'BaseItem',
                'Lvl.Req': 'Lvl.Req',
                'location': 'BodyLoc1',
                'Aura': 'aura.parm',
                'Aura Lvl': 'aura.max',
                'hit-skill': 'hit-skill.parm',
                'oskill': 'oskill.parm',
                'AR.min': 'res-all.min',
                'AR.max': 'res-all.max',
            }
        },
        {
            'enable': False,
            'export_name': 'Cold Damage',
            'check_conditions': {
                'logic': 'OR',
                'conditions': [
                    # 审判光环
                    {"path": "aura.parm", "operator": "==", "threshold": 'Conviction'},
                    # 降低冰抗
                    {"path": "pierce-cold.max", "operator": ">", "threshold": 10},
                    # 技能且FCR
                    {
                        'logic': 'AND',
                        'conditions': [
                            {"path": "cast3.max", "operator": ">", "threshold": 10},
                            {
                                'logic': 'OR',
                                'conditions': [
                                    {"path": "allskills.max", "operator": ">=", "threshold": 1},
                                    {"path": "coldskill.max", "operator": ">=", "threshold": 1},
                                    {"path": "sor.max", "operator": ">=", "threshold": 1},
                                ]
                            },
                        ]
                    },
                    # mf
                    {"path": "mag%/lvl.parm", "operator": ">=", "threshold": 5},
                    {"path": "mag%.max", "operator": ">=", "threshold": 30},
                ]

            },

            'export_mapping': {
                'Name': 'Name',
                'isOriginal': 'isOriginal',
                'Source': 'source',
                'MainType': 'MainType',
                'Type': 'Type',
                'BaseItem': 'BaseItem',
                'Lvl.Req': 'Lvl.Req',
                'location': 'BodyLoc1',
                'Aura': 'aura.parm',
                'Aura Lvl': 'aura.max',
                'Enemy Cold Res': 'pierce-cold.max',
                'Cold Skill Damage': 'extra-cold.max',
                'Faster Cast Rate': 'cast3.max',
                'AllSkills': 'allskills.max',
                'Cold Skill': 'coldskill.max',
                'Sorceress Skill': 'sor.max',
                'Magic Find': 'mag%.max',                
                'Magic Find/Level': 'mag%/lvl.parm',
                'AR.min': 'res-all.min',
                'AR.max': 'res-all.max',
            }
        },
        {
            'enable': False,
            'export_name': 'Crushing Blow & Open Wounds Items',
            'check_conditions': {
                'logic': 'OR',
                'conditions': [
                    {"path": "crush.min", "operator": ">", "threshold": 10},
                    {"path": "dmg.max", "operator": ">", "threshold": 30},
                    {"path": "hit-skill.parm", "operator": "==", "threshold": 'Life Tap'},
                    {
                        'logic': 'AND',
                        'conditions': [
                            {"path": "openwounds.min", "operator": ">", "threshold": 10},
                        ]
                    },
                    {"path": "oskill.parm", "operator": "==", "threshold": 'Teleport'}
                ]
            },

            'export_mapping': {
                'Name': 'Name',
                'isOriginal': 'isOriginal',
                'Source': 'source',
                'MainType': 'MainType',
                'Type': 'Type',
                'BaseItem': 'BaseItem',
                'Lvl.Req': 'Lvl.Req',
                'openwounds': 'openwounds.min',
                'crushing blow': 'crush.min',
                '+ damage': 'dmg.max',
                'location': 'BodyLoc1',
                'Chance of Block': 'block.min',
                'Faster Block': 'block2.min',
                'hit-skill': 'hit-skill.parm',
                'oskill': 'oskill.parm',
                'DTM': 'dmg-to-mana.min',
                'AR.min': 'res-all.min',
                'AR.max': 'res-all.max',
                'CanNotFrozen': 'nofreeze.min',
            }
        },
    ]

    def __init__(self, options):
        BaseJob.__init__(self, options)

        yaml_path = os.path.join(os.path.dirname(__file__), 'D2rrConfig.yaml')

        with open(yaml_path, 'r', encoding='utf-8') as f:
            self.d2r_config = yaml.load(f, yaml.FullLoader)

        self.excel_path = os.path.join(self.d2r_config['mod_d2rr_root'], self.excel_relative_path)
        self.work_path = self.get_options('work_path')
        self.debug_path = os.path.join(self.work_path, 'debug_export')
        if os.path.exists(self.debug_path):
            shutil.rmtree(self.debug_path)
        os.makedirs(self.debug_path)


    def run(self):
        self.logger.info('start')

        if not os.path.exists(self.excel_path):
            self.logger.error(f'Excel directory not found: {self.excel_path}')
            return
        
        item_detail_file_path = os.path.join(self.work_path, 'ItemDetails.xlsx')

        self.logger.info(f'Reading file: {item_detail_file_path}')
        
        items_df = pd.read_excel(item_detail_file_path, index_col=False)
        
        for config in self.config_list:
            # try:
            if config['enable'] == False:
                continue
            export_name = config['export_name']
            check_conditions = config['check_conditions']
            self.logger.info('Checking conditions: %s'%export_name)

            items_found = self.find_item_matches(items_df, check_conditions)
            items_found.to_excel(os.path.join(self.debug_path, f'items_found.xlsx'), index=False)
            self.export_to_excel(items_found, config['export_mapping'], output_file=os.path.join(self.work_path, f'{export_name}.xlsx'))
            # except Exception as e:
            #     # 处理主逻辑异常
            #     self.logger.error(f"错误: 应用条件时发生异常 - {str(e)}")


    def export_to_excel(self, dataframe, export_mapping, output_file='output.xlsx'):
        """
        根据指定的映射关系将DataFrame导出到Excel

        """

        # 创建空的DataFrame用于导出
        export_df = pd.DataFrame()
        
        # 根据映射关系填充导出DataFrame
        for excel_col, df_col in export_mapping.items():

            # 直接字段映射
            if df_col in dataframe.columns:
                export_df[excel_col] = dataframe[df_col]
        
        # 导出到Excel
        # export_df.to_excel(output_file, index=False)

        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            export_df.to_excel(writer, sheet_name='Sheet1', index=False)
            
            # 获取工作簿和工作表对象
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            
            # 获取数据的最大列索引和最大行索引
            max_col = export_df.shape[1]
            max_row = export_df.shape[0]
            
            # 添加筛选器，范围从 A1 到最后一列最后一行
            worksheet.auto_filter.ref = f'A1:{chr(64 + max_col)}{max_row + 1}'  # 列索引转字母
            # 自动调整列宽
            for column_cells in worksheet.columns:
                length = max(len(str(cell.value)) for cell in column_cells)
                adjusted_width = (length + 2) * 1.2  # 适当增加宽度
                column_letter = chr(64 + column_cells[0].column)  # 列索引转字母
                worksheet.column_dimensions[column_letter].width = min(adjusted_width, 50)  # 限制最大宽度

            # 设置自动换行和垂直对齐为居中
            for row in worksheet.iter_rows(min_row=1, max_row=worksheet.max_row, max_col=worksheet.max_column):
                for cell in row:
                    cell.alignment = Alignment(wrap_text=True, vertical='center')

            # 居中对齐所有单元格（包括表头）
            for row in worksheet.iter_rows(min_row=1, max_row=max_row + 1, min_col=1, max_col=max_col):
                for cell in row:
                    cell.font = Font(name='InconsolataLGC NF', size=12)  # 设置字体
                    cell.alignment = Alignment(horizontal='center', vertical='center')

        self.logger.info(f"数据已成功导出到 {output_file}")
        return export_df
    


    def find_item_matches(self, item_list, check_conditions):
        # 动态应用条件
        def apply_condition(df, condition):
            paths = condition["path"]
            op = condition["operator"]
            if "threshold" in condition:
                threshold = condition["threshold"]
            # threshold = condition["threshold"]

            # 初始化结果掩码
            result_mask = pd.Series([False] * len(df))

            if isinstance(paths, str):
                paths = [paths]

            for path in paths:
                if path not in df.columns:
                    raise ValueError(f"列不存在: {path}")
                
                # 特殊处理：判断空值（NaN）
                if op == "isnull":
                    result_mask |= df[path].isna()
                    continue  # 跳过后续逻辑
                elif op == "notnull":
                    result_mask |= df[path].notna()
                    continue  # 跳过后续逻辑
                elif op == "in":
                    result_mask |= df[path].isin(threshold)
                    continue
                
                series = df[path]
            
                if op == ">":
                    current_mask = series > threshold
                elif op == "<":
                    current_mask = series < threshold
                elif op == ">=":
                    current_mask = series >= threshold
                elif op == "<=":
                    current_mask = series <= threshold
                elif op == "==":
                    current_mask = (series == threshold) | (series == threshold.lower())
                elif op == "!=":
                    current_mask = series != threshold
                else:
                    raise ValueError(f"Unsupported operator: {op}")
                
                # 更新结果掩码（任意列满足条件即可）
                result_mask |= current_mask

            return result_mask

        def apply_conditions(df, config):
            if "logic" in config:
                logic = config["logic"].upper()
                sub_masks = [apply_conditions(df, cond) for cond in config["conditions"]]
                
                if logic == "AND":
                    return pd.Series([all(m) for m in zip(*sub_masks)], index=df.index)
                elif logic == "OR":
                    return pd.Series([any(m) for m in zip(*sub_masks)], index=df.index)
                else:
                    raise ValueError(f"Unsupported logic: {logic}")
            else:
                return apply_condition(df, config)

        mask = apply_conditions(item_list, check_conditions)
        result = item_list[mask]
        return result


def read_file_to_dataframe(file_path):
    try:
        # 根据文件扩展名选择读取方法
        if file_path.endswith('.txt'):
            df = pd.read_csv(file_path, sep='\t')
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            print(f"不支持的文件格式: {file_path}")
            
    except Exception as e:
        print(f"读取映射表 {file_path} 时出错: {e}")

    return df