import pandas as logic_pd
from unittest.mock import patch

from file_processor.processors import logic
from . import fixture_processor, pytest, Path, convert_subtitle_id_to_binstr


@pytest.fixture(scope="function")
def fixture_logic(fixture_processor, test_file, output_dir):
    """
    为Logic T7代码测试提供 fixture  
    """
    
    # 构建测试数据
    import shutil
    root_data_path = fixture_processor["root_data_path"]
    source_file: Path = Path(root_data_path) / test_file
    input_file: Path = root_data_path / "test" / "input" / "logic" / source_file.name
    output_dir: Path = root_data_path / "test" / "output" / "logic" / output_dir
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

def _ouput_file_check(output_file: Path, file_name_prefix: str, file_name_suffix: str):
    """
    检查COA输出文件的内容是否符合预期
    """
    assert output_file.exists(), f"找不到输出文件: {output_file}"
    assert output_file.stat().st_size > 0, "输出文件应该有内容"
    assert output_file.name.startswith(file_name_prefix), f"输出文件应该以'{file_name_prefix}'开头"
    assert output_file.name.endswith(file_name_suffix), f"输出文件应该以'{file_name_suffix}'结尾"

@pytest.mark.parametrize("test_file, output_dir", [
    ("logic/bak/T7Code_logic.xlsx", "T7Code/"),
])
def test_logic_t7_code(fixture_logic):
    """
    测试Logic T7代码函数
    """
    assert Path(fixture_logic["input_file"]).exists(), "输入文件应该存在的"
    output_file = logic.proc_t7_code_file(**fixture_logic)
    _ouput_file_check(output_file, 'T7Code_', '.xls')

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


def _coa_output_data_valid(df: logic_pd.DataFrame):
    assert df.iloc[0, 0] == 'Date:', "输出文件的第一行第一列应该是 'Date:', 但实际为 '{}'".format(df.iloc[0, 0])
    assert df.fillna('').iloc[1, 0:6].tolist() == ['Customer ID:', '', 'Product ID:', '0CSN', 'Lot Pass/Fail:', 'Pass'], "第二行数据应该是 ['Customer ID:', '', 'Product ID:', '0CSN', 'Lot Pass/Fail:', 'Pass'], 但实际为 '{}'".format(df.iloc[1, :6].tolist())
    
    assert df.iloc[3, :].isnull().all(), "输出文件的第四行数据应该为空, 实际为: {}".format(df.iloc[3, :].tolist())
    assert df.iloc[4, :].tolist() == ['Wafer ID', 'T7Code', 'BOW_X_UM', 'Pass/Fail', 
                   'BOW_Y_UM', 'Pass/Fail', 'BOW_XY_UM', 'Pass/Fail',
                   'TTV_THK_RNG_A', 'Pass/Fail', 'SI_THK_UM', 'Pass/Fail',
                   'MAC_FS_DDP', 'Pass/Fail', 'VI Pass/Fail', 'Final Pass/Fail'], "第4行数据不匹配"
    assert df.iloc[-2:, 0].tolist() == ['Spec USL', 'Spec LSL'], "输出文件的第五行到倒数第二行数据应该为空, 实际为: {}".format(df.iloc[-2:, 0].tolist())

@pytest.mark.parametrize("test_file, output_dir", [
    ("logic/bak/COA-KPB425.xls", "COA/"),
])
def test_logic_coa(fixture_logic):
    """
    测试Logic COA函数
    """
    assert Path(fixture_logic["input_file"]).exists(), "输入文件应该存在的"
    output_file = logic.proc_coa_file(**fixture_logic)
    _ouput_file_check(output_file, 'COA_', '.csv')
    
    df = logic_pd.read_csv(output_file, header=None)
    _coa_output_data_valid(df)


