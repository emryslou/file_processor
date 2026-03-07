import pytest

@pytest.skip("meta test should be passed, because it has not function code", allow_module_level=True)
def test_meta():
    """
    测试元数据函数
    """
    pass 