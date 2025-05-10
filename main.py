import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging import app_logger
from app.core.config import settings
from app.api.endpoints import router
from app.services.mcp_service import retry_verify_mcp_servers

# 创建FastAPI应用
app = FastAPI(title=settings.API_TITLE)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加API路由
app.include_router(router)

# 服务器启动事件
@app.on_event("startup")
async def startup_event():
    """服务器启动时进行初始化和健康检查"""
    app_logger.info("服务器启动中...")
    
    # 测试MCP服务器连接
    app_logger.info("测试MCP服务器连接...")
    is_ready = await retry_verify_mcp_servers()
    
    if is_ready:
        app_logger.info("MCP服务器连接测试成功，服务器已就绪")
    else:
        app_logger.warning("MCP服务器连接测试部分失败，但将继续尝试运行")

if __name__ == '__main__':
    # 使用Uvicorn服务器运行FastAPI应用
    app_logger.info(f"启动Uvicorn服务器，监听http://{settings.API_HOST}:{settings.API_PORT}")
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT) 