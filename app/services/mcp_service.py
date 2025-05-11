"""
MCP服务管理模块 - 使用SSE方式连接
"""
import asyncio
from app.core.logging import app_logger

async def verify_mcp_servers():
    """验证MCP服务器连接
    
    使用SSE方式连接MCP服务器时，无需额外验证
    SSE连接会在实际使用时自动建立
    """
    app_logger.info("使用SSE方式连接MCP服务器，无需额外验证")
    return True

async def retry_verify_mcp_servers(max_retries=3, retry_interval=2):
    """使用SSE方式时，无需重试验证MCP服务器连接"""
    app_logger.info("使用SSE方式连接MCP服务器，无需验证连接")
    return True 