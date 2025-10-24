from re import T
import click
import sys
import time
from pathlib import Path


from file_processor.notification import send_notification, gen_notification_body_html, gen_notification_body_text
from file_processor.utils.config import load_config, logger as logger_config
from file_processor.utils.logger import logger, init_logger, get_trace_id
from file_processor.utils.tools import human_readable_time
from file_processor.processors import proc_files

@click.command("file-processor")
@click.option("--config", "-c", required=True, help="配置文件路径", type=click.Path(exists=True))
def cli(config: str|Path):
    _start_time = time.time()
    
    config = load_config(config)
    init_logger()

    app_cfg = config['app']
    
    processors = app_cfg.get('processors', [])
    notify_types = app_cfg.get('notification', [])

    result_info = {
        'processor': {
            processor['driver']: {}
            for processor in processors
        },
        'config': config,
    }

    
    for processor in processors:
        result_info['processor'][processor['driver']] = proc_files(processor)
    

    result_info['runtime'] = {
        'elapsed_time': time.time() - _start_time,
        'elapsed_time_human_readable': human_readable_time(time.time() - _start_time),
        'trace_id': get_trace_id(),
    }
    

    if notify_types:
        for notify_type in notify_types:
            try:
                send_notification(notify_type['type'], gen_notification_body_html(result_info))
            except Exception as e:
                logger.error(f"发送通知 {notify_type['type']} 失败: {e}")
    
    if logger_config().get('console_output', True):
        logger.info("\n" + gen_notification_body_text(result_info))
    else:
        print(gen_notification_body_text(result_info))

if __name__ == "__main__":
    cli()
