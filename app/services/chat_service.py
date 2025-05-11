from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models.chat import ChatSession, ChatMessage
from app.api.schemas import ChatSessionCreate, ChatSessionUpdate, MessageCreate
from app.core.logging import app_logger

def create_session(db: Session, user_id: int, session_data: ChatSessionCreate) -> ChatSession:
    """创建新的聊天会话"""
    db_session = ChatSession(
        title=session_data.title,
        user_id=user_id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    app_logger.info(f"用户 {user_id} 创建了新会话: {db_session.id}")
    return db_session

def get_session(db: Session, session_id: int, user_id: int) -> Optional[ChatSession]:
    """获取指定的聊天会话"""
    return db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user_id
    ).first()

def get_sessions(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """获取用户的所有聊天会话，并包含消息数量"""
    results = db.query(
        ChatSession,
        func.count(ChatMessage.id).label('message_count')
    ).outerjoin(
        ChatMessage, ChatSession.id == ChatMessage.session_id
    ).filter(
        ChatSession.user_id == user_id
    ).group_by(
        ChatSession.id
    ).order_by(
        desc(ChatSession.updated_at)
    ).offset(skip).limit(limit).all()
    
    # 转换结果为字典列表，确保日期时间字段有效
    sessions = []
    for session, message_count in results:
        # 确保日期时间字段不为空
        created_at = session.created_at if session.created_at else datetime.now()
        updated_at = session.updated_at if session.updated_at else datetime.now()
        
        session_dict = {
            "id": session.id,
            "title": session.title,
            "user_id": session.user_id,
            "is_active": session.is_active,
            "created_at": created_at,
            "updated_at": updated_at,
            "message_count": message_count
        }
        sessions.append(session_dict)
    
    return sessions

def update_session(db: Session, session_id: int, user_id: int, session_data: ChatSessionUpdate) -> Optional[ChatSession]:
    """更新聊天会话"""
    db_session = get_session(db, session_id, user_id)
    if not db_session:
        return None
    
    # 更新会话属性
    for key, value in session_data.dict(exclude_unset=True).items():
        setattr(db_session, key, value)
    
    # 更新时间
    db_session.updated_at = datetime.now()
    
    db.commit()
    db.refresh(db_session)
    app_logger.info(f"用户 {user_id} 更新了会话 {session_id}")
    return db_session

def delete_session(db: Session, session_id: int, user_id: int) -> bool:
    """删除聊天会话"""
    db_session = get_session(db, session_id, user_id)
    if not db_session:
        return False
    
    db.delete(db_session)
    db.commit()
    app_logger.info(f"用户 {user_id} 删除了会话 {session_id}")
    return True

def add_message(db: Session, session_id: int, user_id: int, message_data: MessageCreate) -> Optional[ChatMessage]:
    """添加聊天消息"""
    # 验证会话存在且属于该用户
    db_session = get_session(db, session_id, user_id)
    if not db_session:
        return None
    
    # 创建消息
    db_message = ChatMessage(
        session_id=session_id,
        role=message_data.role,
        content=message_data.content,
        created_at=datetime.now()
    )
    
    # 更新会话的更新时间
    db_session.updated_at = datetime.now()
    
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_messages(db: Session, session_id: int, user_id: int, skip: int = 0, limit: int = 50) -> List[ChatMessage]:
    """获取会话的所有消息"""
    # 验证会话存在且属于该用户
    db_session = get_session(db, session_id, user_id)
    if not db_session:
        return []
    
    # 查询消息并按创建时间排序
    return db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(
        ChatMessage.created_at
    ).offset(skip).limit(limit).all()

def get_message(db: Session, message_id: int, session_id: int, user_id: int) -> Optional[ChatMessage]:
    """获取特定消息，并验证消息所属的会话是否属于当前用户"""
    # 验证会话存在且属于该用户
    db_session = get_session(db, session_id, user_id)
    if not db_session:
        return None
    
    # 查询特定消息
    return db.query(ChatMessage).filter(
        ChatMessage.id == message_id,
        ChatMessage.session_id == session_id
    ).first()

def delete_message(db: Session, message_id: int, session_id: int, user_id: int) -> bool:
    """删除特定消息，并验证消息所属的会话是否属于当前用户"""
    # 获取消息，并验证权限
    db_message = get_message(db, message_id, session_id, user_id)
    if not db_message:
        return False
    
    # 删除消息
    db.delete(db_message)
    
    # 更新会话的更新时间
    db_session = get_session(db, session_id, user_id)
    db_session.updated_at = datetime.now()
    
    # 提交更改
    db.commit()
    app_logger.info(f"用户 {user_id} 删除了会话 {session_id} 中的消息 {message_id}")
    return True

def batch_delete_messages(db: Session, message_ids: List[int], session_id: int, user_id: int) -> int:
    """批量删除消息，并验证消息所属的会话是否属于当前用户
    
    返回：成功删除的消息数量
    """
    # 验证会话存在且属于该用户
    db_session = get_session(db, session_id, user_id)
    if not db_session:
        return 0
    
    # 查询符合条件的消息，确保消息属于指定会话
    messages_to_delete = db.query(ChatMessage).filter(
        ChatMessage.id.in_(message_ids),
        ChatMessage.session_id == session_id
    ).all()
    
    # 如果没有找到任何符合条件的消息，则返回0
    if not messages_to_delete:
        return 0
    
    # 删除消息
    delete_count = 0
    for message in messages_to_delete:
        db.delete(message)
        delete_count += 1
    
    # 更新会话的更新时间
    db_session.updated_at = datetime.now()
    
    # 提交更改
    db.commit()
    app_logger.info(f"用户 {user_id} 批量删除了会话 {session_id} 中的 {delete_count} 条消息")
    return delete_count

def clear_session_messages(db: Session, session_id: int, user_id: int) -> int:
    """清空会话中的所有消息，但保留会话本身
    
    返回：删除的消息数量
    """
    # 验证会话存在且属于该用户
    db_session = get_session(db, session_id, user_id)
    if not db_session:
        return 0
    
    # 查询会话中的所有消息
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).all()
    
    # 删除所有消息
    delete_count = 0
    for message in messages:
        db.delete(message)
        delete_count += 1
    
    # 更新会话的更新时间
    db_session.updated_at = datetime.now()
    
    # 提交更改
    db.commit()
    app_logger.info(f"用户 {user_id} 清空了会话 {session_id} 中的所有消息，共 {delete_count} 条")
    return delete_count 