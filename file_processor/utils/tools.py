import pandas as pd
from pathlib import Path
from typing import Tuple

def read_file_by_type(file_path: str|Path, **kwargs: dict) -> Tuple[pd.DataFrame, str]:
    """根据文件类型读取文件"""
    if str(file_path).endswith('.csv'):
        return pd.read_csv(file_path, **kwargs), 'csv'
    elif str(file_path).endswith('.xlsx') or str(file_path).endswith('.xls'):
        return pd.read_excel(file_path, **kwargs), 'excel'
    else:
        raise ValueError("不支持的文件类型")


def human_readable_time(seconds: float) -> str:
    """将秒转换为人类可读的时间格式"""
    times = [
        ('年', 60 * 60 * 24 * 365 * 1000000),
        ('月', 60 * 60 * 24 * 30 * 1000000),
        ('天', 60 * 60 * 24 * 1000000),
        ('小时', 60 * 60 * 1000000),
        ('分钟', 60 * 1000000),
        ('秒', 1000000),
        ('毫秒', 1000),
        ('微秒', 1),
    ]
    seconds *= 1000000
    result = []
    for name, sec in times:
        second = int(seconds // sec)
        if second > 0:
            result.append(f"{second}{name}")
            seconds -= second * sec

    
    return ' '.join(result)