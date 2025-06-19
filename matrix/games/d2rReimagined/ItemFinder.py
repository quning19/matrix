#coding=utf-8

import os

import yaml
import pandas as pd
from matrix.base.BaseJob import BaseJob


class ItemFinder(BaseJob):

    excel_relative_path = 'data/global/excel/'
    work_path = None

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

    config_list = [
        {
            'file_name': 'uniqueitems.txt',
            'fields': {
                'Name' : 'index',
                'BaseItem': '*ItemName',
                'Lvl.Req': 'lvl req',
            },
            'prop_fields': {
                'prop_name' : 'prop',
                'param_name' : 'par',
                'min_value' : 'min',
                'max_value' : 'max',
            },
            'check_conditions': {
                'logic': 'OR',
                'conditions': [
                    {"path": "crush.min", "operator": ">", "threshold": 40},
                    {
                        'logic': 'AND',
                        'conditions': [
                            {"path": "crush.min", "operator": ">", "threshold": 0},
                            {"path": "openwounds.min", "operator": ">", "threshold": 20},
                        ]
                    }
                ]
            },

            'export_mapping': {
                'Name': 'Name',
                'Type': 'Type',
                'BaseItem': 'BaseItem',
                'Lvl.Req': 'Lvl.Req',
                'openwounds': 'openwounds.min',
                'crushing blow': 'crush.min',
            }
        },
    ]

    def __init__(self, options):
        BaseJob.__init__(self, options)

        yaml_path = os.path.join(os.path.dirname(__file__), 'D2rrConfig.yaml')

        with open(yaml_path, 'r', encoding='utf-8') as f:
            self.d2r_config = yaml.load(f, yaml.FullLoader)

        self.work_path = self.d2r_config['mod_d2rr_root']

    def run(self):
        self.logger.info('start')

        excel_dir = os.path.join(self.work_path, self.excel_relative_path)
        if not os.path.exists(excel_dir):
            self.logger.error(f'Excel directory not found: {excel_dir}')
            return
        
        self.read_type_files()
        
        for config in self.config_list:
            file_name = config['file_name']
            file_path = os.path.join(excel_dir, file_name)
            if not os.path.exists(file_path):
                self.logger.error(f'File not found: {file_path}')
                continue
            
            check_conditions = config['check_conditions']

            # 读取CSV文件并转换
            items_df = self.read_csv_file(file_path, config['fields'], config['prop_fields'])
            items_df = self.merge_base_item_info(items_df)

            items_found = self.find_item_matches(items_df, check_conditions)
            self.export_to_excel(items_found, config['export_mapping'], output_file=os.path.join(self.work_path, f'export_{file_name}.xlsx'))

    def merge_base_item_info(self, items_df):

        items_df['BaseItem_lower'] = items_df['BaseItem'].str.lower()

        print(items_df)

        # 合并到主DataFrame
        merged_df = items_df.merge(
            self.base_item_mappings,
            on='BaseItem_lower',
            how='left',
            suffixes=('', '_1')
        )
        print(merged_df)
        return merged_df
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
        export_df.to_excel(output_file, index=False)
        print(f"数据已成功导出到 {output_file}")
        return export_df
    

    def read_type_files(self):
        config = self.base_item_info
        all_mappings = pd.DataFrame(columns=[config['fields']['BaseItem'], config['fields']['Type']])
 
        # 读取并合并所有映射表
        for file_name in config['file_names']:
            file_path = os.path.join(self.work_path, self.excel_relative_path, file_name)
            try:
                # 根据文件扩展名选择读取方法
                if file_path.endswith('.txt'):
                    mapping_df = pd.read_csv(file_path, sep='\t')
                elif file_path.endswith(('.xlsx', '.xls')):
                    mapping_df = pd.read_excel(file_path)
                else:
                    print(f"不支持的文件格式: {file_path}")
                    continue
                    
                # 选择需要的列并添加到总映射
                name_col = config['fields']['BaseItem']
                type_col = config['fields']['Type']
                
                if name_col in mapping_df.columns and type_col in mapping_df.columns:
                    all_mappings = pd.concat([
                        all_mappings,
                        mapping_df[[name_col, type_col]]
                    ], ignore_index=True)
                else:
                    print(f"映射表 {file_path} 缺少必要的列: {name_col} 或 {type_col}")
            except Exception as e:
                print(f"读取映射表 {file_path} 时出错: {e}")
        
        # 去除重复项
        all_mappings = all_mappings.drop_duplicates(subset=[config['fields']['BaseItem']])

        self.base_item_mappings = all_mappings.rename(columns={
            config['fields']['BaseItem']: 'BaseItem',
            config['fields']['Type']: 'Type'
        })

        self.base_item_mappings['BaseItem_lower'] = self.base_item_mappings['BaseItem'].str.lower()

    def find_item_matches(self, item_list, check_conditions):
        # 动态应用条件
        def apply_condition(df, condition):
            path = condition["path"]
            op = condition["operator"]
            threshold = condition["threshold"]
            
            if op == ">":
                return df[path] > threshold
            elif op == "<":
                return df[path] < threshold
            elif op == ">=":
                return df[path] >= threshold
            elif op == "<=":
                return df[path] <= threshold
            elif op == "==":
                return df[path] == threshold
            elif op == "!=":
                return df[path] != threshold
            else:
                raise ValueError(f"Unsupported operator: {op}")

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


    def read_csv_file(self, item_file_path, fields, prop_fields):
        
        self.logger.info(f'Reading file: {item_file_path}')
            
        df = pd.read_csv(item_file_path, index_col=False, sep='\t')
        def transform_row(row):
            result = {}
            num_props = len([col for col in df.columns if col.startswith('prop')])

            for key, value in fields.items():
                v = row[value] if pd.notna(row[value]) else 0
                if isinstance(v, float):
                    v = int(v)
                result[key] = v

            for i in range(1, num_props + 1):
                prop = row[prop_fields['prop_name'] + f'{i}']
                par = row[prop_fields['param_name'] + f'{i}']
                min_val = row[prop_fields['min_value'] + f'{i}']
                max_val = row[prop_fields['max_value'] + f'{i}']
                
                # 添加 .min 和 .max 键值对
                result[f"{prop}.min"] = min_val
                result[f"{prop}.max"] = max_val
                result[f"{prop}.parm"] = par

            return pd.Series(result)

        transformed_df = df.apply(transform_row, axis=1)
        return transformed_df

