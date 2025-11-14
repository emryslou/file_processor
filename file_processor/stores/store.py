from abc import ABC, abstractmethod
from pathlib import Path
import platform


class Store(ABC):
    """
    存储类的抽象基类

    Args:
        name (str): 存储类的名称
        root_path (str|Path): 存储类的根路径
    """
    
    __plugins__: list = []
    __instances__: dict = {}
    __type__: str = ''

    def __init_subclass__(cls, *args: tuple, **kwargs: dict) -> None:
        super().__init_subclass__(*args, **kwargs)
        cls.__plugins__.append(cls)
    
    @classmethod
    def plugins(cls) -> list:
        return cls.__plugins__
    
    def __init__(self, name: str, root_path: str|Path, **config: dict):
        self.name = name
        self.root_path = Path(root_path)
        self.config = config
        self.is_win = platform.system() == 'Windows'
        
    def get_path(self, rel_path: str|Path) -> Path:
        return self.root_path / rel_path
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(type: {self.__type__}, name: {self.name}, root_path:{self.root_path})"
    
    def get_config(self) -> dict:
        return self.config
    
    @abstractmethod
    def upload(self, local_path: str|Path, remote_path: str|Path):
        """
        上传本地文件到远程存储

        Args:
            local_path (str|Path): 本地文件路径
            remote_path (str|Path): 远程存储路径
        """
        raise NotImplementedError
    
    @abstractmethod
    def download(self, remote_path: str|Path, local_path: str|Path):
        """
        从远程存储下载文件到本地

        Args:
            remote_path (str|Path): 远程存储路径
            local_path (str|Path): 本地文件路径
        """
        raise NotImplementedError
    
    @abstractmethod
    def list(self, remote_path: str|Path) -> list:
        """
        列出远程存储中的文件

        Args:
            remote_path (str|Path): 远程存储路径

        Returns:
            list: 远程存储中的文件列表
        """
        raise NotImplementedError

    @abstractmethod
    def exists(self, remote_path: str|Path) -> bool:
        """
        检查远程存储中的文件是否存在

        Args:
            remote_path (str|Path): 远程存储路径

        Returns:
            bool: 文件是否存在
        """
        raise NotImplementedError

    @abstractmethod
    def mkdir(self, remote_path: str|Path):
        """
        创建远程存储中的目录

        Args:
            remote_path (str|Path): 远程存储路径
        """
        raise NotImplementedError

    @abstractmethod
    def rmdir(self, remote_path: str|Path):
        """
        删除远程存储中的目录

        Args:
            remote_path (str|Path): 远程存储路径
        """
        raise NotImplementedError

    @abstractmethod
    def rm(self, remote_path: str|Path):
        """
        删除远程存储中的文件

        Args:
            remote_path (str|Path): 远程存储路径
        """
        raise NotImplementedError

    @abstractmethod
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
        pass