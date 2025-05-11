#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import os
import datetime
import codecs
import yaml
from logging.handlers import RotatingFileHandler
from .config import settings

# 创建日志目录
logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# 从fastagent.config.yaml读取日志配置
def load_fastagent_logging_config():
    """从fastagent.config.yaml加载日志配置"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'fastagent.config.yaml')
    
    if not os.path.exists(config_path):
        return settings.LOG_LEVEL, None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        if config and isinstance(config, dict) and 'logger' in config:
            logger_config = config['logger']
            log_level = logger_config.get('level', settings.LOG_LEVEL)
            return log_level.upper() if isinstance(log_level, str) else settings.LOG_LEVEL, logger_config
    except Exception as e:
        print(f"读取日志配置失败: {e}")
    
    return settings.LOG_LEVEL, None

# 加载日志配置
LOG_LEVEL, logger_config = load_fastagent_logging_config()

# 获取当前日期作为日志文件名的一部分
current_date = datetime.datetime.now().strftime('%Y-%m-%d')

# 设置日志格式 - 避免使用特殊Unicode字符
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 为应用程序设置更简洁的日志格式
app_log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 配置根日志
root_logger = logging.getLogger()
if not root_logger.handlers:
    root_handler = logging.StreamHandler(sys.stdout)
    root_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'  # 简化根日志格式
    ))
    root_logger.addHandler(root_handler)
    
    # 映射日志级别名称到实际级别
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR
    }
    # 设置根日志级别
    log_level = level_map.get(LOG_LEVEL, logging.INFO)
    root_logger.setLevel(log_level)
    
    # 记录当前使用的日志级别
    print(f"日志级别设置为: {LOG_LEVEL}")

# 禁用第三方库的过度日志
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("passlib").setLevel(logging.WARNING)  # 禁用passlib的调试输出
logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)  # 完全禁止bcrypt警告
logging.getLogger("watchfiles").setLevel(logging.WARNING)  # 禁用watchfiles的调试输出
logging.getLogger("uvicorn").setLevel(logging.INFO)  # 设置uvicorn为INFO级别
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)  # 禁用sqlalchemy详细日志
logging.getLogger("httpcore").setLevel(logging.ERROR)  # 禁用httpcore的所有调试和警告信息
logging.getLogger("openai").setLevel(logging.WARNING)  # 禁用openai客户端的调试日志
logging.getLogger("mcp").setLevel(logging.WARNING)  # 禁用mcp库的详细调试日志
logging.getLogger("mcp.client").setLevel(logging.WARNING)  # 禁用mcp客户端详细日志
logging.getLogger("httpcore.connection").setLevel(logging.ERROR)  # 禁用连接级别日志
logging.getLogger("httpcore.http11").setLevel(logging.ERROR)  # 禁用HTTP协议级别日志
logging.getLogger("openai._base_client").setLevel(logging.ERROR)  # 禁用OpenAI基础客户端日志

# 创建控制台处理器 - 使用stdout流以便更好地处理Unicode
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(app_log_format)  # 使用简化的格式

# 自定义的Windows兼容RotatingFileHandler
class WindowsCompatibleRotatingFileHandler(RotatingFileHandler):
    """Windows环境下兼容的日志文件处理器，处理编码问题"""
    
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=False):
        # 使用配置中的编码设置
        encoding = encoding or settings.LOG_ENCODING
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay)
    
    def emit(self, record):
        """重写emit方法，确保记录的消息在Windows下正确编码"""
        if isinstance(record.msg, str) and settings.LOG_CLEAN_SPECIAL_CHARS:
            record.msg = clean_text_for_logging(record.msg)
        try:
            super().emit(record)
        except (UnicodeError, UnicodeEncodeError, UnicodeDecodeError) as e:
            # 尝试处理Unicode错误
            self.handleError(record)

# 处理Windows编码问题的功能
def clean_text_for_logging(text):
    """移除可能在Windows下导致编码问题的特殊字符"""
    if not isinstance(text, str):
        return text
        
    # 替换常见的特殊Unicode字符
    replacements = {
        '✓': '[成功]',
        '✗': '[失败]',
        'ℹ': '[信息]',
        '→': '->',
        '⚠': '[警告]',
        '⚡': '[错误]',
        '\u2713': '[成功]',  # ✓
        '\u2717': '[失败]',  # ✗
        '\u24D8': '[信息]',  # ⓘ
        '\u2192': '->',      # →
        '\u26A0': '[警告]',  # ⚠
        '\u26A1': '[错误]',  # ⚡
        '\u2139': '[信息]',  # ℹ
        '\u2022': '*',       # •
        '\u2023': '>',       # ‣
        '\u25BA': '>',       # ►
        '\u21E8': '-->',     # ⇨
        '\u21D2': '=>',      # ⇒
        '…': '...',          # 省略号
        '\u2026': '...',     # …
    }
    
    for char, replacement in replacements.items():
        if char in text:
            text = text.replace(char, replacement)
    
    # 尝试处理一些不可打印字符
    return ''.join(c if c.isprintable() or c.isspace() else f"\\u{ord(c):04x}" for c in text)

# 添加过滤器来处理特殊字符
class TextCleanerFilter(logging.Filter):
    def filter(self, record):
        if settings.LOG_CLEAN_SPECIAL_CHARS:
            if isinstance(record.msg, str):
                record.msg = clean_text_for_logging(record.msg)
            if hasattr(record, 'args') and record.args:
                if isinstance(record.args, tuple):
                    clean_args = tuple(clean_text_for_logging(arg) if isinstance(arg, str) else arg for arg in record.args)
                    record.args = clean_args
        return True

# 创建应用日志记录器
app_logger = logging.getLogger("FastAgentApp")
app_logger.setLevel(logging.INFO)
app_logger.addHandler(console_handler)

# 创建API日志记录器
api_logger = logging.getLogger("FastAgentAPI")
api_logger.setLevel(logging.INFO)
api_logger.addHandler(console_handler)

# 创建测试日志记录器 - 仅记录关键信息
test_logger = logging.getLogger('FastAgentTest')
test_logger.setLevel(logging.INFO)
test_logger.addHandler(console_handler)

# 防止多处理器问题
app_logger.propagate = False
api_logger.propagate = False
test_logger.propagate = False

# 添加统一的日志方法
def log_request_info(request_method, endpoint, status_code, processing_time=None):
    """记录请求信息的统一格式"""
    time_info = f" - {processing_time:.2f}ms" if processing_time is not None else ""
    app_logger.info(f"{request_method} {endpoint} - {status_code}{time_info}")

def log_error(message, exc_info=False):
    """记录错误信息的统一格式"""
    app_logger.error(f"错误: {message}", exc_info=exc_info)

def log_startup_info(host, port):
    """记录启动信息的统一格式"""
    app_logger.info(f"服务器启动于 http://{host}:{port}")

def log_query_info(query_text, session_id=None, truncate_length=50):
    """记录查询信息的统一格式"""
    truncated_query = (query_text[:truncate_length] + "...") if len(query_text) > truncate_length else query_text
    session_info = f" [会话ID: {session_id}]" if session_id else ""
    app_logger.info(f"收到查询{session_info}: {truncated_query}")

def log_response_info(response_length, processing_time=None):
    """记录响应信息的统一格式"""
    time_info = f" (耗时: {processing_time:.2f}s)" if processing_time is not None else ""
    app_logger.info(f"发送响应: {response_length} 字节{time_info}")

# 创建文件处理器
def create_file_handler(log_type):
    """创建日志文件处理器，使用兼容Windows的编码"""
    file_path = os.path.join(logs_dir, f'{log_type}_{current_date}.log')
    
    # 确保日志目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # 使用自定义的Windows兼容处理器
    file_handler = WindowsCompatibleRotatingFileHandler(
        file_path,
        maxBytes=settings.LOG_MAX_SIZE,
        backupCount=settings.LOG_BACKUP_COUNT
    )
    file_handler.setFormatter(log_format)
    return file_handler

# 添加文件处理器
app_file_handler = create_file_handler('app')
app_logger.addHandler(app_file_handler)

api_file_handler = create_file_handler('api')
api_logger.addHandler(api_file_handler)

test_file_handler = create_file_handler('test')
test_logger.addHandler(test_file_handler)

# 应用过滤器
app_logger.addFilter(TextCleanerFilter())
api_logger.addFilter(TextCleanerFilter())
test_logger.addFilter(TextCleanerFilter())

def setup_logger(name, log_file, level=logging.INFO):
    """设置自定义日志记录器"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 添加控制台处理器
    logger.addHandler(console_handler)
    
    # 创建日志文件目录
    log_file_path = os.path.join(logs_dir, log_file)
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    
    # 添加文件处理器
    file_handler = WindowsCompatibleRotatingFileHandler(
        log_file_path,
        maxBytes=settings.LOG_MAX_SIZE,
        backupCount=settings.LOG_BACKUP_COUNT
    )
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    
    # 添加过滤器
    logger.addFilter(TextCleanerFilter())
    logger.propagate = False
    
    return logger 