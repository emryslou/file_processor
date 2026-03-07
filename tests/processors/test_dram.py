import pandas as dram_pd
from unittest.mock import patch

from file_processor.processors import dram
from . import fixture_processor, pytest, Path, convert_subtitle_id_to_binstr


@pytest.fixture(scope="function")
def fixture_dram(fixture_processor, test_file, output_dir):
    """
    为DRAM T7代码测试提供 fixture
    """
    
    # 构建测试数据
    import shutil
    root_data_path = fixture_processor["root_data_path"]
    source_file: Path = Path(root_data_path) / test_file
    input_file: Path = root_data_path / "test" / "input" / "dram" / source_file.name
    output_dir: Path = root_data_path / "test" / "output" / "dram" / output_dir
    input_file.parent.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(source_file, input_file)

    yield {
        "input_file": input_file,
        "output_dir": output_dir,
    }

    # 测试结束后清理
    for t7_file in output_dir.glob("*"):
        t7_file.unlink()
    output_dir.rmdir()
    for input_file in input_file.parent.glob("*"):
        input_file.unlink()
    input_file.parent.rmdir()

@pytest.mark.parametrize("test_file, output_dir", [
    ("dram/bak/t7_code.xlsx", "T7Code/"),
])
def test_dram_t7_code(fixture_dram):
    """
    测试DRAM T7代码函数
    """
    assert Path(fixture_dram["input_file"]).exists(), "输入文件应该存在的"
    output_file = dram.proc_t7_code_file(**fixture_dram)
    assert output_file.exists(), f"找不到输出文件: {output_file}"
    assert output_file.stat().st_size > 0, "输出文件应该有内容"
    assert output_file.name.startswith("T7Code_"), "输出文件应该以'T7Code_'开头"
    assert output_file.name.endswith(".xls"), "输出文件应该是Excel文件"
    # 检查输出文件的内容是否为老版Excel格式
    import xlrd
    with xlrd.open_workbook(output_file) as workbook:
        assert "Sheet1" in workbook.sheet_names(), "输出文件应该包含'Sheet1'工作表"
        sheet = workbook.sheet_by_name("Sheet1")
        assert sheet.nrows > 0, "输出文件的'Sheet1'工作表应该有数据行"
        assert sheet.ncols == 3, "输出文件的'Sheet1'工作表应该有3个数据列"
        columns = sheet.row_values(0)
        assert columns == ["LOT ID", "T7CODE", "WAFERID"], "输出文件的'Sheet1'工作表第一行应该是 ['LOT ID', 'T7CODE', 'WAFERID']"
        # 检查数据行是否符合预期
        for row_index in range(1, sheet.nrows):
            row_values = sheet.row_values(row_index)
            assert len(row_values) == 3, f"输出文件的'Sheet1'工作表第{row_index+1}行应该有3个数据列"


@pytest.mark.parametrize("test_file, output_dir", [
    ("dram/bak/COA_data - BPFQ40010H.xlsx", "COA/"),
])
def test_dram_coa(fixture_dram):
    """
    测试DRAM COA函数
    """
    assert Path(fixture_dram["input_file"]).exists(), "输入文件应该存在的"
    output_file = dram.proc_coa_file(**fixture_dram)
    assert output_file.exists(), f"找不到输出文件: {output_file}"
    assert output_file.stat().st_size > 0, "输出文件应该有内容"
    assert output_file.name.startswith("COA_"), "输出文件应该以'COA_'开头"
    assert output_file.name.endswith(".csv"), "输出文件应该是CSV文件"
    # 检查输出文件的内容是否符合预期
    import re
    df = dram_pd.read_csv(output_file, header=None)
    assert df.iloc[0, 0] == 'Date:', "输出文件的第一行第一列应该是 'Date:', 但实际为 '{}'".format(df.iloc[0, 0])
    assert re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', df.iloc[0, 1]), "输出文件的第一行第二列应该是日期格式，如 '2023-01-01 12:00:00'"
    assert df.iloc[2, 0] == 'Lot ID:', "输出文件的第一行第三列应该是 'Lot ID:', 但实际为 '{}'".format(df.iloc[0, 2])
    assert df.iloc[3,:].isnull().all(), "输出文件的第一行第四列应该为空"
    assert df.iloc[4, 0] == 'Wafer ID', "输出文件的第一行第五列应该是 'Wafer ID', 但实际为 '{}'".format(df.iloc[4, 0])
    assert df.iloc[4, 1] == 'T7Code', "输出文件的第一行第六列应该是 'T7Code', 但实际为 '{}'".format(df.iloc[4, 1])
    for row_index, wafer_id in enumerate(df.iloc[5:-3, 0].tolist()):
        assert re.match(r'^[A-Z0-9]+_[\d]{2}$', wafer_id), f"输出文件的第{row_index+5}行第五列应该是 Wafer ID 格式，如 'BPFQ40010H_01'，但实际为 '{wafer_id}'"
    
    assert df.iloc[-2:, 0].tolist() == ['Spec USL', 'Spec LSL'], "输出文件的第10行第一列应该是 'Spec USL', 第11行第一列应该是 'Spec LSL', 但实际为 '{}'".format(df.iloc[-2:, 0].tolist())


