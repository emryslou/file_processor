from loguru import logger
from pathlib import Path
from ..stores import create_store
import pandas as pd
from datetime import datetime


def proc_t7_code_file(input_file: str|Path, output_dir: str|Path) -> Path:
    """处理 Dram T7Code 文件的逻辑函数
    """
    """处理流程
        1. 新建 excel 文件，后缀为 .xls，文件名称: T7Code_{lot_id}.xls
        2. 新文件内容如下:
            0. lot_id 列: 第三行第二列
            1. 表头为 'LOT ID', 'T7CODE', 'WAFERID'
            2. 从源文件第5行开始，逐行复制，知道第一列为的值为 Spec USL 为止
    """
    try:
        logger.info("Dram T7Code 文件开始转换 ...")
        
        # 指定header=None，避免将第一行作为表头
        # 指定dtype=str，保持所有数据的原始格式，避免自动格式化日期
        df = pd.read_excel(input_file, header=None, dtype=str) 
        lot_id = df.iloc[3, 1]
        
        # 从第5行开始，逐行复制，知道第一列为的值为 Spec USL 为止
        start_row = 5 # 因为第4行是表头，所以从第5行开始复制
        end_row = df.index[df.iloc[:, 0] == 'Spec USL'].tolist()[0]
        # 获取数据行数
        data_rows = df.iloc[start_row:end_row]
        num_rows = len(data_rows)
        
        # 创建正确行数的DataFrame
        new_df = pd.DataFrame(index=range(num_rows), columns=['LOT ID', 'T7CODE', 'WAFERID'], dtype=str)
        
        # 逐列赋值数据
        new_df['LOT ID'] = lot_id  # 标量值会自动广播到所有行
        new_df['T7CODE'] = data_rows.iloc[:, 1].values  # 使用.values确保正确复制值
        
        # 处理WAFERID：LOT ID + '#' + 复制的值的后两位
        wafer_ids = []
        for val in data_rows.iloc[:, 0]:
            # 获取值的后两位（如果长度小于2则全部使用）
            suffix = str(val)[-2:] if len(str(val)) >= 2 else str(val)
            wafer_id = f"{lot_id}#{suffix}"
            wafer_ids.append(wafer_id)
        new_df['WAFERID'] = wafer_ids
        

        output_file = Path(output_dir) / f"T7Code_{lot_id}.xls"
        match output_file.suffix:
            case ".xls":
                logger.warning(f"旧版的 Excel 格式不支持写入大文件, 尝试用 xlwt 库写入")
                # 写入 xls 文件，旧版本的 Excel 格式
                import xlwt
            
                # 创建一个 xlwt.Workbook 对象
                wb = xlwt.Workbook()
                ws = wb.add_sheet('Sheet1')
                
                # 写入列名
                for col_idx, col_name in enumerate(new_df.columns):
                    ws.write(0, col_idx, col_name)
                
                # 写入数据
                for row_idx, row in new_df.iterrows():
                    for col_idx, value in enumerate(row):
                        ws.write(row_idx + 1, col_idx, value)
                
                # 保存为真正的 xls 文件
                wb.save(output_file)
            case _:
                logger.warning(f"其他格式用 pandas 库写入, 尝试用 pandas 库写入 {output_file.suffix}")
                new_df.to_excel(output_file, index=False)

        # 添加header=False，避免输出表头行
        logger.info(f"Dram T7Code 文件转换完成, 源文件: {input_file}, 处理后的文件: {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Dram T7Code 文件转换失败：{e}")
        raise e

def proc_coa_file(input_file: str|Path, output_dir: str|Path) -> Path:
    """处理 Dram COA 文件的逻辑函数
    """
    """处理流程
        1. 新建 csv 文件，后缀为 .csv，文件名称: COA_{lot_id}.csv
        2. 新文件内容如下:
            0. lot_id 列: 第三行第二列
            1. 复制源文件内容
            2. 第4行内容清空
    """
    try:
        logger.info(f"Dram COA 文件开始转换, 源文件: {input_file}")
        
        # 指定header=None，避免将第一行作为表头
        # 指定dtype=str，保持所有数据的原始格式，避免自动格式化日期
        df = pd.read_excel(input_file, header=None, dtype=str) 
        lot_id = df.iloc[3, 1]

        new_df = df.copy()
        new_df.iloc[3, :] = ''
        new_df.iloc[2, 1] = lot_id
        
        """
        处理第一列数据，处理逻辑如下:
        1. 从 值为 'Wafer ID'的下一行开始处理，
        2. 处理方式: 将字符用 '_' 分割，然后第一个替换为 lot_id, 之后用 '_' 连接, 然后替换对应行
        3. 如果遇到包含空格或者空值的行，则停止处理
        """
        # 从 值为 'Wafer ID'的下一行开始处理
        start_row = df.index[df.iloc[:, 0] == 'Wafer ID'].tolist()[0] + 1
        for line in new_df.iloc[start_row:, 0]:
            if line == '' or ' ' in line:
                break
            line_parts = line.split('_')
            line_parts[0] = lot_id
            new_df.iloc[start_row, 0] = '_'.join(line_parts)
            start_row += 1
        
        output_file = Path(output_dir) / f"COA_{lot_id}.csv"
        # 添加header=False，避免输出表头行
        new_df.to_csv(output_file, index=False, header=False)
        logger.info(f"Dram COA 文件转换完成, 源文件: {input_file}, 处理后的文件: {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Dram COA 文件转换失败：{e}")
        raise e

