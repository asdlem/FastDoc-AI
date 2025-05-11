from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class ChatSession(Base):
    """聊天会话模型"""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, default="新会话")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    
    # 关联关系
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    user = relationship("User", back_populates="chat_sessions")
    
    def __repr__(self):
        return f"<ChatSession(id={self.id}, title='{self.title}', user_id={self.user_id})>"


class ChatMessage(Base):
    """聊天消息模型"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    
    # 关联关系
    session = relationship("ChatSession", back_populates="messages")
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role='{self.role}', session_id={self.session_id})>" 