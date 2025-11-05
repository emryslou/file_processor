from pathlib import Path
from file_processor.utils.config import store as store_config
from file_processor.stores.store import Store
from file_processor.stores.local import LocalStore as _LocalStore
from file_processor.stores.ftp import FTPStore as _FTPStore
from file_processor.stores.ftps import FTPSStore as _FTPSStore
from file_processor.stores.sftp import SFTPStore as _SFTPStore
from file_processor.utils.logger import logger


def create_store(store: str) -> Store:
    _type, _name = store.split('/')
    if _name in Store.__instances__:
        return Store.__instances__[_name]
    for plugin in Store.plugins():
        if plugin.__type__ == _type:
            _config = store_config(_type, _name)
            root_path = _config['root_path']
            del _config['root_path'], _config['name'], _config['type']
            _instance = plugin(_name, root_path, **_config)
            Store.__instances__[_name] = _instance
            return _instance

    raise ValueError(f"未支持的存储类型 {_type}")


def destroy_stores():
    for store_name, store_instaince in Store.__instances__.items():
        try:
            store_instaince.close()
            logger.info(f"回收存储资源: {store_instaince.__type__}/{store_name} 成功")            
        except Exception as e:
            logger.error(f"回收存储资源: {store_instaince.__type__}/{store_name} 时出错: {e}")
