import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用配置类，使用pydantic进行环境变量管理"""
    
    # API服务器配置
    API_TITLE: str = "FastAgent技术问答API"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # FastAgent配置
    AGENT_NAME: str = "技术开发助手"
    DEFAULT_MODEL: str = "deepseek-chat"
    
    # 环境设置
    DEBUG: bool = False
    
    # MCP服务器配置
    MCP_FETCH_URL: Optional[str] = None
    MCP_CONTEXT7_COMMAND: str = "npx"
    MCP_CONTEXT7_ARGS: list = ["-y", "@upstash/context7-mcp@latest"]
    
    # API密钥配置
    DEEPSEEK_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# 创建全局配置实例
settings = Settings()

# 如果fastagent.config.yaml中有配置，使用它来覆盖环境变量
def load_fastagent_config():
    """从fastagent.config.yaml加载配置到settings"""
    # FastAgent会自动读取fastagent.config.yaml，此处无需额外加载
    pass 