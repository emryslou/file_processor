from pathlib import Path
import fnmatch
import paramiko

from .store import Store
from file_processor.utils.logger import logger


class SFTPStore(Store):
    __type__ = 'sftp'

    def __init__(self, name: str, root_path: str|Path, **config: dict):
        super().__init__(name, root_path, **config)
        self.root_path = Path(root_path)
        self.host = config['host']
        self.port = config['port']
        self.user = config['user']
        self.password = config['password']
        
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(self.host, self.port, self.user, self.password)
        self.sftp = self.ssh_client.open_sftp()
        self.sftp.encoding = config.get('encoding', 'utf-8')    
        
    def get_path(self, path: str) -> str:
        return str(self.root_path / path)
    
    def upload(self, local_path: str|Path, remote_path: str|Path):
        """
        上传本地文件到远程存储

        Args:
            local_path (str|Path): 本地文件路径
            remote_path (str|Path): 远程存储路径
        """
        try:
            local_path = Path(local_path)
            with open(local_path, 'rb') as f:
                remote_path = Path(remote_path) / local_path.name
                if self.is_win:
                    remote_path = Path(remote_path).as_posix()
                logger.info(f"上传文件 {local_path} 到 {remote_path}")
                self.sftp.put(local_path, str(remote_path))
        except Exception as e:
            logger.exception(f"上传文件 {local_path} 到 {remote_path} 失败: {e}")
            raise Exception(f"上传文件 {local_path} 到 {remote_path} 失败: {e}")
    
    def download(self, remote_path: str|Path, local_path: str|Path) -> Path:
        """
        从远程存储下载文件到本地

        Args:
            remote_path (str|Path): 远程存储路径
            local_path (str|Path): 本地文件路径
        """
        try:
            if self.is_win:
                remote_path = Path(remote_path).as_posix()
            with open(local_path, 'wb') as f:
                logger.info(f"下载文件 {remote_path} 到 {local_path}")
                self.sftp.get(remote_path, local_path)
                return Path(local_path)
        except Exception as e:
            logger.exception(f"下载文件 {remote_path} 到 {local_path} 失败: {e}")
            raise Exception(f"下载文件 {remote_path} 到 {local_path} 失败: {e}")
    
    def delete(self, remote_path: str|Path):
        """
        删除远程存储中的文件

        Args:
            remote_path (str|Path): 远程存储路径
        """
        try:
            if self.is_win:
                remote_path = Path(remote_path).as_posix()
            self.sftp.remove(remote_path)
        except Exception as e:
            logger.exception(f"删除文件 {remote_path} 失败: {e}")
            raise Exception(f"删除文件 {remote_path} 失败: {e}")    
    
    def list(self, remote_path: str|Path, pattern: str = '*') -> list:
        """
        列出远程存储中的文件，支持模糊匹配

        Args:
            remote_path (str|Path): 远程存储路径
            pattern (str, optional): 文件模式匹配（支持通配符如 *.txt, file?.csv 等）. Defaults to '*'.

        Returns:
            list: 远程存储中的文件列表
        """
        logger.info(f"列出目录 {remote_path} 中的文件")
        try:
            if self.is_win:
                remote_path = Path(remote_path).as_posix()
            file_list = self.sftp.listdir(remote_path)  # 避免使用内置函数名list作为变量名
            logger.info(f"SFTP 列出目录 {remote_path} 中的文件，模式匹配: {pattern}: {file_list}")
            # 使用fnmatch进行真正的模糊匹配，只匹配文件名部分
            return [Path(remote_path) / Path(item) for item in file_list if fnmatch.fnmatch(Path(item).name, pattern)]
        except Exception as e:
            logger.exception(f"列出目录 {remote_path} 中的文件失败: {e}")
            raise Exception(f"列出目录 {remote_path} 中的文件失败: {e}")

    def exists(self, remote_path: str|Path) -> bool:
        """
        检查远程存储中的文件或目录是否存在

        Args:
            remote_path (str|Path): 远程存储路径

        Returns:
            bool: 文件或目录是否存在
        """
        try:
            if self.is_win:
                remote_path = Path(remote_path).as_posix()
            
            # 使用stat方法检查路径是否存在，这是最可靠和高效的方式
            # 只需要一次网络请求，且能正确处理空目录的情况
            self.sftp.stat(str(remote_path))
            logger.debug(f"路径 {remote_path} 存在")
            return True
        except FileNotFoundError:
            # 明确捕获文件不存在的异常
            logger.info(f"路径 {remote_path} 不存在")
            return False
        except PermissionError:
            # 捕获权限错误，这通常意味着路径存在但无法访问
            logger.info(f"路径 {remote_path} 存在但无法访问")
            return True
        except Exception as e:
            # 记录其他异常
            logger.info(f"检查路径 {remote_path} 时发生错误: {e}")
            return False
            
    def is_directory(self, remote_path: str|Path) -> bool:
        """
        专门检测是否为存在的目录

        Args:
            remote_path (str|Path): 远程存储路径

        Returns:
            bool: 是否是存在的目录
        """
        try:
            if self.is_win:
                remote_path = Path(remote_path).as_posix()
                
            # 使用stat获取文件属性并检查是否为目录
            mode = self.sftp.stat(str(remote_path)).st_mode
            return paramiko.SFTPAttributes.is_directory(mode)
        except Exception:
            return False
            
    def is_file(self, remote_path: str|Path) -> bool:
        """
        专门检测是否为存在的文件

        Args:
            remote_path (str|Path): 远程存储路径

        Returns:
            bool: 是否是存在的文件
        """
        try:
            if self.is_win:
                remote_path = Path(remote_path).as_posix()
                
            # 使用stat获取文件属性并检查是否为文件
            mode = self.sftp.stat(str(remote_path)).st_mode
            return not paramiko.SFTPAttributes.is_directory(mode)
        except Exception:
            return False

    def mkdir(self, remote_path: str|Path):
        """
        创建远程存储中的目录

        Args:
            remote_path (str|Path): 远程存储路径
        """
        if self.is_win:
            remote_path = Path(remote_path).as_posix()
        self.sftp.mkdir(str(remote_path))

    def rmdir(self, remote_path: str|Path):
        """
        删除远程存储中的目录

        Args:
            remote_path (str|Path): 远程存储路径
        """
        if self.is_win:
            remote_path = Path(remote_path).as_posix()
        self.sftp.rmdir(remote_path)

    def rm(self, remote_path: str|Path):
        """
        删除远程存储中的文件

        Args:
            remote_path (str|Path): 远程存储路径
        """
        if self.is_win:
            remote_path = Path(remote_path).as_posix()
        self.sftp.remove(remote_path)

    def mv(self, src_path: str|Path, dst_path: str|Path):
        """
        移动远程存储中的文件

        Args:
            src_path (str|Path): 源文件路径
            dst_path (str|Path): 目标文件路径
        """
        if self.is_win:
            src_path = Path(src_path).as_posix()
            dst_path = Path(dst_path).as_posix()
        self.sftp.rename(src_path, dst_path)
    
    def close(self):
        if self.sftp:
            self.sftp.close()
            self.sftp = None
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
        logger.info(f"SFTP 连接已关闭(host: {self.host}, port: {self.port})")