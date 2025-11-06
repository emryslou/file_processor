import argparse 
import sys
from pathlib import Path
from tkinter import NO

from file_processor.utils.config import load_config
from file_processor.utils.logger import logger, init_logger
from file_processor.processors import proc_files
from file_processor.stores import destroy_stores

def path_check(path: str|Path):
    path = Path(path)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"路径不存在: {path}")
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"不是文件: {path}")
    
    return path

def parse_args(_call_from: str|None = None):
    if len(sys.argv) >= 2: # 至少有一个参数，第一个参数为命令或选项
        first_args = sys.argv[1]
        if first_args.startswith('-') and first_args not in ['-h', '--help']: # 设置默认命令
            sys.argv.insert(1, 'run')
    if len(sys.argv) == 1: # 没有参数，默认运行run命令
        sys.argv.append('--help')
    
    parser = argparse.ArgumentParser(prog='python -m file_processor', description="文件处理")
    _subparsers = parser.add_subparsers(dest="command", help="支持如下命令")
    _run_parser = _subparsers.add_parser("run", help="运行文件处理任务")
    _run_parser.add_argument( "-c", "--config", required=True, help="配置文件路径", type=path_check)
    
    _package_info_parser = _subparsers.add_parser("package-info", help="获取包信息")
    _package_info_parser.add_argument("-l", "--log", action="store_true", help="显示更新日志")
    _package_info_parser.add_argument("-s", "--struct", action="store_true", help="显示包结构")

    return parser.parse_args()


def cmd_run(config: str|Path):
    config = load_config(config)
    init_logger()

    app_cfg = config['app']
    
    processors = app_cfg['processors']
    notify_types = app_cfg.get('notification', [])
    result_info = {
        'processor': {
            processor['driver']: {}
            for processor in processors
        },
        'config': config,
    }
    try:
        for processor in processors:
            result_info['processor'][processor['driver']] = proc_files(processor)
    finally:
        logger.info("回收所有存储资源")
        destroy_stores()
    
    if notify_types:
        from file_processor.notification import send_notification, gen_notification_body_html
        for notify_type in notify_types:
            send_notification(notify_type['type'], gen_notification_body_html(result_info))
    
    else:
        from file_processor.notification import gen_notification_body_text
        logger.info("\n" + gen_notification_body_text(result_info))


def cmd_package_info(log: bool = False, struct: bool = False):
    from .utils import package_info as _package
    from . import __version__, __author__, __author_email__
    print(f"版本: {__version__}")
    print(f"作者: {__author__}")
    print(f"作者邮箱: {__author_email__}")
    print(f"打包时间: {_package.package_time()}")
    if log:
        print("更新日志:")
        print('\n'.join(_package.version_update(__version__)))
    if struct:
        print("包结构:")
        print('\n'.join(_package.package_structure()))


def cli(call_from: str|None = None):
    args = parse_args(call_from)
    kawrgs = vars(args)
    
    cmds_list = {
        'run': cmd_run,
        'package-info': cmd_package_info,
    }
    cmd = args.command if args.command in cmds_list else '_'
    kawrgs.pop('command')
    cmds_list[cmd](**kawrgs)


if __name__ == "__main__":
    cli('cli.py.__main__')
