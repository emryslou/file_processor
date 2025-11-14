from pathlib import Path

from .store import Store

class LocalStore(Store):
    """
    本地存储类

    Args:
        name (str): 存储类的名称
        root_path (str|Path): 存储类的根路径
    """
    __type__ = 'local'

    def __init__(self, name: str, root_path: str|Path, **config: dict):
        super().__init__(name, root_path, **config)
        self.root_path = Path(root_path)

    def get_path(self, rel_path: str|Path) -> Path:
        rel_path = str(Path(rel_path))

        if rel_path.startswith(str(self.root_path)):
            return Path(rel_path)
        
        return self.root_path / rel_path
        
        
    def upload(self, local_path: str|Path, remote_path: str|Path):
        """
        上传本地文件到远程存储

        Args:
            local_path (str|Path): 本地文件路径
            remote_path (str|Path): 远程存储路径
        """
        import shutil
        shutil.copy(local_path, remote_path)
    
    def download(self, remote_path: str|Path, _local_path: str|Path) -> Path:
        """
        从远程存储下载文件到本地

        Args:
            remote_path (str|Path): 远程存储路径
            local_path (str|Path): 本地文件路径
        """
        import shutil
        shutil.copy(remote_path, _local_path)
        return Path(_local_path)
    
    def delete(self, remote_path: str|Path):
        """
        删除远程存储中的文件

        Args:
            remote_path (str|Path): 远程存储路径
        """
        pass
    
    def list(self, remote_path: str|Path, pattern: str) -> list:
        """
        列出远程存储中的文件

        Args:
            remote_path (str|Path): 远程存储路径

        Returns:
            list: 远程存储中的文件列表
        """
        import glob
        return [Path(remote_path) / f for f in glob.glob(pattern, root_dir=remote_path)]

    def exists(self, remote_path: str|Path) -> bool:
        """
        检查远程存储中的文件是否存在

        Args:
            remote_path (str|Path): 远程存储路径

        Returns:
            bool: 文件是否存在
        """
        return (self.root_path / remote_path).exists()

    def mkdir(self, remote_path: str|Path):
        """
        创建远程存储中的目录

        Args:
            remote_path (str|Path): 远程存储路径
        """
        pass

    def rmdir(self, remote_path: str|Path):
        """
        删除远程存储中的目录

        Args:
            remote_path (str|Path): 远程存储路径
        """
        pass

    def rm(self, remote_path: str|Path):
        """
        删除远程存储中的文件

        Args:
            remote_path (str|Path): 远程存储路径
        """
        pass

    def mv(self, src_path: str|Path, dst_path: str|Path):
        """
        移动远程存储中的文件

        Args:
            src_path (str|Path): 源文件路径
            dst_path (str|Path): 目标文件路径
        """
        import shutil
        shutil.move(src_path, dst_path)

    def close(self):
        """
        关闭与远程存储的连接
        """
        pass