def proc_apc_file(input_file: str|Path, output_dir: str|Path) -> Path:
    """处理 Dram APC 文件的逻辑函数
    """
    """处理流程
        1. 新建 excel 文件，后缀为 .xlsx，文件名称: APC_{lot_id}.xlsx
        2. 新文件内容如下:
            1. 第1列: 源文件的第1列，日期去除开头的空格字符
            2. 第2列: 源文件的第2列
            3. 第3到19列: 源文件的第4到第20列   
        4. 其中第 8 列数据，依据源文件的第5列对第9列数据做聚合，源数据格式为 'XXX{n}', 其中 n 小于等于 25， 大于等于 1，n表示为 01 到 25
            聚合后的数据格式为 25 位二进制字符，每个字符为 0 或 1，若源数据中包含 'XXX_n'，则第 n 位为 1，否则为 0
            例如: 若源数据中包含 'KPIKF01_1', 'KPIKF01_2', 'KPIKF01_3'，则 H 列的值为 '1110000000000000000000000'
    """

    try:
        logger.info(f"Dram APC 文件开始转换, 源文件: {input_file}")
        
        df = pd.read_excel(input_file)
        lot_id = df.iloc[0, 1]

        new_colums = [
            df.columns[0],
            df.columns[1], 
        ]
        new_colums.extend(df.columns[3:])

        new_df = pd.DataFrame(columns=new_colums, dtype=object)

        # 获取需要的列名，避免使用硬编码索引
        group_column = df.columns[4]  # 用于分组的列
        item_column = df.columns[8]   # 包含XXX{n}格式数据的列
        result_column_idx = 7         # 存储二进制结果的列索引

        for _key, items in df.groupby(group_column, sort=False):
            # 初始化二进制结果为25位0
            subtitle_id_bin = 0
            
            # 添加第一行数据作为基础，但只保留new_columns中定义的列
            # 先复制整行，然后只选择new_columns中存在的列
            temp_row = items.iloc[0].copy()
            # 使用reindex确保只包含new_columns中的列，并且顺序一致
            new_row = temp_row.reindex(new_colums)
            
            # 处理每个项目，构建二进制表示
            try:
                old_item = None
                key_item_size = len(items)
                for (idx, item) in enumerate(items[item_column]):
                    if key_item_size > 1:
                        if old_item is None:
                            old_item = items.iloc[idx, 9:].copy()
                        elif not (old_item == items.iloc[idx, 9:]).all():
                            raise ValueError(f"项目 '{items.iloc[idx, 9:].to_string()}' 与前一个项目 '{old_item.to_string()}' 不同，无法构建二进制表示")
                    # 提取数字部分并计算位位置
                    item_str = str(item)
                    if '_' in item_str:
                        idx = int(item_str.split('_')[-1])
                        # 验证索引范围 (1-25)
                        if 1 <= idx <= 25:
                            # 设置对应位为1 (注意：第n位对应24-(n-1)的偏移量)
                            subtitle_id_bin |= 1 << (24 - (idx - 1))
                        else:
                            raise ValueError(f"无效的索引 {idx}，必须在1-25之间, 对应数据: {item_column}: {item_str}")
            except (ValueError, IndexError) as e:
                logger.error(f"警告: 处理项目 '{items.iloc[idx, 9:]}' 时出错: {e}")
                raise
            
            # 将结果转换为25位二进制字符串（确保前导零）
            binary_result = format(subtitle_id_bin, '025b')
            # 去除日期字段开头的空格
            cell_0 = datetime.strptime(str(new_row.iloc[0]).strip(), "%Y-%m-%d %H:%M:%S")

            # Issue Fix: apc文件的第一列日期时间格式，要去掉秒， 不管dram还是logic @dukang
            new_row.iloc[0] = f"{cell_0.year}/{cell_0.month}/{cell_0.day} {cell_0.hour}:{cell_0.minute:02d}"


            # 设置二进制结果
            new_row.iloc[result_column_idx] = binary_result
            new_df = pd.concat([new_df, pd.DataFrame([new_row], dtype=object)], ignore_index=True)
            
        
        output_file = Path(output_dir) / f"APC_{lot_id}.xlsx"
        # 使用rename方法修改第二列的列名
        new_df = new_df.rename(columns={new_df.columns[1]: 'LOT_ID'})
        new_df.to_excel(output_file, index=False)
        logger.info(f"Dram APC 文件转换完成, 源文件: {input_file}, 处理后的文件: {output_file}")
        return output_file
    
    except Exception as e:
        logger.error(f"Dram APC 文件转换失败：{e}")
        raise e
