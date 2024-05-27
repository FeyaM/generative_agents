import logging

# 定义不同日志级别的ANSI颜色代码
RESET = '\033[0m'
BRIGHT_BLACK = '\033[30;1m'
BRIGHT_GREEN = '\033[32;1m'
BRIGHT_YELLOW = '\033[33;1m'
BRIGHT_RED = '\033[31;1m'
BRIGHT_MAGENTA = '\033[35;1m'

class ColoredFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)

    def format(self, record):
        # 根据日志级别添加相应的颜色代码
        levelname = record.levelname
        if levelname == 'DEBUG':
            record.levelname = f'{BRIGHT_BLACK}{levelname}{RESET}'
        elif levelname == 'INFO':
            record.levelname = f'{BRIGHT_GREEN}{levelname}{RESET}'
        elif levelname == 'WARNING':
            record.levelname = f'{BRIGHT_YELLOW}{levelname}{RESET}'
        elif levelname == 'ERROR':
            record.levelname = f'{BRIGHT_RED}{levelname}{RESET}'
        elif levelname == 'CRITICAL':
            record.levelname = f'{BRIGHT_MAGENTA}{levelname}{RESET}'
        return super().format(record)

class LogUtils:
    @staticmethod
    def setup_logging():
        # 创建一个带有颜色的格式化器
        formatter = ColoredFormatter('[%(asctime)s] [%(levelname)s] [%(threadName)s] [%(name)s.%(funcName)s] - %(message)s')
        
        # 创建一个日志处理器，并将其添加到根日志记录器
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        
        # 获取根日志记录器并配置它
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

# 使用LogUtils类设置日志
LogUtils.setup_logging()

# 使用配置好的日志记录器
logging.info('This is an info message.')
logging.warning('This is a warning message.')
logging.error('This is an error message.')
