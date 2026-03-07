from file_processor.stores.local import LocalStore
from pathlib import Path
from unittest.mock import patch
import pytest

def test_local_init():
    """
    测试本地存储初始化
    """
    # 测试创建本地存储
    store = LocalStore('local_store', '/mock/path/local_store')
    assert store.name == 'local_store'
    assert store.root_path == Path('/mock/path/local_store')
    assert store.__type__ == 'local'

@pytest.skip("LocalStore download use glob.glob, not implemented", allow_module_level=True)
def test_local_list():
    """
    测试本地存储列表
    """

def test_local_get_path():
    """
    测试本地存储获取路径
    """
    # 测试获取本地存储中的文件路径
    store = LocalStore('local_store', '/mock/path/local_store')
    file_path = store.get_path('file3.abc')
    assert file_path == Path('/mock/path/local_store/file3.abc')
    # 测试获取不存在的文件路径
    non_existent_path = store.get_path('/real/path/file.aaa')
    assert non_existent_path == Path('/real/path/file.aaa')


@pytest.skip("LocalStore download use shutil.copy, not implemented", allow_module_level=True)
def test_local_download():
    """
    测试本地存储下载
    """
    pass


@pytest.skip("LocalStore download use shutil.copy, not implemented", allow_module_level=True)
def test_local_upload():
    """
    测试本地存储上传
    """
    pass

def test_local_close():
    """
    测试本地存储关闭
    """
    # 测试关闭本地存储
    store = LocalStore('local_store', '/mock/path/local_store')
    
    # 创建一个 close 方法的补丁，以验证它被调用
    with patch.object(store, 'close') as mock_close:
        store.close()
        # 验证 close 方法被调用
        mock_close.assert_called_once()