import yaml
from pathlib import Path

_CONFIG: dict|None = None
_STORE_CONFIGS: dict|None = None
_PROCESSOR_CONFIGS: dict|None = None
_NOTIFY_CONFIGS: dict|None = None
_LOGGER_CONFIGS: dict|None = None


def __init_store_configs():
    global _STORE_CONFIGS, _CONFIG
    _STORE_CONFIGS = {}
    
    for store_config in _CONFIG.get('stores', []):
        if store_config['type'] not in _STORE_CONFIGS:
            _STORE_CONFIGS[store_config['type']] = {}
        _STORE_CONFIGS[store_config['type']][store_config['name']] = store_config

def __init_notify_configs():
    global _NOTIFY_CONFIGS, _CONFIG

    _NOTIFY_CONFIGS = {}
    for notify_config in _CONFIG.get('notification', []):
        _NOTIFY_CONFIGS[notify_config['type']] = notify_config


def __init_processor_configs():
    global _PROCESSOR_CONFIGS, _CONFIG
    _PROCESSOR_CONFIGS = {}
    
    for _config in _CONFIG.get('processors', []):
        if _config['driver'] not in _PROCESSOR_CONFIGS:
            _PROCESSOR_CONFIGS[_config['driver']] = {}
        _PROCESSOR_CONFIGS[_config['driver']][_config['name']] = _config



def __init_logger_configs():
    global _LOGGER_CONFIGS, _CONFIG
    _LOGGER_CONFIGS = _CONFIG.get('logger', {})



def load_config(config_file: str|Path) -> dict:
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        global _CONFIG
        _CONFIG = config['app']
        __init_store_configs()
        __init_processor_configs()
        __init_notify_configs()
        __init_logger_configs()
    return config


def store(store_type: str, store_name: str) -> dict:
    if _STORE_CONFIGS is None:
        raise ValueError("存储配置未初始化，请先调用load_config")
    return _STORE_CONFIGS[store_type][store_name]

def processor(driver: str, processor_name: str) -> dict:
    if _PROCESSOR_CONFIGS is None:
        raise ValueError("处理器配置未初始化，请先调用load_config")
    return _PROCESSOR_CONFIGS[driver][processor_name]

def notify(notify_type: str) -> dict:
    if _NOTIFY_CONFIGS is None:
        raise ValueError("通知配置未初始化，请先调用load_config")
    return _NOTIFY_CONFIGS[notify_type]

def logger() -> dict:
    return _LOGGER_CONFIGS
