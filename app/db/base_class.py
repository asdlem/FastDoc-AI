from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func

# 创建基类
Base = declarative_base()

# 定义一个混合类，为所有模型添加通用列
class TimestampMixin:
    """为模型添加创建时间和更新时间"""
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 