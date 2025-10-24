import pandas as pd
from pathlib import Path
from typing import Tuple

def read_file_by_type(file_path: str|Path, **kwargs) -> Tuple[pd.DataFrame, str]:
    """根据文件类型读取文件"""
    if str(file_path).endswith('.csv'):
        return pd.read_csv(file_path, **kwargs), 'csv'
    elif str(file_path).endswith('.xlsx') or str(file_path).endswith('.xls'):
        return pd.read_excel(file_path, **kwargs), 'excel'
    else:
        raise ValueError("不支持的文件类型")
