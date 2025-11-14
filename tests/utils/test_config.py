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
        assert processor_config['dl_path'] is not None
        assert processor_config['dl_path']['store'] == 'local/local_store'
        assert processor_config['dl_path']['path'] == 'dram/dl'

        assert processor_config['bak_path'] is not None
        assert processor_config['bak_path']['store'] == 'local/local_store'
        assert processor_config['bak_path']['path'] == 'dram/bak'
        assert processor_config['ul_path'] is not None
        assert processor_config['ul_path']['store'] == 'local/local_store'
        assert processor_config['ul_path']['path'] == 'dram/upload'

        assert processor_config['proc_types'] is not None
        assert len(processor_config['proc_types']) == 3
        assert processor_config['proc_types'][0]['type'] == 't7_code'
        assert processor_config['proc_types'][0]['filter'] == 't7_code*.xlsx'
        assert processor_config['proc_types'][0]['dl_path'] == 'dram/dl/t7_code'
        assert processor_config['proc_types'][0]['ul_path'] == 'dram/upload/t7_code'

        assert processor_config['proc_types'][1]['type'] == 'coa'
        assert processor_config['proc_types'][1]['filter'] == 'COA*.xlsx'
        assert processor_config['proc_types'][1]['dl_path'] == 'dram/dl/coa'
        assert processor_config['proc_types'][1]['ul_path'] == 'dram/upload/coa'
        
        assert processor_config['proc_types'][2]['type'] == 'apc'
        assert processor_config['proc_types'][2]['filter'] == '*APC*.xlsx'
        assert processor_config['proc_types'][2]['dl_path'] == 'dram/dl/apc'
        assert processor_config['proc_types'][2]['ul_path'] == 'dram/upload/apc'

def test_logger():
    """
    测试日志配置
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
    logger:
        level: DEBUG
    notification:
        - type: email
          to: 
            - user1@example.com
            - user2@example.com
"""
    with patch('builtins.open', mock_open(read_data=mock_file_content)) as mock_file:
        util_config.load_config(mock_file_name)
        logger_config = util_config.logger()
        assert logger_config is not None
        assert logger_config['level'] == 'DEBUG'

def test_notification():
    """
    测试通知配置
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
    with patch('builtins.open', mock_open(read_data=mock_file_content)) as mock_file:
        util_config.load_config(mock_file_name)
        notification_config = util_config.notify('email')
        assert notification_config is not None
        assert notification_config['type'] == 'email'
