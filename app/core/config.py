#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import secrets
import yaml
from typing import List, Union, Optional
from pathlib import Path

from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 项目基本信息
    PROJECT_NAME: str = "FastAgent"
    PROJECT_DESCRIPTION: str = "现代化聊天助手API"
    PROJECT_VERSION: str = "0.1.0"
    
    # 应用程序设置
    AGENT_NAME: str = "FastAgent"
    DEFAULT_MODEL: str = "deepseek-chat"  # 默认模型
    DEFAULT_API: Optional[str] = None  # 默认API提供商
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8002
    DEBUG: bool = False  # 设置为False以减少日志输出
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///data/fastapi.db"
    
    # 安全配置
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    ALGORITHM: str = "HS256"
    
    # CORS配置
    CORS_ORIGINS: List[str] = ["*"]
    
    # 管理员账户
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: str = "logs/app.log"
    LOG_ENCODING: str = "utf-8-sig" if os.name == 'nt' else "utf-8"  # Windows下使用带BOM的UTF-8
    LOG_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5
    # 是否启用日志特殊字符清理
    LOG_CLEAN_SPECIAL_CHARS: bool = True if os.name == 'nt' else False
    
    # API密钥和敏感配置
    DEEPSEEK_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    
    # MCP服务器配置
    MCP_SERVER_CONFIGS: dict = {}
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# 创建settings实例
settings = Settings()

# 从fastagent.config.yaml加载配置
def load_fastagent_config():
    """从fastagent.config.yaml加载FastAgent配置"""
    config_path = Path("fastagent.config.yaml")
    
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                
                # 读取默认模型
                if "default_model" in config:
                    settings.DEFAULT_MODEL = config["default_model"]
                    print(f"从配置文件加载默认模型: {settings.DEFAULT_MODEL}")
                
                # 存储MCP服务器配置
                if "mcp" in config and "servers" in config["mcp"]:
                    settings.MCP_SERVER_CONFIGS = config["mcp"]["servers"]
                    print(f"已加载MCP服务器基础配置")
                
                # 可以在此处添加其他需要的配置项
                
        except Exception as e:
            print(f"加载 {config_path} 时出错: {str(e)}")
    else:
        print(f"配置文件 {config_path} 不存在，使用默认配置")

# 从fastagent.secrets.yaml加载敏感配置
def load_fastagent_secrets():
    """从fastagent.secrets.yaml加载敏感配置"""
    secrets_path = Path("fastagent.secrets.yaml")
    
    if secrets_path.exists():
        try:
            with open(secrets_path, "r", encoding="utf-8") as f:
                secrets_config = yaml.safe_load(f)
                
                # 加载API密钥
                if "deepseek" in secrets_config and "api_key" in secrets_config["deepseek"]:
                    settings.DEEPSEEK_API_KEY = secrets_config["deepseek"]["api_key"]
                    print("已加载DeepSeek API密钥")
                
                if "openai" in secrets_config and "api_key" in secrets_config["openai"]:
                    settings.OPENAI_API_KEY = secrets_config["openai"]["api_key"]
                    print("已加载OpenAI API密钥")
                
                if "anthropic" in secrets_config and "api_key" in secrets_config["anthropic"]:
                    settings.ANTHROPIC_API_KEY = secrets_config["anthropic"]["api_key"]
                    print("已加载Anthropic API密钥")
                
                if "openrouter" in secrets_config and "api_key" in secrets_config["openrouter"]:
                    settings.OPENROUTER_API_KEY = secrets_config["openrouter"]["api_key"]
                    print("已加载OpenRouter API密钥")
                
                # 加载MCP服务器的敏感配置
                if "mcp" in secrets_config and "servers" in secrets_config["mcp"]:
                    for server_name, server_config in secrets_config["mcp"]["servers"].items():
                        if server_name in settings.MCP_SERVER_CONFIGS:
                            # 合并敏感配置到MCP服务器配置中
                            if "env" in server_config:
                                settings.MCP_SERVER_CONFIGS[server_name]["env"] = server_config["env"]
                            
                            # 如果secrets中也定义了url，使用secrets中的url（优先级更高）
                            if "url" in server_config:
                                settings.MCP_SERVER_CONFIGS[server_name]["url"] = server_config["url"]
                                print(f"已从secrets加载MCP服务器 {server_name} 的URL配置")
                    
                    print("已加载MCP服务器敏感配置")
                
        except Exception as e:
            print(f"加载 {secrets_path} 时出错: {str(e)}")
    else:
        print(f"敏感配置文件 {secrets_path} 不存在，使用环境变量或默认配置")

# 加载FastAgent配置
load_fastagent_config()
# 加载敏感配置
load_fastagent_secrets()

# 设置默认值
if settings.DEFAULT_MODEL is None:
    settings.DEFAULT_MODEL = "deepseek-chat"
    
if settings.DEFAULT_API is None:
    settings.DEFAULT_API = "deepseek" 