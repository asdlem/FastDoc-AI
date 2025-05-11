from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import text

from app.db.session import get_db
from app.core.logging import app_logger

router = APIRouter()

@router.get("/health", status_code=200)
async def health_check(db: Session = Depends(get_db)):
    """
    健康检查端点，验证服务器和数据库连接状态
    """
    try:
        # 尝试执行一个简单的数据库查询，验证数据库连接
        db.execute(text("SELECT 1")).first()
        
        response = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "message": "FastAgent API服务正常运行",
            "database": "connected"
        }
        
        app_logger.info(f"健康检查 - 服务器状态: {response['status']}")
        return response
    except Exception as e:
        app_logger.error(f"健康检查失败 - 错误: {str(e)}")
        response = {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "message": f"服务器运行但数据库连接失败: {str(e)}",
            "database": "disconnected"
        }
        return response 