@pytest.mark.parametrize("test_file, output_dir", [
    ("logic/bak/COA-KPB425.xls", "COA/"),
])
def test_logic_coa_data(fixture_logic):
    """
    测试Logic COA数据函数
    """
    import random
    assert Path(fixture_logic["input_file"]).exists(), "输入文件应该存在的"
    output_file = None
    mock_data = [
        ['KPB425','PWATU107MX', f'KPB425#{i:02d}']
        for i in range(random.randint(3, 10))
    ]
    with patch("file_processor.processors.logic.pd.read_excel") as mock_read_excel:
        mock_read_excel.return_value = logic_pd.DataFrame(data=mock_data, columns=['LOT NAME','T7CODE','WAFERID'])
        output_file = logic.proc_coa_file(**fixture_logic)
    if output_file is None:
        raise AssertionError("输出文件应该存在的")
    _ouput_file_check(output_file, 'COA_', '.csv')
    df = logic_pd.read_csv(output_file, header=None)
    _coa_output_data_valid(df)

    assert df.iloc[5:5+len(mock_data), :2].values.tolist() == [
        [wafer_id.replace('#', '_'), t7code] for _, t7code, wafer_id in mock_data
    ], "源数据验证失败"

    assert df.fillna('').iloc[5:5+len(mock_data), 3:].values.tolist() == [
        ['Pass', '', 'Pass', '', 'Pass', '', 'Pass', '', 'Pass', '', 'Pass', 'Pass', 'Pass']
    ] * len(mock_data), '固定数据验证失败'


@pytest.fixture(scope="function", autouse=True)
def fixture_apc_data_columns(request):
    return {
        'input_columns': [
            'REPLY_DTTS', 'LOT_ID','PRODUCT_ID','LAYER_ID','RETICLE_ID','WAFER_ID',
            'TRANS_X(nm)','TRANS_Y(nm)','EXP_X(ppm)','EXP_Y(ppm)','NON_ORTHO(urad)',
            'ROTATION(urad)','SHOT_ROT(urad)','SHOT_MAG(ppm)','ASYM_ROT(urad)','ASYM_MAG(ppm)','CPE_ID',
        ],
        'output_columns': [
            'REPLY_DTTS','LOT_ID','PRODUCT_ID','LAYER_ID','MACHINE_TYPE','EQUIPMENT_ID','RETICLE',
            'SUBSTRATE_ID','TRANS_X(nm)','TRANS_Y(nm)','EXP_X(ppm)','EXP_Y(ppm)','NON_ORTHO(urad)',
            'ROTATION(urad)','SHOT_ROT(urad)','SHOT_MAG(ppm)','ASYM_ROT(urad)','ASYM_MAG(ppm)','CPE_ID'
        ],
    }


def _test_apc_columns(columns, fixture_apc_data_columns):
    assert columns == fixture_apc_data_columns["output_columns"], "输出文件的列名\n应该是: '{}'\n实际为: '{}'".format(",".join(fixture_apc_data_columns["input_columns"]), ','.join(columns))


@pytest.mark.parametrize("test_file, output_dir", [
    ("logic/bak/0CSN-286-TTM2-APC-KPB425&KLE231.xlsx", "APC/"),
])
def test_logic_apc_columns(fixture_logic, fixture_apc_data_columns):
    """
    测试DRAM APC函数
    """
    assert Path(fixture_logic["input_file"]).exists(), "输入文件应该存在的"
    output_file = logic.proc_apc_file(**fixture_logic)
    _ouput_file_check(output_file, 'APC_', '.xlsx')
    # 检查输出文件的内容是否符合预期
    output_df = logic_pd.read_excel(output_file)
    _test_apc_columns(output_df.columns.tolist(), fixture_apc_data_columns)


