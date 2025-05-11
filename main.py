#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import uvicorn
import socket
import contextlib
import sys
import os
import signal

# 确保正确的控制台编码
if sys.platform.startswith('win'):
    # Windows平台设置控制台编码
    os.environ["PYTHONIOENCODING"] = "utf-8"
    # 尝试设置控制台代码页为UTF-8 (65001)
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)
        kernel32.SetConsoleCP(65001)
    except Exception:
        pass

from fastapi import FastAPI, APIRouter, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.core.logging import app_logger, log_startup_info, log_request_info, log_error
from app.core.config import settings
from app.api.routes import user_router, chat_routes, health, query_router
from app.core.database import init_db
from app.services.user_service import create_initial_admin
from app.core.database import SessionLocal
from app.services.mcp_service import retry_verify_mcp_servers
from app.utils.port_checker import check_port_availability
from app.services.agent_service import get_agent_instance, close_agent_instance

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    log_request_info(request.method, request.url.path, response.status_code, process_time)
    return response

# 使用新的lifespan上下文管理器替代过时的on_event
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # 注册信号处理器以支持正常关闭
    original_sigint_handler = signal.getsignal(signal.SIGINT)
    original_sigterm_handler = signal.getsignal(signal.SIGTERM)
    
    shutdown_event = asyncio.Event()
    
    def handle_shutdown_signal(signum, frame):
        app_logger.info(f"收到信号 {signum}，准备关闭...")
        shutdown_event.set()
        # 保留原始处理器
        if signum == signal.SIGINT and original_sigint_handler:
            if callable(original_sigint_handler):
                original_sigint_handler(signum, frame)
        elif signum == signal.SIGTERM and original_sigterm_handler:
            if callable(original_sigterm_handler):
                original_sigterm_handler(signum, frame)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, handle_shutdown_signal)
    signal.signal(signal.SIGTERM, handle_shutdown_signal)
    
    # 启动事件
    log_startup_info(settings.HOST, settings.PORT)
    app_logger.info("服务器启动中...")
    app_logger.info("初始化数据库...")
    
    # 初始化数据库
    init_db()
    
    # 创建初始管理员用户
    app_logger.info("检查并创建初始管理员账户...")
    db = SessionLocal()
    admin_user = create_initial_admin(db)
    if admin_user:
        app_logger.info(f"已创建初始管理员账户: {admin_user.username}")
    
    # 记录MCP服务器使用SSE连接方式
    app_logger.info("使用SSE方式连接MCP服务器...")
    try:
        await retry_verify_mcp_servers()
        app_logger.info("MCP服务器已配置为使用SSE连接方式")
        
        # 预初始化FastAgent实例
        app_logger.info("预初始化FastAgent实例...")
        await get_agent_instance()
        app_logger.info("FastAgent实例初始化完成，服务器已就绪")
    except Exception as e:
        app_logger.error(f"初始化FastAgent实例时出错: {str(e)}")
        app_logger.warning("继续启动服务器，但Agent功能可能不可用")
    
    yield
    
    # 关闭事件
    app_logger.info("服务器关闭中...")
    
    # 关闭FastAgent实例
    app_logger.info("关闭FastAgent实例...")
    # 使用超时保护，确保关闭操作不会阻塞太久
    try:
        # 创建一个带超时的任务来关闭FastAgent实例
        close_task = asyncio.create_task(close_agent_instance())
        await asyncio.wait_for(close_task, timeout=10.0)
        app_logger.info("FastAgent实例关闭成功")
    except asyncio.TimeoutError:
        app_logger.warning("关闭FastAgent实例超时，强制关闭")
    except Exception as e:
        app_logger.error(f"关闭FastAgent实例时出错: {str(e)}")
    
    # 恢复原始信号处理器
    signal.signal(signal.SIGINT, original_sigint_handler)
    signal.signal(signal.SIGTERM, original_sigterm_handler)
    
    app_logger.info("服务器已完全关闭")

# 设置应用的lifespan
app.router.lifespan_context = lifespan

# 创建主路由
api_router = APIRouter(prefix="/api")

# 注册用户和聊天路由
api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(chat_routes, prefix="/sessions", tags=["chat"])

# 注册健康检查路由（不带/api前缀）
app.include_router(health, tags=["health"])

# 注册查询路由（不带/api前缀）
app.include_router(query_router, tags=["query"])

# 注册API路由（带/api前缀）
app.include_router(api_router)

# 根路由重定向
@app.get("/", include_in_schema=False)
async def root():
    if settings.DEBUG:
        return {"message": "欢迎使用FastAgent API服务", "docs": "/docs"}
    return {"message": "欢迎使用FastAgent API服务"}

# 自定义异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    app_logger.warning(f"HTTP异常: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    log_error(f"未处理的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误，请稍后重试"}
    )

# 启动服务器
if __name__ == "__main__":
    # 检查端口是否可用，如果不可用则直接退出
    check_port_availability(settings.PORT, exit_on_conflict=True)
    
    try:
        uvicorn.run(
            "main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level="info",
            access_log=False  # 关闭访问日志
        )
    except Exception as e:
        log_error(f"启动服务器时出错: {str(e)}", exc_info=True) 