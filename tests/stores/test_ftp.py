from logging import root
import pytest
from unittest.mock import patch
from pathlib import Path
import sys

from file_processor.stores.ftp import FTPStore

pytest.skip("FTP skip", allow_module_level=True)


@pytest.fixture(scope="function")
def ftp_store_fixture():
    
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

def test_ftp_upload(ftp_store_fixture):
    """
    测试FTPStore上传文件
    """
    store: FTPStore = ftp_store_fixture
    root_path = store.root_path
    local_path = Path('/tmp/file1.txt')
    local_path.write_text('test content')
    assert local_path.exists(), "本地文件不存在"
    try:
        store.upload(local_path, root_path)
        # mock_ftp.storbinary.assert_called_once_with(f'STOR {root_path}', open(local_path, 'rb'))
        assert store.list(str(root_path), 'file1.txt') == [root_path / 'file1.txt']
    finally:
        local_path.unlink(missing_ok=True)
        store.rm(root_path / 'file1.txt')

def test_ftp_exists(ftp_store_fixture):
    """
    测试FTPStore检查文件是否存在
    """
    store = ftp_store_fixture
    root_path = store.root_path
    import random
    local_file = Path('/tmp') / f'tmp_file_{random.randint(0, 1000000)}.txt'
    local_file.write_text(f'test content {local_file.name}')
    
    try:
        store.upload(local_file, root_path)
        assert store.exists(str(root_path / local_file.name)) == True
        store.rm(root_path / local_file.name)
        assert store.exists(str(root_path / local_file.name)) == False
    finally:
        local_file.unlink(missing_ok=True)

def test_ftp_download(ftp_store_fixture):
    """
    测试FTPStore下载文件
    """
    store = ftp_store_fixture
    root_path = store.root_path
    """
    测试FTPStore下载文件
    对应方法是: FTPStore.download(remote_path: str|Path, local_path: str|Path)
    """
    import random
    local_file = Path('/tmp') / f'tmp_file_{random.randint(0, 1000000)}.txt'
    local_file.write_text(f'test content {local_file.name}')
    assert local_file.exists(), "本地文件不存在"
    download_file = Path('/tmp') / f'tmp_download_file_{random.randint(0, 1000000)}.txt'
    try:
        store.upload(local_file, root_path)
        store.download(root_path / local_file.name, download_file)
        assert download_file.exists(), "下载的文件不存在"
        assert download_file.read_text() == f'test content {local_file.name}', "下载的文件内容与上传的不一致"
    finally:
        local_file.unlink(missing_ok=True)
        download_file.unlink(missing_ok=True)
        store.rm(root_path / local_file.name)


def test_ftp_mk_rm_dir(ftp_store_fixture):
    """
    测试FTPStore创建目录
    """
    store: FTPStore = ftp_store_fixture
    root_path = store.root_path
    import random
    dir_name = f'tmp_dir_{random.randint(0, 1000000)}'
    
    store.mkdir(root_path / dir_name)
    assert store.exists(str(root_path / dir_name)), f"创建目录({dir_name})失败"
    store.rmdir(root_path / dir_name)
    assert not store.exists(str(root_path / dir_name)), f"删除目录({dir_name})失败"


@pytest.mark.skipif(not sys.platform.startswith('win'), reason="仅在Windows平台运行")
def test_ftp_mk_rm_dir_win(ftp_store_fixture):
    """
    测试FTPStore创建目录
    """
    store: FTPStore = ftp_store_fixture
    root_path = store.root_path
    import random
    dir_name = f'tmp_dir_{random.randint(0, 1000000)}'
    
    store.mkdir(root_path / dir_name)
    assert store.exists(str(root_path / dir_name)), "创建目录失败"
    store.rmdir(root_path / dir_name)
    assert not store.exists(str(root_path / dir_name)), "删除目录失败"

def test_ftp_mv_file(ftp_store_fixture):
    """
    测试FTPStore移动文件
    """
    store: FTPStore = ftp_store_fixture
    root_path = store.root_path
    import random
    local_file = Path('/tmp') / f'tmp_file_{random.randint(0, 1000000)}.txt'
    local_file.write_text(f'test content {local_file.name}')
    assert local_file.exists(), "本地文件不存在"
    try:
        test_dir = f'tmp_dir_{random.randint(0, 1000000)}'
        if not store.exists(root_path / test_dir):
            store.mkdir(root_path / test_dir)

        store.upload(local_file, root_path)
        assert store.exists(str(root_path / local_file.name)), "上传文件失败"
        store.mv(root_path / local_file.name, root_path / test_dir / local_file.name)   
        assert store.exists(root_path / test_dir / local_file.name), "新位置文件不存在, 移动失败"
        assert not store.exists(root_path / local_file.name), "旧位置文件存在, 移动失败"
    except Exception as e:
        assert False, f"移动文件失败: {e}"
    finally:
        local_file.unlink(missing_ok=True)
        store.rm(root_path / test_dir / local_file.name)
        store.rmdir(root_path / test_dir)