@pytest.fixture(scope="function", autouse=True)
def fixture_apc_data_columns(request):
    return {
        'input_columns': [
            'REPLY_DTTS','交货批次号','LOT_ID','PRODUCT_ID','LAYER_ID','MACHINE_TYPE','EQUIPMENT_ID',
            'RETICLE','SUBSTRATE_ID','TRANS_X(nm)','TRANS_Y(nm)','EXP_X(ppm)','EXP_Y(ppm)', 'NON_ORTHO(urad)',
            'ROTATION(urad)','SHOT_ROT(urad)','SHOT_MAG(ppm)', 'ASYM_ROT(urad)','ASYM_MAG(ppm)','CPE_ID',
        ],
        'output_columns': [
            'REPLY_DTTS','LOT_ID','PRODUCT_ID','LAYER_ID','MACHINE_TYPE','EQUIPMENT_ID', 'RETICLE',
            'SUBSTRATE_ID','TRANS_X(nm)','TRANS_Y(nm)','EXP_X(ppm)','EXP_Y(ppm)', 'NON_ORTHO(urad)',
            'ROTATION(urad)','SHOT_ROT(urad)','SHOT_MAG(ppm)', 'ASYM_ROT(urad)','ASYM_MAG(ppm)','CPE_ID',
        ],
    }


@pytest.mark.parametrize("test_file, output_dir", [
    ("dram/bak/APC_dram.xlsx", "APC/"),
])
def test_dram_apc(fixture_dram, fixture_apc_data_columns):
    """
    测试DRAM APC函数
    """
    assert Path(fixture_dram["input_file"]).exists(), "输入文件应该存在的"
    output_file = dram.proc_apc_file(**fixture_dram)
    assert output_file.exists(), f"找不到输出文件: {output_file}"
    assert output_file.stat().st_size > 0, "输出文件应该有内容"
    assert output_file.name.startswith("APC_"), "输出文件应该以'APC_'开头"
    assert output_file.name.endswith(".xlsx"), "输出文件应该是Excel文件"
    # 检查输出文件的内容是否符合预期
    output_df = dram_pd.read_excel(output_file)
    assert output_df.columns.tolist() == fixture_apc_data_columns["output_columns"], "输出文件的列名应该是 '{}', 实际: {}".format(",".join(fixture_apc_data_columns["output_columns"]), str(output_df.columns.tolist()))


