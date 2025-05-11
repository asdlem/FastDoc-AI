from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import time

from app.api.schemas import (
    ChatSessionCreate, ChatSessionUpdate, ChatSession, ChatSessionList,
    MessageCreate, Message, User
)
from app.api.dependencies import get_current_user, get_db
from app.services import chat_service
from app.services.agent_service import tech_assistant_query
from app.core.logging import app_logger, log_query_info, log_response_info, log_error, log_request_info
from pydantic import BaseModel

router = APIRouter(tags=["chat"])

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[int] = None

class QueryResponse(BaseModel):
    answer: str
    session_id: int

class MessageIdsRequest(BaseModel):
    message_ids: List[int]

@router.post("/", response_model=ChatSession, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    session: ChatSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新的聊天会话"""
    db_session = chat_service.create_session(db, current_user.id, session)
    
    # 创建可序列化的响应对象
    session_dict = {
        "id": db_session.id,
        "title": db_session.title,
        "user_id": db_session.user_id,
        "is_active": db_session.is_active,
        "created_at": db_session.created_at,
        "updated_at": db_session.updated_at,
        "messages": []
    }
    
    return session_dict

@router.get("/", response_model=List[ChatSessionList])
async def get_chat_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的所有聊天会话"""
    sessions = chat_service.get_sessions(db, current_user.id, skip, limit)
    return sessions

@router.get("/{session_id}", response_model=ChatSession)
async def get_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取指定的聊天会话"""
    session = chat_service.get_session(db, session_id, current_user.id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在或无权访问"
        )
    
    # 获取会话的消息
    messages = chat_service.get_messages(db, session_id, current_user.id)
    
    # 创建可序列化的响应对象
    session_dict = {
        "id": session.id,
        "title": session.title,
        "user_id": session.user_id,
        "is_active": session.is_active,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "session_id": msg.session_id,
                "created_at": msg.created_at
            } for msg in messages
        ]
    }
    
    return session_dict

@router.put("/{session_id}", response_model=ChatSession)
async def update_chat_session(
    session_id: int,
    session_update: ChatSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新聊天会话"""
    updated_session = chat_service.update_session(
        db, session_id, current_user.id, session_update
    )
    if updated_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在或无权访问"
        )
    
    # 获取会话的消息
    messages = chat_service.get_messages(db, session_id, current_user.id)
    
    # 创建可序列化的响应对象
    session_dict = {
        "id": updated_session.id,
        "title": updated_session.title,
        "user_id": updated_session.user_id,
        "is_active": updated_session.is_active,
        "created_at": updated_session.created_at,
        "updated_at": updated_session.updated_at,
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "session_id": msg.session_id,
                "created_at": msg.created_at
            } for msg in messages
        ]
    }
    
    return session_dict

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除聊天会话"""
    success = chat_service.delete_session(db, session_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在或无权访问"
        )
    return {"status": "success"}

@router.post("/{session_id}/messages", response_model=Message)
async def add_chat_message(
    session_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """添加聊天消息"""
    db_message = chat_service.add_message(db, session_id, current_user.id, message)
    if db_message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在或无权访问"
        )
    
    # 创建可序列化的响应对象
    message_dict = {
        "id": db_message.id,
        "role": db_message.role,
        "content": db_message.content,
        "session_id": db_message.session_id,
        "created_at": db_message.created_at
    }
    
    return message_dict

@router.get("/{session_id}/messages", response_model=List[Message])
async def get_chat_messages(
    session_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取会话的所有消息"""
    # 检查会话是否存在且属于当前用户
    session = chat_service.get_session(db, session_id, current_user.id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在或无权访问"
        )
    
    # 获取消息
    raw_messages = chat_service.get_messages(db, session_id, current_user.id, skip, limit)
    
    # 创建可序列化的响应对象
    messages = [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "session_id": msg.session_id,
            "created_at": msg.created_at
        } for msg in raw_messages
    ]
    
    return messages