@pytest.mark.parametrize("test_file, output_dir", [
    ("logic/bak/0CSN-286-TTM2-APC-KPB425&KLE231.xlsx", "apc/"),
])
def test_logic_apc_data(fixture_logic, fixture_apc_data_columns):
    """
    测试Logic APC数据函数
    """
    assert Path(fixture_logic["input_file"]).exists(), "输入文件应该存在的"
    
    # case 1: 空数据
    output_file = None
    with patch("file_processor.processors.logic.pd.read_excel") as mock_read_excel:
        mock_read_excel.return_value = logic_pd.DataFrame(data=[], columns=fixture_apc_data_columns["input_columns"])
        with pytest.raises(AssertionError, match="Logic APC 数据为空"):
            logic.proc_apc_file(**fixture_logic)
    
    # case 2: 1 条数据
    output_file = None
    with patch("file_processor.processors.logic.pd.read_excel") as mock_read_excel:
        mock_read_excel.return_value = logic_pd.DataFrame(data=[
            [
                '2025-9-29 3:43:00','KLE231','0CSN','286','0CSN00286AA1','21','0.236384229','12.64316584','0.016574739',
                '0.016894928','0.057643334','-0.018472039','-0.096117685','-0.536043252','0.007014191','-0.287610648','NA'
            ],
        ], columns=fixture_apc_data_columns["input_columns"])
        output_file =   logic.proc_apc_file(**fixture_logic)
    if output_file is None:
        pytest.fail("输出文件应该被创建")
    _ouput_file_check(output_file, 'APC_', '.xlsx')
    # 检查输出文件的内容是否符合预期
    output_df = logic_pd.read_excel(output_file)
    _test_apc_columns(output_df.columns.tolist(), fixture_apc_data_columns)
    assert len(output_df.values) == 1, "Logic APC 数据转换后, 应该只有 1 条数据"


    # case 3: 2 条数据, 但处理后应该只有一条
    output_file = None
    with patch("file_processor.processors.logic.pd.read_excel") as mock_read_excel:
        mock_read_excel.return_value = logic_pd.DataFrame(data=[
            [
                '2025-9-29 3:43:00','KLE231','0CSN','286','0CSN00286AA1','21','0.236384229','12.64316584','0.016574739',
                '0.016894928','0.057643334','-0.018472039','-0.096117685','-0.536043252','0.007014191','-0.287610648','NA'
            ],
            [
                '2025-9-29 3:43:00','KLE231','0CSN','286','0CSN00286AA1','25','0.236384229','12.64316584','0.016574739',
                '0.016894928','0.057643334','-0.018472039','-0.096117685','-0.536043252','0.007014191','-0.287610648','NA'
            ],
        ], columns=fixture_apc_data_columns["input_columns"])
        output_file =   logic.proc_apc_file(**fixture_logic)
    if output_file is None:
        pytest.fail("输出文件应该被创建")
    _ouput_file_check(output_file, 'APC_', '.xlsx')
    # 检查输出文件的内容是否符合预期
    output_df = logic_pd.read_excel(output_file)
    _test_apc_columns(output_df.columns.tolist(), fixture_apc_data_columns)
    assert len(output_df.values) == 1, "Logic APC 数据转换后, 应该只有 1 条数据"


    # case 4: 2 条数据, 因为参数差异，应该处理失败
    output_file = None
    with patch("file_processor.processors.logic.pd.read_excel") as mock_read_excel:
        mock_read_excel.return_value = logic_pd.DataFrame(data=[
            [
                '2025-9-29 3:43:00','KLE231','0CSN','286','0CSN00286AA1','21','0.236384229','12.64316584','0.016574739',
                '0.016894928','0.057643334','-0.018472039','-0.096117685','-0.536043252','0.007014191','-0.287610648','NA'
            ],
            [
                '2025-9-29 3:43:00','KLE231','0CSN','286','0CSN00286AA1','25','0.236384229','12.64316584','0.016574739',
                '0.016894928','0.057643334','-0.018472039','-0.096117685','-0.536043252','0.007014195','-0.287610648','NA'
            ],
        ], columns=fixture_apc_data_columns["input_columns"])
        with pytest.raises(ValueError, match="参数有差异不能合并"):
            logic.proc_apc_file(**fixture_logic)


    # case 5: 2 条数据，layer_id 列不同，合并后数据应该有 2 条
    output_file = None
    with patch("file_processor.processors.logic.pd.read_excel") as mock_read_excel:
        mock_read_excel.return_value = logic_pd.DataFrame(data=[
            [
                '2025-9-29 3:43:00','KLE231','0CSN','286','0CSN00286AA1','21','0.236384229','12.64316584','0.016574739',
                '0.016894928','0.057643334','-0.018472039','-0.096117685','-0.536043252','0.007014191','-0.287610648','NA'
            ],
            [
                '2025-9-29 3:43:00','KLE231','0CSN','127','0CSN00286AA1','25','0.236384229','12.64316584','0.016574739',
                '0.016894928','0.057643334','-0.018472039','-0.096117685','-0.536043252','0.007014195','-0.287610648','NA'
            ],
        ], columns=fixture_apc_data_columns["input_columns"])
        output_file =   logic.proc_apc_file(**fixture_logic)
    if output_file is None:
        pytest.fail("输出文件应该被创建")
    _ouput_file_check(output_file, 'APC_', '.xlsx')
    # 检查输出文件的内容是否符合预期
    output_df = logic_pd.read_excel(output_file)
    _test_apc_columns(output_df.columns.tolist(), fixture_apc_data_columns)
    assert len(output_df.values) == 2, "Logic APC 数据转换后, 应该只有 2 条数据"


    # case 6: 验证 第 8 列数据是否正确
    output_file = None
    with patch("file_processor.processors.logic.pd.read_excel") as mock_read_excel:
        mock_read_excel.return_value = logic_pd.DataFrame(data=[
            [
                '2025-9-29 3:43:00','KLE231','0CSN','286','0CSN00286AA1','21','0.236384229','12.64316584','0.016574739',
                '0.016894928','0.057643334','-0.018472039','-0.096117685','-0.536043252','0.007014191','-0.287610648','NA'
            ],
            [
                '2025-9-29 3:43:00','KLE231','0CSN','286','0CSN00286AA1','25','0.236384229','12.64316584','0.016574739',
                '0.016894928','0.057643334','-0.018472039','-0.096117685','-0.536043252','0.007014191','-0.287610648','NA'
            ],
        ], columns=fixture_apc_data_columns["input_columns"])
        output_file =   logic.proc_apc_file(**fixture_logic)
    if output_file is None:
        pytest.fail("输出文件应该被创建")
    _ouput_file_check(output_file, 'APC_', '.xlsx')
    # 检查输出文件的内容是否符合预期
    output_df = logic_pd.read_excel(output_file, dtype=object)
    _test_apc_columns(output_df.columns.tolist(), fixture_apc_data_columns)
    assert len(output_df.values) == 1, "Logic APC 数据转换后, 应该只有 1 条数据"
    assert output_df.iloc[:, 7].tolist() == [convert_subtitle_id_to_binstr(['xxx_21', 'xxx_25'])], f"Logic APC 数据转换后, 第 8 列数据应该为 {convert_subtitle_id_to_binstr(['xxx_21', 'xxx_25'])}, 实际为 {output_df.iloc[:, 7].tolist()}"


    
    # case 7: 验证: 日期字段没有秒
    output_file = None
    with patch("file_processor.processors.logic.pd.read_excel") as mock_read_excel:
        mock_read_excel.return_value = logic_pd.DataFrame(data=[
            [
                '2025-9-29 3:43','KLE231','0CSN','286','0CSN00286AA1','25','0.236384229','12.64316584','0.016574739',
                '0.016894928','0.057643334','-0.018472039','-0.096117685','-0.536043252','0.007014191','-0.287610648','NA'
            ],
            [
                '2025-9-29 3:43','KLE231','0CSN','286','0CSN00286AA1','25','0.236384229','12.64316584','0.016574739',
                '0.016894928','0.057643334','-0.018472039','-0.096117685','-0.536043252','0.007014191','-0.287610648','NA'
            ],
        ], columns=fixture_apc_data_columns["input_columns"])
        output_file =   logic.proc_apc_file(**fixture_logic)
    if output_file is None:
        pytest.fail("输出文件应该被创建")
    _ouput_file_check(output_file, 'APC_', '.xlsx')
    # 检查输出文件的内容是否符合预期
    output_df = logic_pd.read_excel(output_file, dtype=object)
    _test_apc_columns(output_df.columns.tolist(), fixture_apc_data_columns)
