from logging import root
import pytest
from unittest.mock import patch
from pathlib import Path


@pytest.fixture(scope="function")
def ftp_store_fixture():
    from file_processor.stores.ftp import FTPStore
    store = FTPStore('test_ftp', '/应用文件-xunlei/data/data', host="192.168.1.27", port=2121, user="admin", password="Abcd1234")
    yield store
    store.close()


def test_ftp_init(ftp_store_fixture):
    """
    测试FTPStore初始化
    """
    store = ftp_store_fixture
    assert store.__type__ == 'ftp'
    assert store.name == "test_ftp"
    assert store.root_path == Path("/应用文件-xunlei/data/data")
    assert store.host == "192.168.1.27"
    assert store.port == 2121
    assert store.user == "admin"
    assert store.password == "Abcd1234"

def test_ftp_list(ftp_store_fixture):
    """
    测试FTPStore列表文件
    """
    store = ftp_store_fixture
    root_path = store.root_path
    mock_root_path_files = [
        'file1.txt',
        'file2.txt',
        'dir1',
        'dir2',
        'csv1.csv',
        'csv2.csv',
        'excel1.xlsx',
        'excel2.xlsx',
        'word1.docx',
        'word2.docx',
        'excel3.xls',
        'excel4.xls',
    ]
    with patch.object(store, 'ftp') as mock_ftp:
        mock_ftp.nlst.return_value = mock_root_path_files
        files = store.list(str(root_path), '*')
        assert len(files) == len(mock_root_path_files)
        assert files == [root_path / Path(item) for item in mock_root_path_files]

        math_files_xlsx = store.list(str(root_path), '*.xlsx')
        assert len(math_files_xlsx) == 2
        assert math_files_xlsx == [root_path / Path(item) for item in mock_root_path_files if item.endswith('.xlsx')]


        math_files_xls = store.list(str(root_path), '*.xls')
        assert len(math_files_xls) == 2
        assert math_files_xls == [root_path / Path(item) for item in mock_root_path_files if item.endswith('.xls')]


        match_files_contain_xls = store.list(str(root_path), '*xls*')
        assert len(match_files_contain_xls) == 4
        assert match_files_contain_xls == [root_path / Path(item) for item in mock_root_path_files if 'xls' in item]
