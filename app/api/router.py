from fastapi import APIRouter
from app.api.endpoints import router as endpoints_router
from app.api.routes.user_routes import router as user_router
from app.api.routes.chat_routes import router as chat_router

# 创建主路由器
router = APIRouter(prefix="/api")

# 注册子路由器
router.include_router(endpoints_router)
router.include_router(user_router)
router.include_router(chat_router) 