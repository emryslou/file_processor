from pathlib import Path
import pytest
from unittest.mock import mock_open, patch

from file_processor.stores.store import Store
from file_processor.stores import create_store, destroy_stores
from file_processor.utils.config import load_config

DUMMY_STORE_CONFIG_YML = """
version: 1.0.0
app:
    stores:
        - name: dummy_store
          type: dummy
          root_path: /mock/path/store1
    processors:
        - driver: dram
          name: dram_processor
    logger:
        level: DEBUG
    notification:
        - type: email      
          subject: "文件处理报告"     # 邮件主题
          sender: "emrys.liu@foxmail.com"  # 发送者邮箱
          recipients:                       # 接收者邮箱列表
            - "emrys.liu@foxmail.com"
            # - "recipient2@example.com"
          smtp_server: "smtp.qq.com"   # SMTP服务器地址
          smtp_port: 465                    # SMTP服务器端口
          smtp_username: "emrys.liu@foxmail.com"  # SMTP用户名
          smtp_password: "xxxxxx"    # SMTP密码或授权码
"""


class DummyStore(Store):
    """
    用于测试的存储类
    """
    __type__ = 'dummy'
    def __init__(self, name: str, root_path: str|Path, **config: dict):
        super().__init__(name, root_path, **config)
    
    def upload(self, local_path: str|Path, remote_path: str|Path):
        """
        上传本地文件到远程存储

        Args:
            local_path (str|Path): 本地文件路径
            remote_path (str|Path): 远程存储路径
        """
        raise NotImplementedError
    
    def download(self, remote_path: str|Path, local_path: str|Path):
        """
        从远程存储下载文件到本地

        Args:
            remote_path (str|Path): 远程存储路径
            local_path (str|Path): 本地文件路径
        """
        raise NotImplementedError
    
    def delete(self, remote_path: str|Path):
        """
        删除远程存储中的文件

        Args:
            remote_path (str|Path): 远程存储路径
        """
        raise NotImplementedError
    
    def list(self, remote_path: str|Path) -> list:
        """
        列出远程存储中的文件

        Args:
            remote_path (str|Path): 远程存储路径

        Returns:
            list: 远程存储中的文件列表
        """
        raise NotImplementedError

    def exists(self, remote_path: str|Path) -> bool:
        """
        检查远程存储中的文件是否存在

        Args:
            remote_path (str|Path): 远程存储路径

        Returns:
            bool: 文件是否存在
        """
        raise NotImplementedError

    def mkdir(self, remote_path: str|Path):
        """
        创建远程存储中的目录

        Args:
            remote_path (str|Path): 远程存储路径
        """
        raise NotImplementedError

    def rmdir(self, remote_path: str|Path):
        """
        删除远程存储中的目录

        Args:
            remote_path (str|Path): 远程存储路径
        """
        raise NotImplementedError

    def rm(self, remote_path: str|Path):
        """
        删除远程存储中的文件

        Args:
            remote_path (str|Path): 远程存储路径
        """
        raise NotImplementedError

    def mv(self, src_path: str|Path, dst_path: str|Path):
        """
        移动远程存储中的文件

        Args:
            src_path (str|Path): 源文件路径
            dst_path (str|Path): 目标文件路径
        """
        raise NotImplementedError
    
    def close(self):
        """
        关闭与远程存储的连接
        """
        print(f"关闭存储 {self.__type__}/{self.name} 的连接")
        
def test_create_store():
    """
    测试存储函数
    """
    with pytest.raises(ValueError, match='存储配置未初始化'):
        create_store('dummy/my_dummy_store')
    
    with patch('builtins.open', mock_open(read_data=DUMMY_STORE_CONFIG_YML)) as mock_file:
        load_config('/mock/path/proc-config.yml')
        store = create_store('dummy/dummy_store')
        assert store.__class__ == DummyStore
        assert store.name == 'dummy_store'
        assert store.root_path == Path('/mock/path/store1')
        assert store.__type__ == 'dummy'

def test_destroy_stores():
    """
    测试销毁存储函数
    """
    with patch('builtins.open', mock_open(read_data=DUMMY_STORE_CONFIG_YML)) as mock_file:
        load_config('/mock/path/proc-config.yml')
        create_store('dummy/dummy_store')
        # 创建一个 close 方法的补丁，以验证它被调用
        with patch.object(DummyStore, 'close') as mock_close:
            destroy_stores()
            mock_close.assert_called_once()