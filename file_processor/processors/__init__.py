from tkinter import NO
from webbrowser import get
from file_processor.utils.config import processor as processor_config
from file_processor.stores import create_store
from file_processor.utils.logger import logger
from pathlib import Path

from . import logic, dram

_drivers = {
    'logic': logic,
    'dram': dram,
}

def get_proc_path(path_type: str, proc_info: dict, srv_path: dict):
    """获取处理函数的上传路径

    Args:
        path_type (str): 路径类型，ul_path 或 dl_path
        proc_info (dict): 处理类型配置
        srv_path (dict): 存储配置

    Returns:
        str: 处理函数的上传路径
    """

    path = srv_path['path']
    proc_path = proc_info.get(path_type, None)
    if proc_path:
        logger.info(f"{proc_info['type']} 已设置{path_type}: {proc_path}，替换默认: {path}")
        path = proc_path
    else:
        logger.info(f"{proc_info['type']} 未找到{path_type}，使用默认路径:{path}")
    return path

def proc_files(config: dict):
    """处理 文件的逻辑函数
    处理流程
    1. 从配置文件中获取 dl_path, ul_path, bak_path 三个路径
    2. 从 dl_path 中扫描所有符合 proc_types 中 filter 的文件
    3. 对每个文件调用对应的处理函数，处理后的文件放入 ul_path 中
    4. 若处理成功，将原文件移动到 bak_path 中
    """
    result = {
        'status': '',
        'message': '',
        'info': {},
    }
    assert 'driver' in config, "未指定驱动"
    driver = config['driver']
    assert driver is not None, "未指定驱动"
    assert driver in _drivers, f"未找到驱动 {driver}"
    stores: dict[str, dict] = {}
    try:
        result['status'] = 'store'
        stores = {   
            key: {
                'store': create_store(config[key_cfg]['store']),
                'config': config[key_cfg]
            }
            for key, key_cfg in {
                'dl': 'dl_path', 'ul': 'ul_path', 'bak': 'bak_path',
            }.items()
        }

        result['status'] = 'scan_path'
        # scan_path = stores['dl']['store'].get_path(stores['dl']['config']['path'])
        tmp_path = Path('data/tmp/') / driver
        if not tmp_path.exists():
            tmp_path.mkdir(parents=True)

        result['status'] = 'proc_type'
        backup_files = {}
        for proc_info in config['proc_types']:
            proc_type = proc_info['type']
            fn_name = f"proc_{proc_type}_file"
            result['info'][proc_type] = {
                'filter': proc_info['filter'],
                'driver': config['driver'],
                'proc_type': proc_type,
                'files': {}
            }
            
            fn = getattr(_drivers[config['driver']], fn_name, None)
            if fn is None:
                logger.error(f"未找到处理函数 {fn_name}")
                result['info'][proc_type]['error'] = f"未找到处理函数 {fn_name}"
                continue
            
            
            scan_path = stores['dl']['store'].get_path(get_proc_path('dl_path', proc_info, stores['dl']['config']))
            logger.info(f"{driver} {proc_type} 扫描路径 {scan_path} 下符合 {proc_info['filter']} 的文件")
            procs_files = stores['dl']['store'].list(scan_path, proc_info['filter'])
            logger.info(f"{driver} {proc_type} 发现 {len(procs_files)} 个文件需要处理")
            logger.info(f"{driver} {proc_type} 需要处理的文件列表: {procs_files}")
            result['info'][proc_type]['files'] = {
                'files': procs_files, 'success': {}, 'error': {},
            }

            proc_ul_path = get_proc_path('ul_path', proc_info, stores['ul']['config'])

            for input_file in procs_files:
                try:
                    remote_file = stores['dl']['store'].get_path(input_file)
                    
                    # 下载到本地
                    input_file = stores['dl']['store'].download(remote_file, tmp_path / input_file.name)
                    # 处理文件
                    output_file = fn(input_file, tmp_path)
                    
                    # 上传到 ul_path
                    stores['ul']['store'].upload(output_file, stores['ul']['store'].get_path(proc_ul_path))
                    logger.info(f"{driver} 文件 {input_file} 处理完成, 处理后的文件: {output_file}")

                    # 备份到 bak_path   
                    backup_files[str(remote_file)] = Path(stores['bak']['config']['path']) / input_file.name

                    result['info'][proc_type]['files']['success'][str(input_file)] = str(output_file)
                except Exception as e:
                    result['info'][proc_type]['files']['error'][str(input_file)] = '处理文件时出错: ' + str(e)

        # 备份所有文件
        result['status'] = 'backup_files'
        for input_file, bak_file in backup_files.items():
            stores['bak']['store'].mv(input_file, stores['bak']['store'].get_path(bak_file))
            logger.info(f"{driver} 文件 {input_file} 备份到 {bak_file}")
        
        if not any(result['info'][proc_type]['files']['error'] for proc_type in result['info']):
            result['status'] = 'success'
        else:
            result['status'] = 'partial_success'
    except Exception as e:
        logger.exception(f"处理文件 {driver} 时出错: {e}")
        result['status'] = f"{result['status']}_error"
        result['message'] = f"处理文件 {driver} 时出错: " + str(e)  
    finally:
        return result


__all__ = [
    'proc_files',
]
