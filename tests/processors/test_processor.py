from file_processor.processors import get_proc_path, proc_files
import pytest
from pathlib import Path


@pytest.fixture(scope="function")
def fixture_proc_info():
    return {
        "type": "ul_path",
        "ul_path": "demo/01"
    }

@pytest.fixture(scope="function")
def fixture_srv_path():
    return {"path": Path("/test_path")}

def test_get_proc_path(fixture_proc_info, fixture_srv_path):
    """
    测试获取处理器路径函数
    """
    assert str(get_proc_path("ul_path", fixture_proc_info, fixture_srv_path)) == "demo/01"
    assert str(get_proc_path("dl_path", fixture_proc_info, fixture_srv_path)) == "/test_path"


def test_proc_files_driver_error():
    """
    测试处理器文件函数驱动错误
    """
    with pytest.raises(AssertionError, match="未指定驱动"):
        proc_files({})
    with pytest.raises(AssertionError, match="未指定驱动"):
        proc_files({"driver": None})
    with pytest.raises(AssertionError, match="未找到驱动"):
        proc_files({"driver": "nonexistent"})
