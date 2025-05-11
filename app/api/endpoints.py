import time
import asyncio
from fastapi import APIRouter, HTTPException, Response, Depends, Query, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.logging import api_logger
from app.services.agent_service import tech_assistant_query
from app.utils.text_utils import extract_urls, extract_marked_content, clean_query
from app.api.dependencies import get_current_active_user, get_db
from app.models.user import User
from app.services import chat_service
from app.api.schemas import MessageCreate, ChatSessionCreate

# 创建API路由器
router = APIRouter()

# 请求模型
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[int] = None

class QueryResponse(BaseModel):
    answer: str
    session_id: int

# 健康检查端点
@router.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok", "timestamp": time.time()}

# 保存消息到数据库
async def save_message(db: Session, session_id: int, user_id: int, role: str, content: str):
    """后台任务：保存消息到数据库"""
    message_data = MessageCreate(role=role, content=content)
    chat_service.add_message(db, session_id, user_id, message_data)

# 查询端点
@router.post("/query", response_model=QueryResponse)
async def query_endpoint(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """API端点，接收POST请求并返回AI响应"""
    query = request.query
    session_id = request.session_id
    api_logger.info(f"收到查询: {query}，用户: {current_user.username}, 会话ID: {session_id}")

    # 处理会话
    if session_id is None:
        # 创建新会话
        new_session = chat_service.create_session(
            db, current_user.id, 
            ChatSessionCreate(title=query[:50] + ("..." if len(query) > 50 else ""))
        )
        session_id = new_session.id
        api_logger.info(f"为用户 {current_user.username} 创建新会话: {session_id}")
    else:
        # 验证会话存在且属于当前用户
        existing_session = chat_service.get_session(db, session_id, current_user.id)
        if not existing_session:
            raise HTTPException(status_code=404, detail="会话不存在或无权访问")

    # 保存用户消息
    background_tasks.add_task(
        save_message, db, session_id, current_user.id, "user", query
    )

    urls = extract_urls(query)
    api_logger.info(f"提取的URL: {urls}")
    
    # 构造提示词
    if urls:
        # 移除查询中的 @URL 部分
        cleaned_query = query
        for url_pattern in [r'@(https?://\S+)', r'(https?://[^\s\'"\)]+)']:
            cleaned_query = clean_query(query, url_pattern)

        prompt = f"""请严格按照以下要求，为用户提供纯净的Markdown格式技术解答：
用户原始问题: "{cleaned_query}"
参考URL（你需要在后台处理这些URL）: {', '.join(urls)}

你的任务是：
1. 理解问题和分析URL内容。
2. 结合context7-mcp工具查找相关文档。
3. **核心：整合信息，生成最终答案。请将最终的、纯净的Markdown答案严格包裹在 `$$$ANSWER_START$$$` 和 `$$$ANSWER_END$$$` 标记之间。这两个标记之外不要有任何其他内容是给用户的。**
"""
    else:
        prompt = f"""请严格按照以下要求，为用户提供纯净的Markdown格式技术解答：
用户原始问题: "{query}"

你的任务是：
1. 理解问题。
2. 结合context7-mcp工具查找相关文档。
3. (可选，后台进行) 使用fetch补充搜索。
4. **核心：整合信息，生成最终答案。请将最终的、纯净的Markdown答案严格包裹在 `$$$ANSWER_START$$$` 和 `$$$ANSWER_END$$$` 标记之间。这两个标记之外不要有任何其他内容是给用户的。**
"""
    api_logger.info(f"构造的提示词: {prompt}")

    try:
        # 设置重试逻辑
        max_retries = 2
        retry_delay = 3  # 秒
        
        result_raw = None
        for attempt in range(max_retries):
            try:
                # 调用agent服务
                result_raw = await tech_assistant_query(prompt)
                api_logger.info(f"Agent响应(原始，前500字符): {result_raw[:500]}...") 
                break  # 如果成功，跳出循环
            except Exception as e:
                if attempt < max_retries - 1:
                    api_logger.warning(f"处理请求失败 (尝试 {attempt+1}/{max_retries}): {e}，等待{retry_delay}秒后重试...")
                    await asyncio.sleep(retry_delay)
                else:
                    raise  # 最后一次尝试失败时抛出异常
        
        # 提取最终答案
        final_answer_content = extract_marked_content(result_raw)
        
        # 保存助手响应
        background_tasks.add_task(
            save_message, db, session_id, current_user.id, "assistant", final_answer_content
        )
        
        # 返回响应和会话ID
        return QueryResponse(answer=final_answer_content, session_id=session_id)
        
    except Exception as e:
        api_logger.error(f"处理请求失败: {e}")
        raise HTTPException(status_code=500, detail=f"处理请求失败: {str(e)}")
        
# 获取会话历史消息
@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取指定会话的历史消息"""
    # 检查会话是否存在且属于当前用户
    session = chat_service.get_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在或无权访问")
    
    # 获取消息
    messages = chat_service.get_messages(db, session_id, current_user.id, skip, limit)
    return messages 