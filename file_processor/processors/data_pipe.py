import pandas as pd
from pathlib import Path
from enum import Enum

class ReadDataError(Exception):
    """读取数据异常"""
    pass

class WriteDataError(Exception):
    """写入数据异常"""
    pass


class DataFormat(Enum):
    """数据格式"""
    XLSX = 'xlsx'
    XLS = 'xls'
    CSV = 'csv'

    def match_file_format(file_path: str) -> 'DataFormat':
        """
        匹配文件格式

        :param file_path: 文件路径
        :return: 数据格式
        """
        return DataFormat(str(file_path).split('.')[-1])
    
    def get_file_extension(self) -> str:
        """
        获取文件扩展名

        :return: 文件扩展名
        """
        return self.value
    
    def get_all_file_extensions() -> list[str]:
        """
        获取所有文件扩展名

        :return: 文件扩展名列表
        """
        return [fmt.value for fmt in DataFormat]
    
    def is_supported(file_path: str) -> bool:
        """
        判断数据格式是否支持

        :return: 是否支持
        """
        return file_path.split('.')[-1] in DataFormat.get_all_file_extensions()


def read_pd_data_frame(file_path: str, /, **kwargs) -> pd.DataFrame:
    """
    从文件路径读取 pandas DataFrame

    :param file_path: 文件路径
    :return: pandas DataFrame
    """
    assert file_path is not None, "未指定文件路径"
    assert Path(file_path).exists(), f"文件路径 {file_path} 不存在"
    
    df = None
    match DataFormat.match_file_format(file_path):
        case DataFormat.XLSX:
            df = pd.read_excel(file_path, **kwargs)
        case DataFormat.XLS:
            from xlrd import open_workbook
            df = pd.read_excel(open_workbook(file_path), **kwargs)
        case DataFormat.CSV:
            df = pd.read_csv(file_path, **kwargs)
        case _:
            raise ReadDataError(f"不支持的文件格式 {file_path.split('.')[-1]}")

    return df

def write_pd_data_frame(df: pd.DataFrame, file_path: str, /, **kwargs):
    """
    将 pandas DataFrame 写入文件路径

    :param df: pandas DataFrame
    :param file_path: 文件路径
    """
    assert df is not None, "未指定 DataFrame"
    assert file_path is not None, "未指定文件路径"
    
    match DataFormat.match_file_format(file_path):
        case DataFormat.XLSX:
            df.to_excel(file_path, **kwargs)
        case DataFormat.XLS:
            from xlwt import Workbook
            wb = Workbook()
            ws = wb.add_sheet('Sheet1')
            # 写入表头
            for c, col in enumerate(df.columns):
                ws.write(0, c, col)
            # 写入数据
            for r, row in enumerate(df.values):
                for c, val in enumerate(row):
                    ws.write(r+1, c, val)
            wb.save(file_path)
        case DataFormat.CSV:
            df.to_csv(file_path, **kwargs)
        case _:
            raise WriteDataError(f"不支持的文件格式 {file_path.split('.')[-1]}")
