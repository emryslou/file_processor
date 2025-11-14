import pytest

from file_processor.utils import config as util_config
from unittest.mock import mock_open, patch

def test_load_config():
    """
    测试配置函数
    """
    not_found_file = '/not_found.yml'
    with pytest.raises(FileNotFoundError):
        util_config.load_config(not_found_file)
    
    mock_file_name = '/mock/path/proc-config.yml'
    mock_file_content = """
version: 1.0.0
app:
    stores:
        - name: store1
          type: local
          path: /mock/path/store1
    processors:
        - name: processor1
          driver: local
    logger:
        level: DEBUG
    notification:
        - type: email
"""
    with patch('builtins.open', mock_open(read_data=mock_file_content)) as mock_file:
        config = util_config.load_config(mock_file_name)
        assert config['version'] == '1.0.0'
        assert config['app'] is not None
        assert config['app']['stores'] is not None
        assert config['app']['processors'] is not None
        assert config['app']['logger'] is not None
        assert config['app']['notification'] is not None

def test_store():
    """
    测试存储配置
    """
    mock_file_name = '/mock/path/proc-config.yml'
    mock_file_content = """
version: 1.0.0
app:
    stores:
        - name: local_store
          type: local
          path: /mock/path/store1
    processors:
        - name: processor1
          driver: local
    logger:
        level: DEBUG
    notification:
        - type: email
"""
    with patch('builtins.open', mock_open(read_data=mock_file_content)) as mock_file:
        util_config.load_config(mock_file_name)
        store_config = util_config.store('local', 'local_store')
        assert store_config is not None
        assert store_config['name'] == 'local_store'
        assert store_config['type'] == 'local'
        assert store_config['path'] == '/mock/path/store1'

def test_processor():
    """
    测试处理器配置
    """
    mock_file_name = '/mock/path/proc-config.yml'
    mock_file_content = """
version: 1.0.0
app:
    stores:
        - name: local_store
          type: local
          path: /mock/path/store1
    processors:
        - driver: dram
          name: dram_processor
          dl_path: 
            store: local/local_store # 存储类型/存储名称
            path: dram/dl # 下载路径
          bak_path: 
            store: local/local_store # 存储类型/存储名称
            path: dram/bak # 备份路径
          ul_path: 
            store: local/local_store # 存储类型/存储名称
            path: dram/upload # 上传路径, 或被覆盖或者指定
          proc_types: # 处理类型
            - type: t7_code # T7Code文件处理
              filter: 't7_code*.xlsx' # 匹配t7_code*.xlsx文件
              dl_path: dram/dl/t7_code # 下载路径, 或被覆盖或者指定
              ul_path: dram/upload/t7_code # 上传路径, 或被覆盖或者指定
            - type: coa # COA文件处理
              filter: 'COA*.xlsx' # 匹配COA*.xlsx文件
              dl_path: dram/dl/coa # 下载路径, 或被覆盖或者指定 
              ul_path: dram/upload/coa # 上传路径, 或被覆盖或者指定
            - type: apc # APC文件处理
              filter: '*APC*.xlsx' # 匹配*APC*.xlsx文件
              dl_path: dram/dl/apc # 下载路径, 或被覆盖或者指定 
              ul_path: dram/upload/apc # 上传路径 ，相对于 store.root_path, 会覆盖 url.path -----
    logger:
        level: DEBUG
    notification:
        - type: email
"""
    with patch('builtins.open', mock_open(read_data=mock_file_content)) as mock_file:
        util_config.load_config(mock_file_name)
        processor_config = util_config.processor('dram', 'dram_processor')
        assert processor_config is not None
        assert processor_config['name'] == 'dram_processor'
        assert processor_config['driver'] == 'dram'
