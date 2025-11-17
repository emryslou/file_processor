from pathlib import Path
from ftplib import FTP_TLS
import fnmatch

from .store import Store
from file_processor.utils.logger import logger


class FTPSStore(Store):
    __type__ = 'ftps'

    def __init__(self, name: str, root_path: str|Path, **config: dict):
        super().__init__(name, root_path, **config)
        self.root_path = Path(root_path)
        self.host = config['host']
        self.port = config['port']
        self.user = config['user']
        self.password = config['password']
        self.timeout = config.get('timeout', 30)  # 连接超时设置，默认30秒
        self.debug = config.get('debug', False)  # 调试模式设置
        self.encoding = config.get('encoding', 'utf-8')  # 编码设置
        self.ftp = None
        self.connected = False
        self._connect()
        
    def _connect(self):
        """
        建立FTPS连接，支持降级处理
        """
        try:
            logger.info(f"正在连接FTPS服务器 {self.host}:{self.port}")
            self.ftp = FTP_TLS(timeout=self.timeout)
            
            # 设置调试级别（如果需要）
            if self.debug:
                self.ftp.set_debuglevel(2)
            
            # 连接服务器
            self.ftp.connect(self.host, self.port)
            logger.info(f"已连接到FTPS服务器 {self.host}:{self.port}")
            
            # 尝试以非TLS模式登录（处理534错误）
            try:
                # 有些服务器需要先设置保护级别为None再登录
                # self.ftp.prot_c()  # 清除保护命令
                self.ftp.login(self.user, self.password)
                logger.info(f"用户 {self.user} 以非TLS模式登录成功")
                
                # 尝试启用加密传输，如果失败则继续使用非加密模式
                try:
                    self.ftp.prot_p()  # 尝试启用加密数据传输
                    logger.info("已启用加密数据传输")
                except Exception as prot_error:
                    logger.warning(f"无法启用加密数据传输，继续使用非加密模式: {prot_error}")
                    
            except Exception as login_error:
                # 如果非TLS模式也失败，尝试标准TLS登录
                logger.warning(f"非TLS模式登录失败，尝试标准TLS登录: {login_error}")
                self.ftp.login(self.user, self.password)
                logger.info(f"用户 {self.user} 以标准TLS模式登录成功")
            
            # 设置被动模式
            self.ftp.set_pasv(True)
            logger.info("已设置被动模式")
            
            # 设置编码
            self.ftp.encoding = self.encoding
            logger.info(f"已设置编码为 {self.ftp.encoding}")
            
            self.connected = True
            logger.info("FTPS连接初始化完成")
            
        except Exception as e:
            self.connected = False
            error_msg = str(e)
            logger.exception(f"FTPS连接初始化失败: {e}")
            
            # 特殊处理534错误
            if "534 Local policy on server does not allow TLS secure connections" in error_msg:
                logger.info("检测到534错误，服务器不支持TLS连接，建议尝试使用普通FTP连接")
                raise Exception(f"无法连接到FTPS服务器 {self.host}:{self.port}: {e}\n提示：服务器不支持TLS连接，请检查服务器配置或尝试使用普通FTP连接")
            else:
                raise Exception(f"无法连接到FTPS服务器 {self.host}:{self.port}: {e}")
        
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
            if self.is_win:
                remote_path = Path(remote_path).as_posix()
            with open(local_path, 'wb') as f:
                logger.info(f"下载文件 {remote_path} 到 {local_path}")
                self.ftp.retrbinary(f'RETR {remote_path}', f.write)
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
            self.ftp.delete(remote_path)
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
        logger.info(f"FTPS 列出远程路径 {remote_path} 中的文件，模式匹配 {pattern}")
        file_list = self.ftp.nlst('/')
        logger.info(f"FTPS 根目录文件列表: {file_list}")
        if self.is_win:
            remote_path = Path(remote_path).as_posix()
        file_list = self.ftp.nlst(remote_path)  # 避免使用内置函数名list作为变量名
        logger.info(f"FTPS 列出 {remote_path} 中的文件，模式匹配: {pattern}: {file_list}")
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
        self.ftp.mkd(remote_path)

    def rmdir(self, remote_path: str|Path):
        """
        删除远程存储中的目录

        Args:
            remote_path (str|Path): 远程存储路径
        """
        if self.is_win:
            remote_path = Path(remote_path).as_posix()
        self.ftp.rmd(remote_path)

    def rm(self, remote_path: str|Path):
        """
        删除远程存储中的文件

        Args:
            remote_path (str|Path): 远程存储路径
        """
        if self.is_win:
            remote_path = Path(remote_path).as_posix()    
        self.ftp.delete(remote_path)

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
        self.ftp.rename(src_path, dst_path)
    
    def close(self):
        """
        关闭FTPS连接
        """
        if self.ftp and self.connected:
            try:
                self.ftp.quit()  # 尝试优雅关闭
                logger.info(f"FTPS连接已关闭 (host: {self.host}:{self.port})")
            except Exception as e:
                logger.exception(f"关闭FTPS连接时出错: {e}")
                try:
                    self.ftp.close()  # 强制关闭
                except:
                    pass
            finally:
                self.connected = False
                self.ftp = None
