import pytest
from pathlib import Path
from file_processor.stores.sftp import SFTPStore

@pytest.fixture(scope="function")
def sftp_store_fixture():
    """
    测试SFTPStore fixture
    """
    store = SFTPStore(
        name='sftp_store_fixture',
        root_path='/vol2/@appshare/xunlei/data/data',
        host='192.168.1.27',
        port=22,
        user='admin',
        password='Abcd1234',
    )
    yield store
    store.close()

def test_sftp_init(sftp_store_fixture):
    """
    测试SFTPStore初始化
    """
    store = sftp_store_fixture
    assert store.__type__ == 'sftp'
    assert store.name == "sftp_store_fixture"
    assert store.root_path == Path("/vol2/@appshare/xunlei/data/data")
    assert store.host == "192.168.1.27"
    assert store.port == 22
    assert store.user == "admin"
    assert store.password == "Abcd1234"

def test_sftp_upload(sftp_store_fixture):
    """
    测试SFTPStore上传文件
    """
    from random import randint
    store: SFTPStore = sftp_store_fixture
    local_file = Path(f'/tmp/test_upload_{randint(0, 1000000)}.txt')
    remote_file = store.root_path
    try:
        with local_file.open('w') as f:
            f.write('test content')
        store.upload(str(local_file), str(remote_file))
        assert store.exists(str(remote_file / local_file.name)), "SFTPStore上传文件后应该存在"
    except Exception as e:
        pytest.fail(f"SFTPStore上传文件失败: {e} {local_file} {remote_file}")
    finally:
        store.rm(str(remote_file / local_file.name))
        local_file.unlink(missing_ok=True)


def test_sftp_download(sftp_store_fixture):
    """
    测试SFTPStore下载文件
    """
    from random import randint
    store: SFTPStore = sftp_store_fixture
    local_file = Path(f'/tmp/test_download_{randint(0, 1000000)}.txt')
    remote_file = store.root_path
    new_local_file = Path(f'/tmp/aa_{local_file.name}')
    try:
        with local_file.open('w') as f:
            f.write('test content')
        store.upload(str(local_file), str(remote_file))
        store.download(str(remote_file / local_file.name), str(new_local_file))
        assert new_local_file.exists(), "SFTPStore下载文件后应该存在"
        with new_local_file.open('r') as f:
            content = f.read()
        assert content == 'test content', "SFTPStore下载文件内容应该正确"
    except Exception as e:
        pytest.fail(f"SFTPStore下载文件失败: {e} {local_file} {remote_file / local_file.name}")
    finally:
        new_local_file.unlink(missing_ok=True)
        store.rm(str(remote_file / local_file.name))
        local_file.unlink(missing_ok=True)


def test_sftp_mk_rmdir(sftp_store_fixture):
    """
    测试SFTPStore创建和删除目录
    """
    from random import randint
    store: SFTPStore = sftp_store_fixture
    dir_name = f'test_dir_{randint(0, 1000000)}'
    remote_dir = store.root_path / dir_name
    try:
        store.mkdir(str(remote_dir))
        assert store.exists(str(remote_dir)), "SFTPStore创建目录后应该存在"
        store.rmdir(str(remote_dir))
        assert not store.exists(str(remote_dir)), "SFTPStore删除目录后应该不存在"
    except Exception as e:
        pytest.fail(f"SFTPStore创建目录失败: {e} {remote_dir}")
    finally:
        pass


def test_sftp_exists(sftp_store_fixture):
    """
    测试SFTPStore检查文件是否存在
    """
    from random import randint
    store: SFTPStore = sftp_store_fixture
    dir_name = f'test_dir_{randint(0, 1000000)}'
    remote_dir = store.root_path / dir_name
    try:
        assert not store.exists(str(remote_dir)), "SFTPStore创建目录后应该不存在"
        store.mkdir(str(remote_dir))
        assert store.exists(str(remote_dir)), "SFTPStore创建目录后应该存在"
        test_file = Path('/tmp') / f'test_{randint(0, 1000000)}.txt'
        assert not store.exists(str(test_file)), "SFTPStore创建文件后应该不存在"
        with test_file.open('w') as f:
            f.write('test content')
        store.upload(str(test_file), str(store.root_path))
        assert store.exists(str(store.root_path / test_file.name)), "SFTPStore创建文件后应该存在"
    finally:
        pass