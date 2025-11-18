from file_processor.processors import dram
from . import fixture_dram, pytest, Path
import pandas as pd


@pytest.fixture(scope="function", autouse=True)
def fixture_dram_t7_code(fixture_dram, test_file, output_dir):
    """
    为DRAM T7代码测试提供 fixture
    """
    import shutil
    root_data_path = fixture_dram["root_data_path"]
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
def test_dram_t7_code(fixture_dram_t7_code):
    """
    测试DRAM T7代码函数
    """
    assert Path(fixture_dram_t7_code["input_file"]).exists(), "输入文件应该存在的"
    output_file = dram.proc_t7_code_file(**fixture_dram_t7_code)
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
        assert sheet.ncols > 0, "输出文件的'Sheet1'工作表应该有数据列"


def test_dram_coa():
    """
    测试DRAM COA函数
    """


def test_dram_apc():
    """
    测试DRAM APC函数
    """
