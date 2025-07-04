import pandas as pd

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

def get_excel_column_letter(column_index):
    """将列索引转换为Excel列字母表示（如1->A, 27->AA）"""
    letter = ''
    while column_index > 0:
        remainder = (column_index - 1) % 26
        letter = chr(65 + remainder) + letter
        column_index = (column_index - 1) // 26
    return letter

def remove_all_empty_columns(df):
    """
    删除DataFrame中所有值都是空值的列
    仅将NaN、None和空字符串视为空值，0和False不视为空值
    
    参数:
    df (pd.DataFrame): 输入的DataFrame
    
    返回:
    pd.DataFrame: 删除全空列后的DataFrame
    """
    # 自定义函数判断是否为空值（只考虑NaN、None和空字符串）
    def is_empty(value):
        return pd.isna(value) or value == ''
    
    # 检查每一列是否全部为空值
    is_empty_col = df.apply(lambda col: col.apply(is_empty).all())
    
    # 获取全部为空值的列名
    columns_to_drop = is_empty_col[is_empty_col].index.tolist()
    
    # 删除这些列
    if columns_to_drop:
        df = df.drop(columns=columns_to_drop)
        print(f"已删除 {len(columns_to_drop)} 个全部为空值的列.")
    else:
        print("没有发现全部为空值的列")
    
    return df