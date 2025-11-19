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