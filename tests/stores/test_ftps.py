import pytest
from file_processor.stores.ftps import FTPSStore
from pathlib import Path
from unittest.mock import patch


@pytest.fixture(scope="function")
def ftps_store_fixture():
    store = FTPSStore('test_ftps', '/应用文件-xunlei/data/data', host="192.168.1.27", port=2121, user="admin", password="Abcd1234")
    yield store
    store.close()

def test_ftps_init(ftps_store_fixture):
    """
    测试FTPSStore初始化
    """
    store = ftps_store_fixture
    assert store.__type__ == 'ftps'
    assert store.name == "test_ftps"
    assert store.root_path == Path("/应用文件-xunlei/data/data")
    assert store.host == "192.168.1.27"
    assert store.port == 2121
    assert store.user == "admin"
    assert store.password == "Abcd1234"
    assert store.connected, "FTPSStore初始化时应该已连接"

def test_ftps_list(ftps_store_fixture):
    """
    测试FTPSStore列表文件
    """
    store = ftps_store_fixture
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

def test_ftps_upload(ftps_store_fixture):
    """
    测试FTPSStore上传文件
    """
    from random import randint
    store: FTPSStore = ftps_store_fixture
    local_file = Path(f'/tmp/test_upload_{randint(0, 1000000)}.txt')
    remote_file = store.root_path
    try:
        with local_file.open('w') as f:
            f.write('test content')
        store.upload(str(local_file), str(remote_file))
        assert store.exists(str(remote_file / local_file.name)), "FTPSStore上传文件后应该存在"
    finally:
        store.rm(str(remote_file / local_file.name))
        local_file.unlink(missing_ok=True)

def test_ftps_download(ftps_store_fixture):
    """
    测试FTPSStore下载文件
    """
    from random import randint
    store: FTPSStore = ftps_store_fixture
    local_file = Path(f'/tmp/test_download_{randint(0, 1000000)}.txt')
    remote_file = store.root_path / local_file.name
    try:
        with local_file.open('w') as f:
            f.write('test content')
        store.upload(str(local_file), str(remote_file))
        assert store.exists(str(remote_file)), "FTPSStore上传文件后应该存在"
        store.download(str(remote_file), str(local_file))
        assert local_file.exists(), "FTPSStore下载文件后应该存在"
        with local_file.open('r') as f:
            assert f.read() == 'test content', "FTPSStore下载文件内容应该与上传内容一致"
    finally:
        store.rm(str(remote_file))
        local_file.unlink(missing_ok=True)


def test_ftps_mv(ftps_store_fixture):
    """
    测试FTPSStore移动文件
    """
    from random import randint
    store: FTPSStore = ftps_store_fixture
    local_file = Path(f'/tmp/test_mv_{randint(0, 1000000)}.txt')
    remote_file = store.root_path / local_file.name
    try:
        with local_file.open('w') as f:
            f.write('test content')
        store.upload(str(local_file), str(remote_file))
        assert store.exists(str(remote_file)), "FTPSStore上传文件后应该存在"
        new_remote_file = store.root_path / f'test_mv_new_{randint(0, 1000000)}.txt'
        store.mv(str(remote_file), str(new_remote_file))
        assert store.exists(str(new_remote_file)), "FTPSStore移动文件后应该存在"
        assert not store.exists(str(remote_file)), "FTPSStore移动文件后原文件应该不存在"
    finally:
        store.rm(str(new_remote_file))
        local_file.unlink(missing_ok=True)

def test_ftps_mk_rmdir(ftps_store_fixture):
    """
    测试FTPSStore删除目录
    """
    from random import randint
    store: FTPSStore = ftps_store_fixture
    dir_name = f'test_rmdir_{randint(0, 1000000)}'
    remote_dir = store.root_path / dir_name
    try:
        store.mkdir(str(remote_dir))
        assert store.exists(str(remote_dir)), "FTPSStore创建目录后应该存在"
        store.rmdir(str(remote_dir))
        assert not store.exists(str(remote_dir)), "FTPSStore删除目录后应该不存在"
    finally:
        # store.rm(str(remote_dir))
        pass