@router.post("/query", response_model=QueryResponse)
async def process_query(
    query_request: QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """处理用户查询并返回结果，可选择关联到指定会话"""
    start_time = time.time()
    log_query_info(query_request.query)
    
    try:
        # 检查会话ID是否有效
        session_id = query_request.session_id
        if session_id:
            session = chat_service.get_session(db, session_id, current_user.id)
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="会话不存在或无权访问"
                )
            app_logger.info(f"使用现有会话: {session_id}")
        else:
            # 创建新会话
            session_data = ChatSessionCreate(title=f"查询: {query_request.query[:30]}...")
            session = chat_service.create_session(db, current_user.id, session_data)
            session_id = session.id
            app_logger.info(f"创建新会话: {session_id}")
        
        # 添加用户消息
        user_message = MessageCreate(role="user", content=query_request.query)
        chat_service.add_message(db, session_id, current_user.id, user_message)
        
        # 调用AI处理查询
        app_logger.info(f"处理查询 [会话ID: {session_id}]")
        try:
            response_start = time.time()
            response = await tech_assistant_query(query_request.query)
            response_time = time.time() - response_start
            response_length = len(response) if response else 0
            log_response_info(response_length, response_time)
        except Exception as e:
            log_error(f"AI处理查询失败: {str(e)}", exc_info=True)
            # 返回友好的错误消息
            response = "$$$ANSWER_START$$$\n## 处理查询时出错\n\n很抱歉，在处理您的查询时遇到技术问题。请稍后再试。\n$$$ANSWER_END$$$"
        
        # 提取答案
        answer = extract_answer(response)
        
        # 添加助手消息
        assistant_message = MessageCreate(role="assistant", content=answer)
        chat_service.add_message(db, session_id, current_user.id, assistant_message)
        
        processing_time = time.time() - start_time
        log_request_info("POST", f"/api/sessions/query", 200, processing_time * 1000)
        return {"answer": answer, "session_id": session_id}
    except Exception as e:
        if isinstance(e, HTTPException):
            log_request_info("POST", f"/api/sessions/query", e.status_code)
            raise e
        
        log_error(f"处理查询失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理查询失败: {str(e)}"
        )

@router.get("/history/{session_id}", response_model=List[Message])
async def get_chat_history(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取会话的所有历史消息"""
    # 检查会话是否存在且属于当前用户
    session = chat_service.get_session(db, session_id, current_user.id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在或无权访问"
        )
    
    # 获取所有消息
    raw_messages = chat_service.get_messages(db, session_id, current_user.id)
    
    # 创建可序列化的响应对象
    messages = [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "session_id": msg.session_id,
            "created_at": msg.created_at
        } for msg in raw_messages
    ]
    
    return messages

@router.delete("/{session_id}/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_message(
    session_id: int,
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除聊天消息"""
    success = chat_service.delete_message(db, message_id, session_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在或无权访问"
        )
    return {"status": "success"}

@router.delete("/{session_id}/messages", status_code=status.HTTP_200_OK)
async def batch_delete_chat_messages(
    session_id: int,
    request: MessageIdsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """批量删除聊天消息"""
    # 检查会话是否存在且属于当前用户
    session = chat_service.get_session(db, session_id, current_user.id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在或无权访问"
        )
    
    # 批量删除消息
    delete_count = chat_service.batch_delete_messages(
        db, request.message_ids, session_id, current_user.id
    )
    
    return {"status": "success", "deleted_count": delete_count}

@router.delete("/{session_id}/clear", status_code=status.HTTP_200_OK)
async def clear_chat_session_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """清空会话中的所有消息，但保留会话本身"""
    # 检查会话是否存在且属于当前用户
    session = chat_service.get_session(db, session_id, current_user.id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在或无权访问"
        )
    
    # 清空会话消息
    delete_count = chat_service.clear_session_messages(
        db, session_id, current_user.id
    )
    
    return {"status": "success", "deleted_count": delete_count}

def extract_answer(response: str) -> str:
    """从FastAgent响应中提取最终答案"""
    if not response:
        app_logger.warning("收到空响应")
        return "无法获取回答，请稍后重试"
        
    # 查找回答的开始和结束标记
    start_marker = "$$$ANSWER_START$$$"
    end_marker = "$$$ANSWER_END$$$"
    
    start_index = response.find(start_marker)
    end_index = response.find(end_marker)
    
    if start_index != -1 and end_index != -1 and start_index < end_index:
        # 提取标记之间的内容
        answer = response[start_index + len(start_marker):end_index].strip()
        app_logger.info(f"成功提取回答，长度: {len(answer)}")
        return answer
    
    # 如果没有找到标记，记录详细内容以便调试
    app_logger.warning(f"未找到回答标记，返回完整响应。响应长度: {len(response)}")
    app_logger.debug(f"响应内容前100字符: {response[:100]}")
    app_logger.debug(f"响应内容后100字符: {response[-100:] if len(response) > 100 else response}")
    
    # 尝试查找部分标记
    if start_index != -1:
        app_logger.warning(f"找到开始标记，但未找到结束标记")
    elif end_index != -1:
        app_logger.warning(f"找到结束标记，但未找到开始标记")
    
    return response 