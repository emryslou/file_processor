import click
from pathlib import Path

from file_processor.utils.config import load_config
from file_processor.utils.logger import logger, init_logger
from file_processor.processors import proc_files
from file_processor.stores import destroy_stores

@click.group()
@click.pass_context
def client(ctx):
    if ctx.invoked_subcommand is None:
        ctx.invoke(cli)

@client.command("run", help="运行文件处理任务")
@click.option("--config", "-c", required=True, help="配置文件路径", type=click.Path(exists=True))
def cli(config: str|Path):
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


@client.command("package-info")
def package_info():
    import file_processor.utils.package as _package
    print(_package.desc())
    print(_package.version_update())
    print(_package.package_structure())

if __name__ == "__main__":
    client()
