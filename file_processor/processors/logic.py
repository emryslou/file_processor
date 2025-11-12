from pathlib import Path
import pandas as pd
from datetime import datetime

from file_processor.stores import create_store
from file_processor.utils.logger import logger

def proc_t7_code_file(input_file: str|Path, output_dir: str|Path) -> Path:
    """ 处理 Logic T7Code 文件"""
    """ 处理过程：
        1. 输入 csv 文件转换为 xls 表格，
        2. xls 表格重命名为 T7COde_{lot_id}.xls
        2. 列：LOT NAME 改为 LOT ID
    Args:
        input_file (str): 要处理的 csv 文件路径
        output_dir (str): 输出目录路径
    """

    try:
        logger.info("T7Code 文件开始转换 ...")
        
        # 读取 csv 文件
        df = pd.read_excel(input_file)
        
        # 提取 lot_id
        lot_id = df['LOT NAME'].iloc[0]
        
        # 重命名列
        df.rename(columns={'LOT NAME': 'LOT ID'}, inplace=True)
        
        # 保存为 xls 文件
        output_file = Path(output_dir) / f"T7Code_{lot_id}.xls"
        df.to_excel(output_file, index=False)
        
        logger.info(f"T7Code 文件转换完成, 源文件: {input_file}, 处理后的文件: {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"T7Code 文件转换失败：{e}")

def proc_coa_file(input_file: str|Path, output_dir: str|Path) -> Path:
    """ 处理 Logic COA 文件转换"""
    """ 处理过程：
        1. 输入 csv 存储为 新的 csv 文件，
        2. 新 CSV 文件名为：COA_{lot_id}.csv
        3. lot_id 为 源文件 B 列第三行
        4. 新文件中：
            第1行第1列: 'Date:'
            第1行第2列: 当前日期加时间，格式为：yyyy/mm/dd hh:mm
            第2行第1列: 'Customer ID:'
            第2行第2列: 空字符串
            第2行第3列: 'Product ID:'
            第2行第4列: '0CSN'
            第2行第5列: 'Lot Pass/Fail:'
            第2行第6列: 'Pass'
            第3行第1列: 'Lot ID:'
            第3行第2列: lot_id
            第3行第3列: 'Wafer Qty:'
            第3行第4列: 源文件除第一行之外的数据的行数
            第3行第5列: 'Lot Type:'
            第3行第6列: 'PROD'
            第4行: 空
            第5行: Wafer ID,T7Code,BOW_X_UM,Pass/Fail,BOW_Y_UM,Pass/Fail,BOW_XY_UM,Pass/Fail,TTV_THK_RNG_A,Pass/Fail,SI_THK_UM,Pass/Fail,MAC_FS_DDP,Pass/Fail,VI Pass/Fail,Final Pass/Fail
            第6行第1列: 源文件的第3列,
            第6行第2列: 源文件的第2列,
            第6行剩余列：值均为 'Pass'
            第7行第1列：'Spec USL'
            第8行第1列：'Spec LSL'


    Args:
        input_file (str): 要处理的 csv 文件路径
        output_dir (str): 输出目录路径
    """
    try:
        logger.info("Logic COA 文件开始转换 ...")
        
        # 读取 csv 文件
        old_df = pd.read_excel(input_file)
        
        # 提取 lot_id
        lot_id = old_df.iloc[1, 0]
        
        rows = old_df.shape[0] + 7
        # 创建一个指定数据类型为 object 的 DataFrame，以避免类型不匹配警告
        new_df = pd.DataFrame(index=range(rows), columns=range(16), dtype=object)

        # 第1行第1列: 'Date:'
        # 第1行第2列: 当前日期加时间，格式为：yyyy/mm/dd hh:mm
        new_df.iloc[0, 0] = 'Date:'
        new_df.iloc[0, 1] = pd.Timestamp.now().strftime('%Y/%m/%d %H:%M')
        
        # 第2行第1列: 'Customer ID:'
        new_df.iloc[1, 0] = 'Customer ID:'
        new_df.iloc[1, 1] = ''
        
        # 第2行第3列: 'Product ID:'
        new_df.iloc[1, 2] = 'Product ID:'
        new_df.iloc[1, 3] = '0CSN'
        
        # 第2行第5列: 'Lot Pass/Fail:'
        new_df.iloc[1, 4] = 'Lot Pass/Fail:'
        new_df.iloc[1, 5] = 'Pass'


        # 第3行第1列: 'Lot ID:'
        new_df.iloc[2, 0] = 'Lot ID:'
        new_df.iloc[2, 1] = lot_id
        
        # 第3行第3列: 'Wafer Qty:'
        new_df.iloc[2, 2] = 'Wafer Qty:'
        new_df.iloc[2, 3] = old_df.shape[0]
        
        # 第3行第5列: 'Lot Type:'
        new_df.iloc[2, 4] = 'Lot Type:'
        new_df.iloc[2, 5] = 'PROD'

        new_df.iloc[3, 0:] = ''

        new_df.iloc[4, 0] = 'Wafer ID'
        new_df.iloc[4, 1] = 'T7Code'
        new_df.iloc[4, 2] = 'BOW_X_UM'
        new_df.iloc[4, 3] = 'Pass/Fail'
        new_df.iloc[4, 4] = 'BOW_Y_UM'
        new_df.iloc[4, 5] = 'Pass/Fail'
        new_df.iloc[4, 6] = 'BOW_XY_UM'
        new_df.iloc[4, 7] = 'Pass/Fail'
        new_df.iloc[4, 8] = 'TTV_THK_RNG_A'
        new_df.iloc[4, 9] = 'Pass/Fail'
        new_df.iloc[4, 10] = 'SI_THK_UM'
        new_df.iloc[4, 11] = 'Pass/Fail'
        new_df.iloc[4, 12] = 'MAC_FS_DDP'
        new_df.iloc[4, 13] = 'Pass/Fail'
        new_df.iloc[4, 14] = 'VI Pass/Fail'
        new_df.iloc[4, 15] = 'Final Pass/Fail'

        row_number = 5
        for i in range(old_df.shape[0]):
            # # 第5行第1列: 源文件的第3列,
            # Fix Issue: Fix: logic的COA文件中的wafer ID，需要的格式是KPB425_02，不是KPB425#02, 即替换 # 为 _
            new_df.iloc[row_number+i, 0] = str(old_df.iloc[i, 2]).replace('#', '_')
            # # 第5行第2列: 源文件的第2列,
            new_df.iloc[row_number+i, 1] = old_df.iloc[i, 1]
            # # 第5行剩余列：值均为 'Pass'
            new_df.iloc[row_number+i, [3,5,7,9,11,13,14,15]] = 'Pass'

        row_number += old_df.shape[0]
        # 第6行第1列：'Spec USL'
        new_df.iloc[row_number, 0] = 'Spec USL'
        # 第7行第1列：'Spec LSL'
        row_number += 1
        new_df.iloc[row_number, 0] = 'Spec LSL'


        output_file = Path(output_dir) / f"COA_{lot_id}.csv"
        # 添加 header=False 以避免输出数字列名
        new_df.to_csv(output_file, index=False, header=False)
        

        logger.info(f"Logic COA 文件转换完成, 源文件: {input_file}, 处理后的文件: {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Logic COA 文件转换失败：{e}")
        raise e

def proc_apc_file(input_file: str|Path, output_dir: str|Path) -> Path:
    """处理 Logic APC 文件的逻辑函数
    """
    """处理流程
    1. 新建 excel 文件，后缀为 .xlsx，文件名称: APC_{lot_id}.xlsx
    2. 新文件中数据处理逻辑如下:
        第 1 到 4 列: 源文件的第1到第4列
        5 列: 为固定值 'ASML'
        6 列: 依据源文件的第4列: 若等于 127 , 则为 'KPIKF01'; 若等于 286 , 则为 'KPIKF02'
        7 列: 依据源文件的第4列: 若等于 127 , 则为 '0CSN00127AA1'; 若等于 286 , 则为 '0CSN00286AA1'
        8 列: 获取第4列等于 127 或 286 的 源文件 F 列的所有值，做聚合，源数据格式为 'XXX_{n}', 其中 n 小于等于 25， 大于等于 1
            聚合后的数据格式为 25 位二进制字符，每个字符为 0 或 1，若源数据中包含 'XXX_n'，则第 n 位为 1，否则为 0
            例如: 若源数据中包含 'KPIKF01_1', 'KPIKF01_2', 'KPIKF01_3'，则 H 列的值为 '1110000000000000000000000'
        第 9 到 19 列: 源文件的第7到第17列
    """
    
    try:
        logger.info("Logic APC 文件开始转换 ...")
        
        old_df = pd.read_excel(input_file)

        lot_id = old_df.iloc[2, 1]
        new_columns = old_df.columns[0:4].tolist()
        new_columns.extend(['MACHINE_TYPE','EQUIPMENT_ID','RETICLE','SUBSTRATE_ID'])
        new_columns.extend(old_df.columns[6:17].to_list())

        new_df = pd.DataFrame(columns=new_columns, dtype=object)

        def match(value, mapping, default=None):
            return mapping.get(value, default)

        substrate_id_idx = new_columns.index('SUBSTRATE_ID')
        machine_type_idx = new_columns.index('MACHINE_TYPE')
        equipment_id_idx = new_columns.index('EQUIPMENT_ID')
        reply_dtts_idx = new_columns.index('REPLY_DTTS')
        reticle_idx = new_columns.index('RETICLE')
        for layer_id, items in old_df.groupby(old_df.columns[3], sort=False):
            new_row =  items.iloc[0].copy().reindex(new_columns)
            subtitle_id_bin = 0b0
            old_item = None
            for idx, item in enumerate(items[old_df.columns[5]]):
                if len(items) > 1:
                    if old_item is None:
                        old_item = items.iloc[idx, 6:].copy().fillna('')
                    elif not(old_item == items.iloc[idx, 6:].fillna('')).all():
                        logger.error(f"{layer_id} 的参数有差异不能合并")
                        logger.error(f"第 {idx+1} 行参数: {old_item.tolist()}")
                        logger.error(f"第 {idx+2} 行参数: {items.iloc[idx, 6:].tolist()}")
                        raise ValueError(f"{layer_id} 的参数有差异不能合并")
                logger.info(f"第 {idx+1} 行参数: {item}")
                subtitle_id_bin |= (1 << (24 - (int(str(item)[-2:]) - 1)))
            
            #  Fix: logic的APC文件，REPLY_DTTS对应的日期，要和Dram一样，是2025/9/29 03:43:00这种，不要自定义的2025-09-29 03:43:00 @dukang
            cell_0 = datetime.strptime(str(new_row.iloc[reply_dtts_idx]).strip(), "%Y-%m-%d %H:%M:%S")
            # Issue Fix: apc文件的第一列日期时间格式，要去掉秒， 不管dram还是logic @dukang
            new_row.iloc[reply_dtts_idx] = f"{cell_0.year}/{cell_0.month}/{cell_0.day} {cell_0.hour}:{cell_0.minute:02d}"
            
            new_row.iloc[substrate_id_idx] = format(subtitle_id_bin, '025b')
            new_row.iloc[machine_type_idx] = 'ASML'
            new_row.iloc[equipment_id_idx] = match(layer_id, {127: 'KPIKF01', 286: 'KPIKF02'})
            new_row.iloc[reticle_idx] = match(layer_id, {127: '0CSN00127AA1', 286: '0CSN00286AA1'})
            logger.debug(f"第 {idx+1} 行参数: {new_row.tolist()}, old_item: {items.iloc[:, 0].tolist()}")
            new_df.loc[len(new_df)] = new_row

        out_file = Path(output_dir) / f"APC_{lot_id}.xlsx"
        new_df.to_excel(out_file, index=False)

        logger.info(f"Logic APC 文件转换完成, 源文件: {input_file}, 处理后的文件: {out_file}")
        return out_file
    except Exception as e:
        logger.exception(f"Logic APC 文件转换失败：{e}")
        raise e
    