@pytest.mark.parametrize("test_file, output_dir", [
    ("dram/bak/APC_dram.xlsx", "APC/"),
])
def test_dram_apc_data(fixture_dram, fixture_apc_data_columns):
    """
    测试DRAM APC数据函数
    """
    assert Path(fixture_dram["input_file"]).exists(), "输入文件应该存在的"
    
    # case 1: 只有一行数据
    output_file = None
    with patch("file_processor.processors.dram.pd.read_excel") as mock_read_excel:
        mock_read_excel.return_value = dram_pd.DataFrame(data=[
            [
                '	2025-08-29 09:56:10', 'BGGT332600','BP5044000','CWJGAN1.00','M4B','ASML',
                'LKFACB02','CWJGAM4BAAH1','BP5044000_01','2.088','-6.442','0.226','0.256',
                '-0.036','-0.097','-0.23','-0.007','0.052','-0.234','-'
            ]
        ], columns=fixture_apc_data_columns["input_columns"])
        output_file = dram.proc_apc_file(**fixture_dram)
    if output_file is None:
        pytest.fail("输出文件应该被创建")
    assert output_file.exists(), f"找不到输出文件: {output_file}"
    assert output_file.stat().st_size > 0, "输出文件应该有内容"
    assert output_file.name.startswith("APC_"), "输出文件应该以'APC_'开头"
    assert output_file.name.endswith(".xlsx"), "输出文件应该是Excel文件"
    # 检查输出文件的内容是否符合预期
    output_df = dram_pd.read_excel(output_file)
    assert output_df.columns.tolist() == fixture_apc_data_columns["output_columns"], "输出文件的列名\n应该是: '{}'\n实际为: '{}'".format(",".join(fixture_apc_data_columns["output_columns"]), ','.join(output_df.columns.tolist()))
    assert output_df.iloc[:, 0].tolist() == ['2025/8/29 9:56'], "输出文件的第一列第一行应该是 '2025/8/29 9:56', 但实际为 '{}'".format(output_df.iloc[:, 0].tolist()[0])
    assert output_df.iloc[:, 1].tolist() == ['BGGT332600'], "输出文件的第二列第一行应该是 'BGGT332600', 但实际为 '{}'".format(output_df.iloc[:, 1].tolist()[0])
    assert output_df.iloc[:, 7].tolist() == ['1' + '0' * 24], "输出文件的第八列第一行应该是 {}, 但实际为 '{}'".format('1' + '0' * 24, output_df.iloc[:, 7].tolist()[0])
    assert len(output_df.iloc[:, 0].tolist()) == 1, "输出文件的第一列应该只有 1 行数据"

    # case 2: 有多行数据, 第 5 列一致
    output_file = None
    with patch("file_processor.processors.dram.pd.read_excel") as mock_read_excel:
        mock_read_excel.return_value = dram_pd.DataFrame(data=[
            [
                '	2025-08-29 09:56:10', 'BGGT332600','BP5044000','CWJGAN1.00','M4B','ASML',
                'LKFACB02','CWJGAM4BAAH1','BP5044000_01','2.088','-6.442','0.226','0.256',
                '-0.036','-0.097','-0.23','-0.007','0.052','-0.234','-'
            ],
            [
                '	2025-08-29 09:56:10', 'BGGT332600','BP5044000','CWJGAN1.00','M4B','ASML',
                'LKFACB02','CWJGAM4BAAH1','BP5044000_02','2.088','-6.442','0.226','0.256',
                '-0.036','-0.097','-0.23','-0.007','0.052','-0.234','-'
            ]
        ], columns=fixture_apc_data_columns["input_columns"])
        output_file = dram.proc_apc_file(**fixture_dram)
    if output_file is None:
        pytest.fail("输出文件应该被创建")
    assert output_file.exists(), f"找不到输出文件: {output_file}"
    assert output_file.stat().st_size > 0, "输出文件应该有内容"
    assert output_file.name.startswith("APC_"), "输出文件应该以'APC_'开头"
    assert output_file.name.endswith(".xlsx"), "输出文件应该是Excel文件"
    # 检查输出文件的内容是否符合预期
    output_df = dram_pd.read_excel(output_file)
    assert output_df.columns.tolist() == fixture_apc_data_columns["output_columns"], "输出文件的列名\n应该是: '{}'\n实际为: '{}'".format(",".join(fixture_apc_data_columns["output_columns"]), ','.join(output_df.columns.tolist()))
    assert output_df.iloc[:, 0].tolist() == ['2025/8/29 9:56'], "输出文件的第一列第一行应该是 '2025/8/29 9:56', 但实际为 '{}'".format(output_df.iloc[:, 0].tolist()[0])
    assert output_df.iloc[:, 1].tolist() == ['BGGT332600'], "输出文件的第二列第一行应该是 'BGGT332600', 但实际为 '{}'".format(output_df.iloc[:, 1].tolist()[0])
    assert output_df.iloc[:, 7].tolist() == [convert_subtitle_id_to_binstr(['BP5044000_01', 'BP5044000_02'])], "输出文件的第八列第一行应该是 {}, 但实际为 '{}'".format(convert_subtitle_id_to_binstr(['BP5044000_01', 'BP5044000_02']), output_df.iloc[:, 7].tolist()[0])
    assert len(output_df.iloc[:, 0].tolist()) == 1, "输出文件的第一列应该只有 1 行数据"

    # case 3: 有多行数据, 第 5 列不一致
    output_file = None
    with patch("file_processor.processors.dram.pd.read_excel") as mock_read_excel:
        mock_read_excel.return_value = dram_pd.DataFrame(data=[
            [
                '	2025-08-29 09:56:10', 'BGGT332600','BP5044000','CWJGAN1.00','M4B','ASML',
                'LKFACB02','CWJGAM4BAAH1','BP5044000_01','2.088','-6.442','0.226','0.256',
                '-0.036','-0.097','-0.23','-0.007','0.052','-0.234','-'
            ],
            [
                '	2025-08-29 09:56:10', 'BGGT332600','BP5044000','CWJGAN1.00','TB1','ASML',
                'LKFACB02','CWJGAM4BAAH1','BP5044000_02','2.088','-6.442','0.226','0.256',
                '-0.036','-0.097','-0.23','-0.007','0.052','-0.234','-'
            ]
        ], columns=fixture_apc_data_columns["input_columns"])
        output_file = dram.proc_apc_file(**fixture_dram)
    if output_file is None:
        pytest.fail("输出文件应该被创建")
    assert output_file.exists(), f"找不到输出文件: {output_file}"
    assert output_file.stat().st_size > 0, "输出文件应该有内容"
    assert output_file.name.startswith("APC_"), "输出文件应该以'APC_'开头"
    assert output_file.name.endswith(".xlsx"), "输出文件应该是Excel文件"
    # 检查输出文件的内容是否符合预期
    output_df = dram_pd.read_excel(output_file)
    assert output_df.columns.tolist() == fixture_apc_data_columns["output_columns"], "输出文件的列名\n应该是: '{}'\n实际为: '{}'".format(",".join(fixture_apc_data_columns["output_columns"]), ','.join(output_df.columns.tolist()))
    assert output_df.iloc[:, 0].tolist() == ['2025/8/29 9:56'] * 2, "输出文件的第一列第一行应该是 '2025/8/29 9:56', 但实际为 '{}'".format(output_df.iloc[:, 0].tolist())
    assert output_df.iloc[:, 1].tolist() == ['BGGT332600'] * 2, "输出文件的第二列第一行应该是 'BGGT332600', 但实际为 '{}'".format(output_df.iloc[:, 1].tolist())
    assert output_df.iloc[:, 7].tolist() == ['1' + '0' * 24, '01' + '0' * 23], "输出文件的第八列第一行应该是 {}, 但实际为 '{}'".format(['1' + '0' * 24, '01' + '0' * 23], output_df.iloc[:, 7].tolist())
    assert len(output_df.iloc[:, 0].tolist()) == 2, "输出文件的第一列应该只有 2 行数据"

    # case 3: 有多行数据, 第 5 列一致, 第 9 列不一样
    output_file = None
    with patch("file_processor.processors.dram.pd.read_excel") as mock_read_excel:
        mock_read_excel.return_value = dram_pd.DataFrame(data=[
            [
                '	2025-08-29 09:56:10', 'BGGT332600','BP5044000','CWJGAN1.00','M4B','ASML',
                'LKFACB02','CWJGAM4BAAH1','BP5044000_01','2.088','-6.442','0.226','0.256',
                '-0.036','-0.097','-0.23','-0.007','0.052','-0.234','-'
            ],
            [
                '	2025-08-29 09:56:10', 'BGGT332600','BP5044000','CWJGAN1.00','M4B','ASML',
                'LKFACB02','CWJGAM4BAAH1','BP5044000_02','2.089','-6.442','0.226','0.256',
                '-0.036','-0.097','-0.23','-0.007','0.052','-0.234','-'
            ]
        ], columns=fixture_apc_data_columns["input_columns"])
        with pytest.raises(ValueError, match="不同，无法构建二进制表示"):
            dram.proc_apc_file(**fixture_dram)
    

    # case 4: 有多行数据, 第 5 列一致, 第 9 列不一样
    output_file = None
    with patch("file_processor.processors.dram.pd.read_excel") as mock_read_excel:
        mock_read_excel.return_value = dram_pd.DataFrame(data=[
            [
                '	2025-08-29 09:56', 'BGGT332600','BP5044000','CWJGAN1.00','M4B','ASML',
                'LKFACB02','CWJGAM4BAAH1','BP5044000_01','2.088','-6.442','0.226','0.256',
                '-0.036','-0.097','-0.23','-0.007','0.052','-0.234','-'
            ]
        ], columns=fixture_apc_data_columns["input_columns"])
        dram.proc_apc_file(**fixture_dram)
