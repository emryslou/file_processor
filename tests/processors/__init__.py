import pytest
from pathlib import Path

@pytest.fixture(scope="session", autouse=True)
def fixture_processor():
    test_data_root = Path(__file__).parent.parent.parent / "data"
    assert test_data_root.exists(), f"测试数据根目录不存在: {test_data_root}"
    
    yield {
        "root_data_path": test_data_root,
    }
    # 测试结束后清理
    # for file in test_data_root.glob("*"):
    #     file.unlink()


def convert_subtitle_id_to_binstr(subtitle_ids: list) -> str:
    """
    将字幕ID列表转换为BINS字符串

    参数:
    subtitle_ids (list): 字幕ID列表

    返回:
    str: 对应的二进制字符串

    1100000000000000000000000
    """
    bin_num = 0b0
    max_subtitle_pos = 25
    for subtitle_id in subtitle_ids:
        bin_num |= 0b1 << int(max_subtitle_pos - 1 - (int(subtitle_id.split('_')[-1]) - 1))
    return format(bin_num, '025b')
