from loguru import logger
from .config import logger as _config


def init_logger():
    logger.add(
        sink=_config().get('log_file', 'log.log'),
        rotation=_config().get('rotation', '10 MB'),
        encoding=_config().get('encoding', 'utf-8'),
        level=str(_config().get('level', 'INFO')).upper(),
        backtrace=_config().get('backtrace', False),
    )

