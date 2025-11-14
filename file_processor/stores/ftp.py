from pathlib import Path
from ftplib import FTP
import fnmatch

from .store import Store
from file_processor.utils.logger import logger


class FTPStore(Store):
    __type__ = 'ftp'

    def __init__(self, name: str, root_path: str|Path, **config: dict):
        super().__init__(name, root_path, **config)
        self.root_path = Path(root_path)
        self.host = config['host']
        self.port = config['port']
        self.user = config['user']
        self.password = config['password']
        self.ftp = FTP()
        self.ftp.connect(self.host, self.port, timeout=10)
        logger.info(f"连接 FTP 服务器 {self.host}:{self.port} 成功")
        self.ftp.login(self.user, self.password)
        logger.info(f"登录 FTP 服务器 : {self.ftp.pwd()}")
        self.ftp.set_pasv(True)
        self.ftp.encoding = config.get('encoding', 'utf-8')
        
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
            with open(local_path, 'rb') as f:
                remote_path = Path(remote_path) / local_path.name
                if self.is_win:
                    remote_path = Path(remote_path).as_posix()
                logger.info(f"上传文件 {local_path} 到 {remote_path}")
                self.ftp.storbinary(f'STOR {remote_path}', f)
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
            with open(local_path, 'wb') as f:
                if self.is_win:
                    remote_path = Path(remote_path).as_posix()
                logger.info(f"下载文件 {remote_path} 到 {local_path}")
                self.ftp.retrbinary(f'RETR {remote_path}', f.write)
                return Path(local_path)
        except Exception as e:
            logger.exception(f"下载文件 {remote_path} 到 {local_path} 失败: {e}")
            raise Exception(f"下载文件 {remote_path} 到 {local_path} 失败: {e}")
    
    
    def list(self, remote_path: str|Path, pattern: str = '*') -> list:
        """
        列出远程存储中的文件，支持模糊匹配

        Args:
            remote_path (str|Path): 远程存储路径
            pattern (str, optional): 文件模式匹配（支持通配符如 *.txt, file?.csv 等）. Defaults to '*'.

        Returns:
            list: 远程存储中的文件列表
        """
        logger.info(f"FTP 列出远程路径 {remote_path} 中的文件，模式匹配 {pattern}")
        file_list = self.ftp.nlst('/')
        logger.info(f"FTP 根目录文件列表: {file_list}")

        if self.is_win:
            remote_path = Path(remote_path).as_posix()
        file_list = self.ftp.nlst(remote_path)  # 避免使用内置函数名list作为变量名
        logger.info(f"FTP 列出 {remote_path} 中的文件，模式匹配: {pattern}: {file_list}")
        # 使用fnmatch进行真正的模糊匹配，只匹配文件名部分
        return [Path(remote_path) / Path(item) for item in file_list if fnmatch.fnmatch(Path(item).name, pattern)]

    def exists(self, remote_path: str|Path) -> bool:
        """
        检查远程存储中的文件是否存在

        Args:
            remote_path (str|Path): 远程存储路径

        Returns:
            bool: 文件是否存在
        """
        if self.is_win:
            remote_path = Path(remote_path).as_posix()
        try:
            self.ftp.size(str(remote_path))
            return True
        except Exception as e:
            if '550' in str(e) and 'No such file or directory' in str(e):
                return False
            
            try:
                cur_dir_bak = self.ftp.pwd()
                self.ftp.cwd(str(remote_path))
                self.ftp.cwd(cur_dir_bak)
                return True
            except Exception as e:
                logger.exception(f"检查目录 {remote_path} 是否存在失败: {e}")
                return False

    def mkdir(self, remote_path: str|Path):
        """
        创建远程存储中的目录

        Args:
            remote_path (str|Path): 远程存储路径
        """
        if self.is_win:
            remote_path = Path(remote_path).as_posix()    
        self.ftp.mkd(str(remote_path))

    def rmdir(self, remote_path: str|Path):
        """
        删除远程存储中的目录

        Args:
            remote_path (str|Path): 远程存储路径
        """
        if self.is_win:
            remote_path = Path(remote_path).as_posix()    
        self.ftp.rmd(str(remote_path))

    def rm(self, remote_path: str|Path):
        """
        删除远程存储中的文件

        Args:
            remote_path (str|Path): 远程存储路径
        """
        if self.is_win:
            remote_path = Path(remote_path).as_posix()    
        self.ftp.delete(str(remote_path))

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
        self.ftp.rename(str(src_path), str(dst_path))
    
    def close(self):
        if self.ftp:
            self.ftp.close()
            self.ftp = None
        logger.info(f"FTP 连接已关闭(host: {self.host}, port: {self.port})")
