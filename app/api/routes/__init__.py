# API路由模块初始化
"""
提供API路由定义
"""
from app.api.routes.user_routes import router as user_router
from app.api.routes.chat_routes import router as chat_routes
from app.api.routes.health import router as health
from app.api.routes.query import router as query_router 