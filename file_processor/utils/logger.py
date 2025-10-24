import sys
from loguru import logger
from .config import logger as _config


# 全局trace_id变量
_current_trace_id = ""



def set_trace_id(trace_id: str) -> None:
    """
    设置当前的trace_id
    
    :param trace_id: 要设置的trace_id
    """
    global _current_trace_id
    _current_trace_id = trace_id

def set_default_trace_id() -> None:
    import uuid
    global _current_trace_id
    if not _current_trace_id:
        _current_trace_id = str(uuid.uuid4())


def get_trace_id() -> str:
    """
    获取当前的trace_id
    
    :return: 当前的trace_id
    """
    return _current_trace_id


# 自定义格式化器，在日志中包含trace_id
def _custom_formatter(record):
    set_default_trace_id()
    record["extra"]["trace_id"] = _current_trace_id
    return "[{time:YYYY-MM-DD HH:mm:ss.SSS}][{extra[trace_id]}]|{level: <8}|{module}:{function}|{file}:{line} - {message}"

def _console_formatter(record):
    set_default_trace_id()
    record["extra"]["trace_id"] = _current_trace_id
    # 将格式化字符串拆分为多行以提高可读性
    format_str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>"  # 时间
        "|<magenta>{extra[trace_id]}</magenta>"  # 跟踪ID
        "|<level>{level:<8}</level>"  # 日志级别
        "|<cyan>{module}</cyan>.<cyan>{function}</cyan>"
        "|<cyan>{file}</cyan>:{line}"  # 模块、函数和行号
        " - <level>{message}</level>\n"  # 消息内容
    )
    return format_str


def init_logger():
    logger.remove()

    logger.add(
        sink=_config().get('log_file', 'log.log'),
        rotation=_config().get('rotation', '10 MB'),
        encoding=_config().get('encoding', 'utf-8'),
        level=str(_config().get('level', 'INFO')).upper(),
        backtrace=_config().get('backtrace', False),
        format=_custom_formatter,
    )

    if _config().get('console_output', True):
        logger.add(
            sink=sys.stdout,
            format=_console_formatter,
            level=str(_config().get('console_level', 'INFO')).upper(),
        )

