import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.logging import app_logger
from app.core.config import settings

# 创建数据库目录
database_path = 'data'
os.makedirs(database_path, exist_ok=True)

# 数据库URL
DATABASE_URL = f"sqlite:///data/fastapi.db"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 导入Base以便在其他地方使用
from app.models.user import Base

# 获取数据库会话
def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 初始化数据库
def init_db():
    """初始化数据库表结构并创建初始数据"""
    from app.db.base_class import Base
    
    # 导入所有模型以确保它们被Base注册
    from app.models.user import User
    from app.models.chat import ChatSession, ChatMessage
    
    app_logger.info("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    app_logger.info("数据库表创建完成") 