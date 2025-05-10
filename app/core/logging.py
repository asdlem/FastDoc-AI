import sys
import logging
from .config import settings

# 配置根日志
root_logger = logging.getLogger()
if not root_logger.handlers:
    root_handler = logging.StreamHandler(sys.stdout)
    root_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    root_logger.addHandler(root_handler)
    root_logger.setLevel(logging.INFO if not settings.DEBUG else logging.DEBUG)

# 禁用第三方库的过度日志
logging.getLogger("asyncio").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# 创建应用日志记录器
app_logger = logging.getLogger("FastAgentApp")
if not app_logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    app_logger.addHandler(handler)
    app_logger.setLevel(logging.INFO if not settings.DEBUG else logging.DEBUG)

# 创建API日志记录器
api_logger = logging.getLogger("FastAgentAPI")
if not api_logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    api_logger.addHandler(handler)
    api_logger.setLevel(logging.INFO if not settings.DEBUG else logging.DEBUG) 