from file_processor.stores import create_store, Store
from file_processor.utils.logger import logger
from pathlib import Path
from types import ModuleType

from . import logic, dram



_drivers: dict[str, ModuleType] = { 'logic': logic, 'dram': dram, }

def _proc_files_init_store(config: dict) -> dict[str, dict[str, Store]]:
    """初始化处理文件的 store
    """
    stores: dict[str, dict[str, Store]] = {}
    for key, key_cfg in {
        'dl': 'dl_path', 'ul': 'ul_path', 'bak': 'bak_path',
    }.items():
        stores[key] = {
            'store': create_store(config[key_cfg]['store']),
            'config': config[key_cfg]
        }
    
    assert len(stores) == 3, "初始化 store 失败"
    for key in stores:
        assert stores[key]['store'] is not None or len(stores[key]['config']['path']) > 0, f"初始化 store {key} 失败" 
    return stores


def _proc_files_backup_files(
        stores: dict[str, dict[str, Store]],
        backup_files: dict[Path, Path],
    ):
    """备份处理后的文件
    """
    for input_file, bak_file in backup_files.items():
        stores['bak']['store'].mv(input_file, stores['bak']['store'].get_path(bak_file))
        logger.info(f"文件 {input_file} 备份到 {bak_file}")


def _proc_file(
        stores: dict[str, dict[str, Store]],
        input_file: Path,
        tmp_path: Path,
        fn: callable,
    ) -> tuple[Path, Path, Path]:
    remote_file = stores['dl']['store'].get_path(input_file)
                    
    # 下载到本地
    input_file = stores['dl']['store'].download(remote_file, tmp_path / input_file.name)
    # 处理文件
    output_file = fn(input_file, tmp_path)
    
    # 上传到 ul_path
    stores['ul']['store'].upload(output_file, stores['ul']['store'].get_path(stores['ul']['config']['path']))

    # 备份到 bak_path   
    bak_file = Path(stores['bak']['config']['path']) / input_file.name

    return remote_file, output_file, bak_file

def proc_files(config: dict):
    """处理 文件的逻辑函数
    处理流程
    1. 从配置文件中获取 dl_path, ul_path, bak_path 三个路径
    2. 从 dl_path 中扫描所有符合 proc_types 中 filter 的文件
    3. 对每个文件调用对应的处理函数，处理后的文件放入 ul_path 中
    4. 若处理成功，将原文件移动到 bak_path 中
    """
    result: dict[str, str|dict] = { 'status': '', 'message': '', 'info': {}, }
    driver = config['driver']
    assert driver is not None, "未指定驱动"
    assert driver in _drivers, f"未找到驱动 {driver}"
    stores: dict[str, dict[str, Store]] = {}
    try:
        stores = _proc_files_init_store(config)

        result['status'] = 'scan_path'
        scan_path = stores['dl']['store'].get_path(stores['dl']['config']['path'])
        tmp_path: Path = Path('data/tmp/') / driver
        if not tmp_path.exists():
            tmp_path.mkdir(parents=True)

        result['status'] = 'proc_type'
        backup_files = {}
        for proc_info in config['proc_types']:
            proc_type = proc_info['type']
            fn_name = f"proc_{proc_type}_file"
            result['info'][proc_type] = {
                'filter': proc_info['filter'], 'driver': driver,
                'proc_type': proc_type, 'files': {}
            }
            
            fn = getattr(_drivers[driver], fn_name, None)
            if fn is None:
                logger.error(f"未找到处理函数 {fn_name}")
                result['info'][proc_type]['error'] = f"未找到处理函数 {fn_name}"
                continue
            
            procs_files = stores['dl']['store'].list(scan_path, proc_info['filter'])
            info_mesg = f"{driver} {proc_type} 发现 {len(procs_files)} 个文件需要处理"
            logger.info(f"{info_mesg}, 需要处理的文件列表: \n{procs_files}")
            result['info'][proc_type]['files'] = {
                'files': procs_files, 'success': {}, 'error': {},
            }

            for input_file in procs_files:
                try:
                    remote_file, output_file, bak_file = _proc_file(stores, input_file, tmp_path, fn)
                    logger.info(f"{driver} 文件 {input_file} 处理完成, 处理后的文件: {output_file}")
                    backup_files[str(remote_file)] = bak_file

                    result['info'][proc_type]['files']['success'][str(input_file)] = str(output_file)
                except Exception as e:
                    result['info'][proc_type]['files']['error'][str(input_file)] = '处理文件时出错: ' + str(e)

        # 备份所有文件
        result['status'] = 'backup_files'
        _proc_files_backup_files(stores, backup_files)
        
        if not any(result['info'][proc_type]['files']['error'] for proc_type in result['info']):
            result['status'] = 'success'
        else:
            result['status'] = 'partial_success'
    except Exception as e:
        logger.exception(f"处理文件 {driver} 时出错: {e}")
        result['status'] = f"{result['status']}_error"
        result['message'] = f"处理文件 {driver} 时出错: " + str(e)  
    finally:
        for store in stores.values():
            store['store'].close()
        return result


__all__ = [ 'proc_files', ]
